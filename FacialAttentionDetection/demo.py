import cv2
import dlib
import numpy as np
import time
import os
import matplotlib.pyplot as plt
from datetime import datetime
from record import DistractionRecorder

class AttentionDetectionDemo:
    """面部注意力检测演示类"""
    
    def __init__(self):
        """初始化演示程序"""
        # 加载人脸检测器和预测器
        self.detector = dlib.get_frontal_face_detector()
        try:
            model_path = './models/shape_predictor_68_face_landmarks.dat'
            if not os.path.exists(model_path):
                print(f"警告: 模型文件 {model_path} 不存在!")
                print("尝试在当前目录查找...")
                model_path = 'shape_predictor_68_face_landmarks.dat'
            self.predictor = dlib.shape_predictor(model_path)
        except RuntimeError as e:
            print(f"错误: 无法加载面部关键点预测模型: {e}")
            exit()
            
        # 定义参数
        self.EAR_THRESHOLD = 0.21
        self.DISTRACTION_FRAMES = 3
        
        # 初始化状态变量
        self.ear_history = []
        self.attention_history = []  # 用于记录注意力状态历史
        self.distraction_counter = 0
        self.is_currently_distracted = False
        
        # 初始化记录器
        self.recorder = DistractionRecorder()
        
        # 开始时间
        self.start_time = None
        
        # 可视化设置
        self.plot_width = 300
        self.plot_height = 100
        self.visualization = np.ones((self.plot_height, self.plot_width, 3), dtype=np.uint8) * 255
        
    def calculate_ear(self, eye_landmarks):
        """计算眼睛纵横比"""
        # 计算垂直距离
        A = np.linalg.norm(np.array([eye_landmarks[1].x, eye_landmarks[1].y]) - 
                        np.array([eye_landmarks[5].x, eye_landmarks[5].y]))
        B = np.linalg.norm(np.array([eye_landmarks[2].x, eye_landmarks[2].y]) - 
                        np.array([eye_landmarks[4].x, eye_landmarks[4].y]))
        # 计算水平距离
        C = np.linalg.norm(np.array([eye_landmarks[0].x, eye_landmarks[0].y]) - 
                        np.array([eye_landmarks[3].x, eye_landmarks[3].y]))
        # 计算EAR
        ear = (A + B) / (2.0 * C) if C > 0 else 0
        return ear
    
    def estimate_head_pose(self, landmarks):
        """估计头部姿态"""
        nose = (landmarks.part(30).x, landmarks.part(30).y)
        left = (landmarks.part(0).x, landmarks.part(0).y)
        right = (landmarks.part(16).x, landmarks.part(16).y)
        center_x = (left[0] + right[0]) // 2
        return abs(nose[0] - center_x) > (right[0] - left[0]) * 0.15
    
    def update_visualization(self, is_distracted):
        """更新注意力可视化图表"""
        # 记录注意力状态
        self.attention_history.append(0 if is_distracted else 1)
        
        # 如果历史记录超过绘图宽度，移除最早的记录
        if len(self.attention_history) > self.plot_width:
            self.attention_history = self.attention_history[-self.plot_width:]
        
        # 创建新的可视化图像
        self.visualization = np.ones((self.plot_height, self.plot_width, 3), dtype=np.uint8) * 255
        
        # 绘制注意力历史
        for i, attention in enumerate(self.attention_history):
            if i >= self.plot_width:
                break
            color = (0, 0, 255) if attention == 0 else (0, 255, 0)  # 红色表示分心，绿色表示专注
            cv2.line(self.visualization, 
                    (i, self.plot_height), 
                    (i, int(self.plot_height * (1 - attention * 0.8))), 
                    color, 1)
        
        # 添加水平线表示阈值
        cv2.line(self.visualization, 
                (0, int(self.plot_height * 0.5)), 
                (self.plot_width, int(self.plot_height * 0.5)), 
                (0, 0, 0), 1)
    
    def run(self):
        """运行演示程序"""
        # 打开摄像头
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("错误: 无法打开摄像头")
            return
        
        self.start_time = time.time()
        
        while True:
            # 读取帧
            ret, frame = cap.read()
            if not ret:
                print("错误: 无法获取视频帧")
                break
            
            # 创建信息展示区
            info_panel = np.ones((frame.shape[0], 300, 3), dtype=np.uint8) * 240
            
            # 检测与分析
            current_frame_distracted = self.process_frame(frame)
            
            # 更新分心记录
            if current_frame_distracted and not self.is_currently_distracted:
                self.is_currently_distracted = True
                self.recorder.start_distraction_event()
            elif not current_frame_distracted and self.is_currently_distracted:
                self.is_currently_distracted = False
                self.recorder.end_distraction_event()
            
            # 更新可视化
            self.update_visualization(current_frame_distracted)
            
            # 显示信息面板
            self.draw_info_panel(info_panel)
            
            # 合并主视图和信息面板
            combined_view = np.hstack((frame, info_panel))
            
            # 显示结果
            cv2.imshow('面部注意力检测演示', combined_view)
            
            # 检查按键
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # 按Q退出
                break
            elif key == ord('s'):  # 按S保存记录
                self.save_record()
            elif key == ord('r'):  # 按R重置记录
                self.reset()
            
        # 释放资源
        cap.release()
        cv2.destroyAllWindows()
    
    def process_frame(self, frame):
        """处理单帧并返回是否分心"""
        # 转换为灰度图像
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 检测人脸
        faces = self.detector(gray)
        
        # 当前帧是否分心
        current_frame_distracted = False
        
        # 显示运行时间
        elapsed_time = time.time() - self.start_time
        cv2.putText(frame, f"运行时间: {int(elapsed_time)}秒", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if not faces:
            # 没有检测到人脸
            cv2.putText(frame, "未检测到人脸", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            current_frame_distracted = True
        
        for face in faces:
            # 检测面部特征点
            landmarks = self.predictor(gray, face)
            
            # 提取眼睛关键点
            left_eye_landmarks = [landmarks.part(i) for i in range(36, 42)]
            right_eye_landmarks = [landmarks.part(i) for i in range(42, 48)]
            
            # 计算眼睛纵横比
            left_ear = self.calculate_ear(left_eye_landmarks)
            right_ear = self.calculate_ear(right_eye_landmarks)
            ear = (left_ear + right_ear) / 2.0
            
            # 更新眼睛状态历史
            self.ear_history.append(ear)
            if len(self.ear_history) > 10:
                self.ear_history.pop(0)
            avg_ear = sum(self.ear_history) / len(self.ear_history)
            
            # 检查头部姿态
            head_turned = self.estimate_head_pose(landmarks)
            
            # 绘制面部关键点
            for n in range(0, 68):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
            
            # 高亮眼睛区域
            for eye_points in [left_eye_landmarks, right_eye_landmarks]:
                points = [(p.x, p.y) for p in eye_points]
                hull = cv2.convexHull(np.array(points))
                cv2.drawContours(frame, [hull], -1, (0, 255, 0), 1)
            
            # 显示眼睛状态
            cv2.putText(frame, f"眼睛开度: {avg_ear:.2f}", (face.left(), face.bottom() + 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # 分析注意力状态
            if avg_ear < self.EAR_THRESHOLD or head_turned:
                current_frame_distracted = True
                self.distraction_counter += 1
            else:
                self.distraction_counter = max(0, self.distraction_counter - 1)
            
            # 显示注意力状态
            if self.distraction_counter >= self.DISTRACTION_FRAMES:
                cv2.putText(frame, "注意力分散", (face.left(), face.top() - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                cv2.rectangle(frame, (face.left(), face.top()), 
                            (face.right(), face.bottom()), (0, 0, 255), 2)
            else:
                cv2.rectangle(frame, (face.left(), face.top()), 
                            (face.right(), face.bottom()), (0, 255, 0), 2)
        
        # 更新分心记录和检查是否需要提醒
        if current_frame_distracted and self.is_currently_distracted:
            # 检查是否需要触发提醒
            if self.recorder.check_reminder_needed():
                # 在画面上显示大警告
                warning_text = "警告：分心时间过长！"
                text_size = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_TRIPLEX, 1.2, 2)[0]
                text_x = (frame.shape[1] - text_size[0]) // 2
                text_y = (frame.shape[0] + text_size[1]) // 2
                
                # 绘制半透明背景
                overlay = frame.copy()
                cv2.rectangle(overlay, (text_x - 20, text_y - text_size[1] - 20), 
                             (text_x + text_size[0] + 20, text_y + 20), 
                             (0, 0, 200), -1)
                cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
                
                # 绘制警告文字
                cv2.putText(frame, warning_text, (text_x, text_y), 
                          cv2.FONT_HERSHEY_TRIPLEX, 1.2, (255, 255, 255), 2)
            
            # 在状态面板显示当前分心持续时间
            current_distraction_time = self.recorder.get_current_distraction_time()
            if current_distraction_time >= 5:  # 只有超过5秒才显示计时器
                cv2.putText(frame, f"当前分心: {current_distraction_time:.1f}秒", 
                          (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                          (0, 165, 255) if current_distraction_time < 10 else (0, 0, 255), 2)
        
        return current_frame_distracted
    
    def draw_info_panel(self, panel):
        """在信息面板上绘制统计数据和控制信息"""
        # 绘制标题
        cv2.putText(panel, "注意力检测统计", (20, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        
        # 绘制分割线
        cv2.line(panel, (10, 40), (290, 40), (200, 200, 200), 1)
        
        # 获取统计数据
        total_time, event_count = self.recorder.get_statistics()
        
        # 显示统计信息
        cv2.putText(panel, f"分心次数: {event_count}", (20, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        cv2.putText(panel, f"总分心时间: {total_time:.1f}秒", (20, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        elapsed = time.time() - self.start_time
        minutes, seconds = divmod(int(elapsed), 60)
        hours, minutes = divmod(minutes, 60)
        
        cv2.putText(panel, f"总运行时间: {hours:02d}:{minutes:02d}:{seconds:02d}", (20, 130), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        if total_time > 0 and elapsed > 0:
            distraction_percentage = (total_time / elapsed) * 100
            cv2.putText(panel, f"分心占比: {distraction_percentage:.1f}%", (20, 160), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        # 绘制注意力历史可视化
        viz_y = 200
        panel[viz_y:viz_y+self.plot_height, 10:10+self.plot_width] = self.visualization
        
        # 添加图表标签
        cv2.putText(panel, "注意力状态历史", (20, viz_y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # 添加控制说明
        controls_y = viz_y + self.plot_height + 30
        cv2.putText(panel, "控制:", (20, controls_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        cv2.putText(panel, "Q - 退出", (30, controls_y + 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv2.putText(panel, "S - 保存记录", (30, controls_y + 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv2.putText(panel, "R - 重置统计", (30, controls_y + 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    def save_record(self):
        """保存分心记录"""
        record_file = f"distraction_record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        if self.recorder.save_to_file(record_file):
            print(f"分心记录已保存至: {record_file}")
            
    def reset(self):
        """重置统计数据"""
        self.recorder = DistractionRecorder()
        self.ear_history = []
        self.attention_history = []
        self.distraction_counter = 0
        self.is_currently_distracted = False
        self.start_time = time.time()
        print("统计数据已重置")

if __name__ == "__main__":
    print("启动面部注意力检测演示...")
    print("按Q退出，S保存记录，R重置统计")
    demo = AttentionDetectionDemo()
    demo.run()