import time
import csv
from datetime import datetime

class EmotionEvent:
    """表示一次情绪事件的类"""
    
    def __init__(self, timestamp, emotion, confidence, face_id=None):
        """初始化情绪事件"""
        self.timestamp = timestamp
        self.emotion = emotion
        self.confidence = confidence
        self.face_id = face_id or "face_1"  # 如果未提供face_id，默认为face_1
    
    def to_dict(self):
        """将事件转换为字典格式"""
        return {
            'timestamp': datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'emotion': self.emotion,
            'confidence': round(self.confidence, 4),
            'face_id': self.face_id
        }

class EmotionRecorder:
    """情绪事件记录器"""
    
    def __init__(self):
        """初始化情绪记录器"""
        self.emotion_events = []
        self.start_time = time.time()
        
    def record_emotion(self, emotion, confidence, face_id=None):
        """记录一个情绪事件"""
        event = EmotionEvent(time.time(), emotion, confidence, face_id)
        self.emotion_events.append(event)
        return event
    
    def record_emotions(self, emotion_results):
        """记录多个情绪检测结果"""
        for i, result in enumerate(emotion_results):
            face_id = f"face_{i+1}"
            self.record_emotion(result['emotion'], result['confidence'], face_id)
    
    def get_statistics(self):
        """获取情绪统计数据"""
        if not self.emotion_events:
            return {}
        
        # 按情绪类型分组统计
        emotion_stats = {}
        for event in self.emotion_events:
            emotion = event.emotion
            if emotion not in emotion_stats:
                emotion_stats[emotion] = {
                    'count': 0,
                    'total_confidence': 0,
                    'min_confidence': 1.0,
                    'max_confidence': 0.0
                }
            
            stats = emotion_stats[emotion]
            stats['count'] += 1
            stats['total_confidence'] += event.confidence
            stats['min_confidence'] = min(stats['min_confidence'], event.confidence)
            stats['max_confidence'] = max(stats['max_confidence'], event.confidence)
        
        # 计算平均置信度
        for emotion, stats in emotion_stats.items():
            stats['avg_confidence'] = stats['total_confidence'] / stats['count']
            # 四舍五入置信度值
            stats['avg_confidence'] = round(stats['avg_confidence'], 4)
            stats['min_confidence'] = round(stats['min_confidence'], 4)
            stats['max_confidence'] = round(stats['max_confidence'], 4)
            # 删除总置信度字段
            del stats['total_confidence']
        
        # 计算主要情绪
        primary_emotion = max(emotion_stats.items(), key=lambda x: x[1]['count'])
        
        return {
            'emotion_stats': emotion_stats,
            'primary_emotion': primary_emotion[0],
            'total_events': len(self.emotion_events),
            'session_duration': round(time.time() - self.start_time, 2)
        }
    
    def save_to_file(self, filename):
        """保存情绪记录到CSV文件"""
        # 如果没有事件，不创建文件
        if not self.emotion_events:
            return False
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['timestamp', 'emotion', 'confidence', 'face_id']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for event in self.emotion_events:
                    writer.writerow(event.to_dict())
                
            return True
        except Exception as e:
            print(f"保存情绪记录时出错: {e}")
            return False
    
    def reset(self):
        """重置记录器"""
        self.emotion_events = []
        self.start_time = time.time() 