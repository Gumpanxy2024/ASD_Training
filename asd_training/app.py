from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
import base64
import json
import time
import logging
from datetime import datetime
import os
from utils.emotion_detector import EmotionDetector
from utils.detector import AttentionDetector
from utils.record import DistractionRecorder
from utils.emotion_record import EmotionRecorder

# 添加JSON序列化帮助函数
def convert_numpy_types(obj):
    """将NumPy类型转换为Python标准类型，用于JSON序列化"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return [convert_numpy_types(item) for item in obj]
    return obj

# 自定义JSON编码器
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super(NumpyEncoder, self).default(obj)

# 创建日志目录
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 配置日志
log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('asd_training')

app = Flask(__name__)
# 配置Flask使用自定义JSON编码器
app.json.encoder = NumpyEncoder

# 全局变量
emotion_detector = None
attention_detector = None
distraction_recorder = DistractionRecorder()
emotion_recorder = EmotionRecorder()
detection_results = {}
is_detecting = False
training_records = []  # 记录训练题目情况

def init_detectors():
    """初始化检测器"""
    global emotion_detector, attention_detector
    
    # 获取项目根目录的绝对路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    logger.info("开始初始化检测器")
    
    # 初始化情绪检测器
    emotion_model_path = os.path.join(base_dir, 'models', 'emotion', 'cnn3_best_weights.h5')
    logger.info(f"加载情绪模型从: {os.path.abspath(emotion_model_path)}")
    try:
        emotion_detector = EmotionDetector(emotion_model_path, use_blaze=True)
        logger.info("情绪检测器加载成功")
    except Exception as e:
        logger.error(f"加载情绪检测器失败: {e}")
    
    # 初始化注意力检测器
    attention_model_path = os.path.join(base_dir, 'models', 'attention', 'shape_predictor_68_face_landmarks.dat')
    logger.info(f"加载注意力模型从: {os.path.abspath(attention_model_path)}")
    try:
        attention_detector = AttentionDetector(attention_model_path)
        logger.info("注意力检测器加载成功")
    except Exception as e:
        logger.error(f"加载注意力检测器失败: {e}")
    
    logger.info("检测器初始化完成")

@app.route('/')
def index():
    """主页，直接重定向到训练欢迎页面"""
    return render_template('training_main.html')

@app.route('/training')
def training():
    """传统训练页面（旧版）"""
    return render_template('training.html')

@app.route('/training/main')
def training_main():
    """新版表情训练主页面"""
    return render_template('training_main.html')

@app.route('/emotion')
def emotion():
    """情绪检测页面"""
    return render_template('emotion.html')

@app.route('/attention')
def attention():
    """注意力检测页面"""
    return render_template('attention.html')

@app.route('/api/integrated_detect', methods=['POST'])
def integrated_detect():
    """集成检测API - 同时处理情绪和注意力检测"""
    if emotion_detector is None or attention_detector is None:
        logger.error("检测模型未加载完成")
        return jsonify({'error': '检测模型未加载完成'}), 500
    
    try:
        # 获取图像数据
        data = request.json
        if not data or 'image' not in data:
            logger.warning("未收到图像数据")
            return jsonify({'error': '未收到图像数据'}), 400
        
        logger.info("接收到集成检测请求")
        
        # 解码图像
        encoded_data = data['image'].split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 情绪检测
        try:
            emotion_results = emotion_detector.detect_emotion(img)
            logger.info(f"情绪检测结果: {len(emotion_results)}个人脸")
            
            # 记录情绪结果
            emotion_recorder.record_emotions(emotion_results)
        except Exception as e:
            logger.error(f"情绪检测失败: {e}")
            emotion_results = []
        
        # 注意力检测
        try:
            attention_result = attention_detector.process_image(img)
            is_distracted = attention_result.get('is_distracted', False)
            logger.info(f"注意力检测结果: {'分心' if is_distracted else '专注'}")
            
            # 更新注意力记录器状态
            if attention_result['is_distracted'] and not attention_detector.is_currently_distracted:
                attention_detector.is_currently_distracted = True
                distraction_recorder.start_distraction_event()
                logger.info("开始分心事件记录")
            elif not attention_result['is_distracted'] and attention_detector.is_currently_distracted:
                attention_detector.is_currently_distracted = False
                distraction_recorder.end_distraction_event()
                logger.info("结束分心事件记录")
            elif attention_result['is_distracted'] and attention_detector.is_currently_distracted:
                if distraction_recorder.check_reminder_needed():
                    attention_result['show_reminder'] = True
                    logger.info("触发分心提醒")
                attention_result['current_distraction_time'] = round(distraction_recorder.get_current_distraction_time(), 1)
        except Exception as e:
            logger.error(f"注意力检测失败: {e}")
            attention_result = {'is_distracted': False, 'face_detected': False}
        
        # 获取注意力统计信息
        total_time, event_count = distraction_recorder.get_statistics()
        
        # 添加注意力统计信息到结果
        attention_result.update({
            'distraction_count': event_count,
            'distraction_time': round(total_time, 1),
            'distraction_percentage': round((total_time / attention_detector.elapsed_time * 100), 1) if attention_detector.elapsed_time > 0 else 0
        })
        
        # 确保所有NumPy类型转换为Python标准类型
        processed_emotion_results = []
        for result in emotion_results:
            processed_result = {}
            for key, value in result.items():
                processed_result[key] = convert_numpy_types(value)
            processed_emotion_results.append(processed_result)
            
        processed_attention_result = {}
        for key, value in attention_result.items():
            processed_attention_result[key] = convert_numpy_types(value)
        
        # 整合结果
        integrated_result = {
            'status': 'success',
            'timestamp': time.time(),
            'emotion_results': processed_emotion_results,
            'attention_result': processed_attention_result
        }
        
        logger.info("集成检测完成")
        
        # 使用自定义编码器序列化JSON
        try:
            json_data = json.dumps(integrated_result, cls=NumpyEncoder)
            return Response(json_data, mimetype='application/json')
        except TypeError as e:
            # 如果还有序列化错误，进行深度转换
            logger.warning(f"使用自定义编码器序列化失败: {e}，尝试进行深度转换")
            deep_converted = convert_numpy_types(integrated_result)
            return Response(json.dumps(deep_converted), mimetype='application/json')
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        logger.error(f"集成检测异常: {error_msg}")
        error_response = {
            'status': 'error',
            'message': str(e)
        }
        return Response(json.dumps(error_response), mimetype='application/json', status=500)

@app.route('/api/reset', methods=['POST'])
def reset_stats():
    """重置所有统计数据"""
    global distraction_recorder, emotion_recorder, training_records
    
    logger.info("重置所有统计数据")
    
    # 保存重置前的数据备份
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 创建主备份目录
    backup_dir = os.path.join('static', 'records', 'backups')
    attention_backup_dir = os.path.join(backup_dir, 'attention')
    emotion_backup_dir = os.path.join(backup_dir, 'emotion')
    training_backup_dir = os.path.join(backup_dir, 'training')
    
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(attention_backup_dir, exist_ok=True)
    os.makedirs(emotion_backup_dir, exist_ok=True)
    os.makedirs(training_backup_dir, exist_ok=True)
    
    # 重置前备份
    if distraction_recorder.distraction_events:
        backup_file = os.path.join(attention_backup_dir, f"distraction_backup_{timestamp}.csv")
        distraction_recorder.save_to_file(backup_file)
        logger.info(f"注意力数据备份至: {backup_file}")
    
    if emotion_recorder.emotion_records:
        backup_file = os.path.join(emotion_backup_dir, f"emotion_backup_{timestamp}.csv")
        emotion_recorder.save_to_file(backup_file)
        logger.info(f"情绪数据备份至: {backup_file}")
    
    if training_records:
        backup_file = os.path.join(training_backup_dir, f"training_backup_{timestamp}.json")
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(training_records, f, ensure_ascii=False, indent=2)
        logger.info(f"训练数据备份至: {backup_file}")
    
    # 重置记录器
    distraction_recorder = DistractionRecorder()
    emotion_recorder = EmotionRecorder()
    training_records = []
    
    if attention_detector:
        attention_detector.reset()
    
    logger.info("所有统计数据已重置")
    return jsonify({'status': 'success'})

@app.route('/api/record_training', methods=['POST'])
def record_training():
    """记录训练题目情况"""
    try:
        data = request.json
        if not data:
            logger.warning("未收到训练数据")
            return jsonify({'error': '未收到训练数据'}), 400
        
        # 记录训练结果
        question_id = data.get('question_id')
        is_correct = data.get('is_correct')
        question_type = data.get('question_type', '未知')
        answer = data.get('answer', '')
        correct_answer = data.get('correct_answer', '')
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'question_id': question_id,
            'question_type': question_type,
            'is_correct': is_correct,
            'answer': answer,
            'correct_answer': correct_answer
        }
        
        training_records.append(record)
        
        logger.info(f"训练题目记录 - ID: {question_id}, 类型: {question_type}, 正确: {is_correct}")
        
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"记录训练题目异常: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_records', methods=['POST'])
def save_records():
    """保存所有记录数据"""
    # 接收前端传来的训练数据（如有）
    training_data = request.json or {}
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 创建主记录目录
    records_dir = os.path.join('static', 'records')
    os.makedirs(records_dir, exist_ok=True)
    
    # 创建分类子目录
    attention_dir = os.path.join(records_dir, 'attention')
    emotion_dir = os.path.join(records_dir, 'emotion')
    training_dir = os.path.join(records_dir, 'training')
    summary_dir = os.path.join(records_dir, 'summary')
    
    os.makedirs(attention_dir, exist_ok=True)
    os.makedirs(emotion_dir, exist_ok=True)
    os.makedirs(training_dir, exist_ok=True)
    os.makedirs(summary_dir, exist_ok=True)
    
    logger.info(f"创建记录目录结构: {records_dir}")
    
    # 保存注意力记录
    attention_filename = os.path.join(attention_dir, f"distraction_record_{timestamp}.csv")
    attention_saved = distraction_recorder.save_to_file(attention_filename)
    if attention_saved:
        logger.info(f"注意力记录已保存: {attention_filename}")
    
    # 保存情绪记录
    emotion_filename = os.path.join(emotion_dir, f"emotion_record_{timestamp}.csv")
    emotion_saved = emotion_recorder.save_to_file(emotion_filename)
    if emotion_saved:
        logger.info(f"情绪记录已保存: {emotion_filename}")
    
    # 保存训练题目记录
    training_log_filename = os.path.join(training_dir, f"training_log_{timestamp}.json")
    if training_records:
        with open(training_log_filename, 'w', encoding='utf-8') as f:
            json.dump(training_records, f, ensure_ascii=False, indent=2)
        logger.info(f"训练题目记录已保存: {training_log_filename}")
        training_log_saved = True
    else:
        training_log_saved = False
    
    # 获取统计数据
    emotion_stats = emotion_recorder.get_statistics()
    attention_stats = {
        'total_distractions': len(distraction_recorder.distraction_events),
        'total_time': sum(event.duration for event in distraction_recorder.distraction_events if event.duration is not None),
    }
    
    # 整合前端传来的数据
    summary_data = {
        'timestamp': timestamp,
        'emotion_stats': emotion_stats,
        'attention_stats': attention_stats
    }
    
    # 计算题目正确率
    if training_records:
        correct_count = sum(1 for record in training_records if record.get('is_correct'))
        total_count = len(training_records)
        accuracy = correct_count / total_count if total_count > 0 else 0
        summary_data['training_stats'] = {
            'total_questions': total_count,
            'correct_count': correct_count,
            'accuracy': round(accuracy * 100, 2)
        }
        logger.info(f"训练统计: 总题数 {total_count}, 正确数 {correct_count}, 正确率 {round(accuracy * 100, 2)}%")
    
    # 如果前端传递了训练数据，添加到摘要中
    if training_data:
        summary_data['training_data'] = training_data
    
    # 保存统计摘要
    summary_filename = os.path.join(summary_dir, f"training_summary_{timestamp}.json")
    with open(summary_filename, 'w') as f:
        json.dump(summary_data, f, indent=2)
    logger.info(f"训练摘要已保存: {summary_filename}")
    
    # 构建返回给前端的URL路径
    attention_url = f"/static/records/attention/distraction_record_{timestamp}.csv" if attention_saved else None
    emotion_url = f"/static/records/emotion/emotion_record_{timestamp}.csv" if emotion_saved else None
    training_log_url = f"/static/records/training/training_log_{timestamp}.json" if training_log_saved else None
    summary_url = f"/static/records/summary/training_summary_{timestamp}.json"
    
    return jsonify({
        'status': 'success' if (attention_saved or emotion_saved or training_log_saved or training_data) else 'no_data',
        'attention_record': attention_url,
        'emotion_record': emotion_url,
        'training_log': training_log_url,
        'summary': summary_url
    })

@app.route('/api/emotion/detect', methods=['POST'])
def detect_emotion():
    """处理情绪检测请求"""
    if emotion_detector is None:
        return jsonify({'error': '情绪检测模型未加载'}), 500
    
    try:
        # 获取图像数据
        data = request.json
        image_b64 = data['image']
        
        # 解码图像
        image_data = base64.b64decode(image_b64.split(',')[1])
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 调用检测器
        results = emotion_detector.detect_emotion(image)
        
        return jsonify({
            'status': 'success',
            'timestamp': time.time(),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/attention/detect', methods=['POST'])
def detect_attention():
    """处理注意力检测请求"""
    if attention_detector is None:
        return jsonify({'error': '注意力检测模型未加载'}), 500
    
    try:
        # 获取图像数据
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': '未收到图像数据'}), 400
        
        # 解码图像
        encoded_data = data['image'].split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 处理图像
        result = attention_detector.process_image(img)
        
        # 更新记录器状态
        if result['is_distracted'] and not attention_detector.is_currently_distracted:
            attention_detector.is_currently_distracted = True
            distraction_recorder.start_distraction_event()
        elif not result['is_distracted'] and attention_detector.is_currently_distracted:
            attention_detector.is_currently_distracted = False
            distraction_recorder.end_distraction_event()
        elif result['is_distracted'] and attention_detector.is_currently_distracted:
            if distraction_recorder.check_reminder_needed():
                result['show_reminder'] = True
            result['current_distraction_time'] = round(distraction_recorder.get_current_distraction_time(), 1)
        
        # 获取统计信息
        total_time, event_count = distraction_recorder.get_statistics()
        
        # 添加统计信息到结果
        result.update({
            'distraction_count': event_count,
            'distraction_time': round(total_time, 1),
            'distraction_percentage': round((total_time / attention_detector.elapsed_time * 100), 1) if attention_detector.elapsed_time > 0 else 0
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/attention/reset', methods=['POST'])
def reset_attention_stats():
    """重置注意力检测统计数据"""
    global distraction_recorder
    distraction_recorder = DistractionRecorder()
    attention_detector.reset()
    return jsonify({'status': 'success'})

@app.route('/api/attention/save', methods=['POST'])
def save_attention_record():
    """保存注意力检测记录"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 创建目录
    attention_dir = os.path.join('static', 'records', 'attention')
    os.makedirs(attention_dir, exist_ok=True)
    
    filename = os.path.join(attention_dir, f"distraction_record_{timestamp}.csv")
    
    if distraction_recorder.save_to_file(filename):
        logger.info(f"注意力记录单独保存至: {filename}")
        return jsonify({
            'status': 'success', 
            'filename': f"/static/records/attention/distraction_record_{timestamp}.csv"
        })
    else:
        logger.error("保存注意力记录失败")
        return jsonify({'error': '保存记录失败'}), 500

