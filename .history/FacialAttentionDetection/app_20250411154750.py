from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
import dlib
import base64
import time
import os
from utils.detector import AttentionDetector
from utils.record import DistractionRecorder

app = Flask(__name__)

# 初始化检测器
detector = None
recorder = DistractionRecorder()

try:
    model_path = os.path.join('models', 'shape_predictor_68_face_landmarks.dat')
    detector = AttentionDetector(model_path)
    print("成功加载面部检测模型")
except Exception as e:
    print(f"加载模型失败: {e}")

@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    """处理从前端发送的视频帧"""
    if detector is None:
        return jsonify({'error': '模型未加载'}), 500
    
    # 从请求中获取图像数据
    data = request.json
    if not data or 'image' not in data:
        return jsonify({'error': '未收到图像数据'}), 400
    
    # 解码base64图像
    try:
        encoded_data = data['image'].split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception as e:
        return jsonify({'error': f'图像解码失败: {e}'}), 400
    
    # 处理图像
    result = detector.process_image(img)
    
    # 更新记录器状态
    if result['is_distracted'] and not detector.is_currently_distracted:
        detector.is_currently_distracted = True
        recorder.start_distraction_event()
    elif not result['is_distracted'] and detector.is_currently_distracted:
        detector.is_currently_distracted = False
        recorder.end_distraction_event()
    
    # 获取统计信息
    total_time, event_count = recorder.get_statistics()
    
    # 添加统计信息到结果
    result.update({
        'distraction_count': event_count,
        'distraction_time': round(total_time, 1),
        'distraction_percentage': round((total_time / detector.elapsed_time * 100), 1) if detector.elapsed_time > 0 else 0
    })
    
    return jsonify(result)

@app.route('/reset_stats', methods=['POST'])
def reset_stats():
    """重置统计数据"""
    global recorder
    recorder = DistractionRecorder()
    detector.reset()
    return jsonify({'status': 'success'})

@app.route('/save_record', methods=['POST'])
def save_record():
    """保存记录到文件"""
    from datetime import datetime
    filename = f"distraction_record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    if recorder.save_to_file(filename):
        return jsonify({'status': 'success', 'filename': filename})
    else:
        return jsonify({'error': '保存记录失败'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
