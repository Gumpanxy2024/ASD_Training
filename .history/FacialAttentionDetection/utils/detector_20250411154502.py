import cv2
import dlib
import numpy as np
import time

class AttentionDetector:
    """面部注意力检测类"""
    
    def __init__(self, model_path):
        """初始化检测器"""
        # 加载人脸检测器和面部关键点检测器
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(model_path)
        
        # 参数
        self.EAR_THRESHOLD = 0.21
        
        # 状态变量
        self.ear_history = []
        self.is_currently_distracted = False
        self.start_time = time.time()
        self.elapsed_time = 0
    
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
    
    def process_image(self, image):
        """处理单个图像帧"""
        self.elapsed_time = time.time() - self.start_time
        
        # 结果字典
        result = {
            'face_detected': False,
            'is_distracted': False,
            'avg_ear': None,
            'head_turned': False,
            'image_width': image.shape[1],
            'image_height': image.shape[0]
        }
        
        # 转为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 检测人脸
        faces = self.detector(gray)
        
        if not faces:
            result['is_distracted'] = True
            return result
        
        # 处理检测到的第一个人脸
        face = faces[0]
        result['face_detected'] = True
        
        # 保存人脸框位置
        result['face_box'] = {
            'x': face.left(),
            'y': face.top(),
            'width': face.width(),
            'height': face.height()
        }
        
        # 检测面部关键点
        landmarks = self.predictor(gray, face)
        
        # 提取眼睛关键点
        left_eye = [landmarks.part(i) for i in range(36, 42)]
        right_eye = [landmarks.part(i) for i in range(42, 48)]
        
        # 计算眼睛开度
        left_ear = self.calculate_ear(left_eye)
        right_ear = self.calculate_ear(right_eye)
        ear = (left_ear + right_ear) / 2.0
        
        # 更新眼睛状态历史
        self.ear_history.append(ear)
        if len(self.ear_history) > 10:
            self.ear_history.pop(0)
        avg_ear = sum(self.ear_history) / len(self.ear_history)
        
        # 检查头部姿态
        head_turned = self.estimate_head_pose(landmarks)
        
        # 更新结果
        result['avg_ear'] = avg_ear
        result['head_turned'] = head_turned
        result['is_distracted'] = avg_ear < self.EAR_THRESHOLD or head_turned
        
        # 提取关键点坐标
        result['landmarks'] = [
            {'x': landmarks.part(i).x, 'y': landmarks.part(i).y} 
            for i in range(68)
        ]
        
        return result
    
    def reset(self):
        """重置检测器状态"""
        self.ear_history = []
        self.is_currently_distracted = False
        self.start_time = time.time()
        self.elapsed_time = 0