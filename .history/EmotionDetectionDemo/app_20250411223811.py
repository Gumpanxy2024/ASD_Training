# emotion_detection/app.py
from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
import base64
import json
import time
from datetime import datetime
import os
from utils.emotion_detector import EmotionDetector
from utils.model import CNN3
import csv
from collections import defaultdict

app = Flask(__name__)

# 全局变量
detector = None
detection_results = {}
is_detecting = False
emotion_records = defaultdict(list)  # 用于跟踪每张脸的情绪变化
current_emotions = defaultdict(dict)  # 跟踪每个会话中每个人脸的当前情绪状态

def init_detector():
    """初始化检测器"""
    global detector
    model_path = os.path.join('models', 'cnn3_best_weights.h5')
    # 第二个参数控制是否使用BlazeFace (True则启用)
    detector = EmotionDetector(model_path, use_blaze=True)

def save_emotion_records_to_csv(session_id):
    """将情绪记录保存为CSV文件"""
    csv_dir = os.path.join('static', 'csv_results')
    os.makedirs(csv_dir, exist_ok=True)
    
    csv_path = os.path.join(csv_dir, f"{session_id}.csv")
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['face_id', 'emotion', 'start_time', 'end_time', 'duration_seconds', 'confidence']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # 写入所有记录
        for record in emotion_records[session_id]:
            writer.writerow(record)
    
    return csv_path

def update_emotion_records(session_id, current_faces, formatted_time, timestamp):
    """更新情绪记录"""
    global current_emotions, emotion_records
    
    # 获取当前会话的情绪状态
    session_emotions = current_emotions[session_id]
    
    # 对于每个当前检测到的人脸
    for face_id, face_result in current_faces.items():
        emotion = face_result['emotion']
        confidence = face_result['confidence']
        
        # 如果是新的人脸或情绪改变了
        if face_id not in session_emotions or session_emotions[face_id]['emotion'] != emotion:
            # 如果已经有记录，先关闭上一条记录
            if face_id in session_emotions:
                prev_record = session_emotions[face_id]['record']
                prev_record['end_time'] = formatted_time
                duration = timestamp - session_emotions[face_id]['start_timestamp']
                prev_record['duration_seconds'] = round(duration, 2)
            
            # 创建新记录
            new_record = {
                'face_id': face_id,
                'emotion': emotion,
                'start_time': formatted_time,
                'end_time': None,  # 暂时为空，会在情绪变化或会话结束时填写
                'duration_seconds': 0,
                'confidence': confidence
            }
            
            # 保存到记录列表
            emotion_records[session_id].append(new_record)
            
            # 更新当前状态
            session_emotions[face_id] = {
                'emotion': emotion,
                'start_timestamp': timestamp,
                'record': new_record
            }
        # 如果是相同情绪，更新置信度
        else:
            session_emotions[face_id]['record']['confidence'] = confidence
    
    # 检查是否有消失的人脸，结束它们的记录
    disappeared_faces = set(session_emotions.keys()) - set(current_faces.keys())
    for face_id in disappeared_faces:
        if face_id in session_emotions:
            record = session_emotions[face_id]['record']
            if record['end_time'] is None:  # 确保没有已经结束
                record['end_time'] = formatted_time
                duration = timestamp - session_emotions[face_id]['start_timestamp']
                record['duration_seconds'] = round(duration, 2)
                # 从当前会话状态中移除
                del session_emotions[face_id]

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/start_detection', methods=['POST'])
def start_detection():
    """开始检测"""
    global is_detecting, detection_results
    
    session_id = f"session_{int(time.time())}"
    detection_results[session_id] = {
        'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'results': []
    }
    
    is_detecting = True
    
    return jsonify({
        'status': 'success',
        'session_id': session_id,
        'message': '检测已开始'
    })

@app.route('/api/stop_detection', methods=['POST'])
def stop_detection():
    """停止检测"""
    global is_detecting, current_emotions
    
    is_detecting = False
    session_id = request.json.get('session_id')
    
    if session_id in detection_results:
        # 获取结束时间
        end_time = datetime.now()
        formatted_end_time = end_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        timestamp = time.time()
        
        # 结束所有未结束的情绪记录
        if session_id in current_emotions:
            for face_id, data in current_emotions[session_id].items():
                record = data['record']
                if record['end_time'] is None:
                    record['end_time'] = formatted_end_time
                    duration = timestamp - data['start_timestamp']
                    record['duration_seconds'] = round(duration, 2)
        
        # 保存CSV记录
        csv_path = save_emotion_records_to_csv(session_id)
        
        # 更新会话结束时间
        detection_results[session_id]['end_time'] = formatted_end_time
        detection_results[session_id]['csv_path'] = f"/static/csv_results/{session_id}.csv"
        
        # 保存JSON结果到文件
        results_dir = os.path.join('static', 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        file_path = os.path.join(results_dir, f"{session_id}.json")
        with open(file_path, 'w') as f:
            json.dump(detection_results[session_id], f, indent=2)
        
        return jsonify({
            'status': 'success',
            'message': '检测已停止',
            'results': detection_results[session_id],
            'file_path': f"/static/results/{session_id}.json",
            'csv_path': f"/static/csv_results/{session_id}.csv"
        })
    else:
        return jsonify({
            'status': 'error',
            'message': '无效的会话ID'
        }), 400

@app.route('/api/detect', methods=['POST'])
def detect():
    """处理单帧检测"""
    global detector, detection_results, emotion_records
    
    if not is_detecting:
        return jsonify({
            'status': 'error',
            'message': '检测尚未开始'
        }), 400
    
    try:
        # 获取图像数据和会话ID
        data = request.json
        image_b64 = data['image']
        session_id = data['session_id']
        
        # 解码图像
        image_data = base64.b64decode(image_b64.split(',')[1])
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 调用检测器
        results = detector.detect_emotion(image)
        
        # 记录结果
        timestamp = time.time()
        formatted_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # 跟踪情绪变化
        current_faces = {}
        for i, face_result in enumerate(results):
            face_id = f"face_{i}"
            current_faces[face_id] = face_result
        
        # 更新情绪记录
        update_emotion_records(session_id, current_faces, formatted_time, timestamp)
        
        frame_result = {
            'timestamp': timestamp,
            'time': formatted_time,
            'faces': results
        }
        
        if session_id in detection_results:
            detection_results[session_id]['results'].append(frame_result)
        
        return jsonify({
            'status': 'success',
            'timestamp': timestamp,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500



@app.route('/results/<session_id>')
def show_results(session_id):
    """显示检测结果"""
    results_file = os.path.join('static', 'results', f"{session_id}.json")
    
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        return render_template('result.html', session_id=session_id, results=results)
    else:
        return "结果不存在", 404
    

if __name__ == '__main__':
    init_detector()
    app.run(debug=True)