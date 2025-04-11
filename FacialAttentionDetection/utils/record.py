import time
import csv
from datetime import datetime

class DistractionEvent:
    """表示一次分心事件的类"""
    
    def __init__(self, start_time):
        """初始化分心事件"""
        self.start_time = start_time
        self.end_time = None
        self.duration = None
    
    def end(self, end_time):
        """结束分心事件"""
        self.end_time = end_time
        self.duration = end_time - self.start_time
        return self.duration
    
    def to_dict(self):
        """将事件转换为字典格式"""
        return {
            'start_time': datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'end_time': datetime.fromtimestamp(self.end_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] if self.end_time else None,
            'duration': round(self.duration, 2) if self.duration else None
        }

class DistractionRecorder:
    """分心事件记录器"""
    
    def __init__(self):
        """初始化分心记录器"""
        self.distraction_events = []
        self.current_event = None
        self.reminder_threshold = 10  # 提醒阈值（秒）
        self.reminder_triggered = False  # 标记是否已触发提醒
    
    def start_distraction_event(self):
        """开始一个新的分心事件"""
        if not self.current_event:  # 确保没有未结束的事件
            self.current_event = DistractionEvent(time.time())
            self.reminder_triggered = False  # 重置提醒状态
    
    def end_distraction_event(self):
        """结束当前分心事件"""
        if self.current_event:
            duration = self.current_event.end(time.time())
            self.distraction_events.append(self.current_event)
            self.current_event = None
            self.reminder_triggered = False  # 重置提醒状态
            return duration
        return 0
    
    def get_statistics(self):
        """获取分心统计数据"""
        total_distraction_time = sum(event.duration for event in self.distraction_events if event.duration is not None)
        if self.current_event:
            # 当前正在进行的分心事件
            ongoing_duration = time.time() - self.current_event.start_time
            total_distraction_time += ongoing_duration
        
        return total_distraction_time, len(self.distraction_events) + (1 if self.current_event else 0)
    
    def check_reminder_needed(self):
        """检查是否需要触发提醒"""
        if self.current_event and not self.reminder_triggered:
            current_duration = time.time() - self.current_event.start_time
            if current_duration >= self.reminder_threshold:
                self.reminder_triggered = True
                return True
        return False
    
    def get_current_distraction_time(self):
        """获取当前分心事件的持续时间"""
        if self.current_event:
            return time.time() - self.current_event.start_time
        return 0
    
    def save_to_file(self, filename):
        """保存分心记录到CSV文件"""
        events_to_save = self.distraction_events.copy()
        
        # 如果有正在进行的事件，结束它并添加到列表中
        if self.current_event:
            temp_event = DistractionEvent(self.current_event.start_time)
            temp_event.end(time.time())
            events_to_save.append(temp_event)
        
        # 如果没有事件，不创建文件
        if not events_to_save:
            return False
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['start_time', 'end_time', 'duration']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for event in events_to_save:
                    writer.writerow(event.to_dict())
                
            return True
        except Exception as e:
            print(f"保存分心记录时出错: {e}")
            return False