@app.errorhandler(500)
def handle_500_error(e):
    """处理500错误，记录日志"""
    logger.error(f"服务器错误: {str(e)}")
    return jsonify({
        'status': 'error',
        'message': '服务器内部错误，请检查日志获取详细信息'
    }), 500

# 自定义JSON处理错误处理器
def safe_jsonify(data):
    """安全的JSON序列化，确保处理NumPy类型"""
    try:
        # 尝试使用自定义编码器进行JSON序列化
        json_data = json.dumps(data, cls=NumpyEncoder)
        return Response(json_data, mimetype='application/json')
    except TypeError as e:
        logger.error(f"JSON序列化错误: {e}")
        logger.info("尝试深度转换数据类型...")
        
        # 进行深度转换
        converted_data = convert_numpy_types(data)
        try:
            return Response(json.dumps(converted_data), mimetype='application/json')
        except Exception as e2:
            logger.error(f"深度转换后仍然无法序列化: {e2}")
            return Response(json.dumps({
                'status': 'error',
                'message': '数据序列化失败'
            }), mimetype='application/json', status=500)

if __name__ == '__main__':
    try:
        init_detectors()
        logger.info("===============================================")
        logger.info("应用程序启动 - ASD训练系统")
        logger.info(f"运行环境: {os.environ.get('FLASK_ENV', 'development')}")
        logger.info(f"日志文件: {log_file}")
        logger.info("===============================================")
        
        # 使用不同端口，例如5001
        app.run(debug=True, host='0.0.0.0', port=8000)
    except Exception as e:
        logger.error(f"应用程序异常退出: {e}")
    finally:
        logger.info("===============================================")
        logger.info("应用程序关闭")
        logger.info("===============================================") 