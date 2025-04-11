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

app = Flask(__name__)

# 全局变量
detector = None
detection_results = {}
is_detecting = False

def init_detector():
    """初始化检测器"""
    global detector
    model_path = os.path.join('models', 'cnn3_best_weights.h5')
    # 第二个参数控制是否使用BlazeFace (True则启用)
    detector = EmotionDetector(model_path, use_blaze=True)

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
    global is_detecting
    
    is_detecting = False
    session_id = request.json.get('session_id')
    
    if session_id in detection_results:
        detection_results[session_id]['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 保存结果到文件
        results_dir = os.path.join('static', 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        file_path = os.path.join(results_dir, f"{session_id}.json")
        with open(file_path, 'w') as f:
            json.dump(detection_results[session_id], f, indent=2)
        
        return jsonify({
            'status': 'success',
            'message': '检测已停止',
            'results': detection_results[session_id],
            'file_path': f"/static/results/{session_id}.json"
        })
    else:
        return jsonify({
            'status': 'error',
            'message': '无效的会话ID'
        }), 400

@app.route('/api/detect', methods=['POST'])
def detect():
    """处理单帧检测"""
    global detector, detection_results
    
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