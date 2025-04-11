# emotion_detection/utils/emotion_detector.py
import cv2
import numpy as np
import tensorflow as tf
import os
from .model import CNN3

class EmotionDetector:
    def __init__(self, model_path):
        """初始化情绪检测器"""
        # 加载模型架构
        self.model = CNN3()
        
        # 加载预训练权重
        try:
            self.model.load_weights(model_path)
            print(f"模型加载成功: {model_path}")
        except Exception as e:
            print(f"模型加载失败: {e}")
            raise
        
        # 情绪类别映射
        self.emotions = ['anger', 'disgust', 'fear', 'happy', 'sad', 'surprised', 'neutral']
        
        # 初始化人脸检测器
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def preprocess_face(self, face_img):
        """预处理人脸图像"""
        # 调整大小为48x48
        face_img = cv2.resize(face_img, (48, 48))
        
        # 转换为灰度图
        if len(face_img.shape) == 3:
            face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        
        # 归一化
        face_img = face_img / 255.0
        
        # 调整维度以适应模型输入 [batch_size, height, width, channels]
        face_img = np.expand_dims(face_img, 0)
        face_img = np.expand_dims(face_img, -1)
        
        return face_img
    
    def detect_emotion(self, image):
        """
        检测图像中的人脸及其情绪
        
        参数:
            image: BGR格式的图像
            
        返回:
            包含人脸位置和情绪的字典列表
        """
        # 转为灰度图像
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 应用直方图均衡化以提高对比度
        gray = cv2.equalizeHist(gray)
        
        # 检测人脸 - 降低minNeighbors参数以提高检测率
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=4,  # 从5降低到4
            minSize=(30, 30)
        )
        
        # 调试信息
        print(f"检测到 {len(faces)} 个人脸")
        
        # 如果没有检测到人脸，尝试使用更宽松的参数
        if len(faces) == 0:
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.05, 
                minNeighbors=2, 
                minSize=(20, 20)
            )
            print(f"使用宽松参数后检测到 {len(faces)} 个人脸")
        
        results = []
        for (x, y, w, h) in faces:
            # 提取人脸区域
            face_roi = gray[y:y+h, x:x+w]
            
            # 预处理
            processed_face = self.preprocess_face(face_roi)
            
            # 预测情绪
            emotion_predictions = self.model.predict(processed_face, verbose=0)[0]
            
            # 获取最高概率的情绪
            emotion_idx = np.argmax(emotion_predictions)
            emotion = self.emotions[emotion_idx]
            confidence = float(emotion_predictions[emotion_idx])
            
            # 存储结果
            result = {
                'box': (x, y, w, h),
                'emotion': emotion,
                'confidence': confidence,
                'all_emotions': {e: float(s) for e, s in zip(self.emotions, emotion_predictions)}
            }
            
            results.append(result)
        
        return results