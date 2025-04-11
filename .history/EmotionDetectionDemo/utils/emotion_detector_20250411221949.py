# emotion_detection/utils/emotion_detector.py
import cv2
import numpy as np
import tensorflow as tf
import os
import sys

# 确保可以导入同级目录的模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if (current_dir not in sys.path):
    sys.path.append(current_dir)

# 现在可以直接导入
from model import CNN3

# 设置TensorFlow日志级别
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 仅显示错误信息

# 导入BlazeFace相关模块
try:
    from blazeface import blaze_detect
    BLAZE_AVAILABLE = True
    print("BlazeFace 人脸检测器已加载")
except ImportError:
    BLAZE_AVAILABLE = False
    print("警告：未找到BlazeFace模块，将仅使用OpenCV进行人脸检测")


class EmotionDetector:
    def __init__(self, model_path, use_blaze=True):
        """
        初始化情绪检测器
        
        参数:
            model_path: 模型权重路径
            use_blaze: 是否使用BlazeFace检测器(如果可用)
        """
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
        # 添加备用人脸检测器
        self.alt_face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
        
        # BlazeFace设置
        self.use_blaze = use_blaze and BLAZE_AVAILABLE
    
    def generate_faces(self, face_img, img_size=48):
        """
        将探测到的人脸进行增广，参考recognition_camera.py
        :param face_img: 灰度化的单个人脸图
        :param img_size: 目标图片大小
        :return: 增广后的人脸图像数组
        """
        # 确保输入是灰度图像
        if len(face_img.shape) == 3:
            face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        
        # 归一化
        face_img = face_img / 255.0
        # 调整大小
        face_img = cv2.resize(face_img, (img_size, img_size), interpolation=cv2.INTER_LINEAR)
        
        resized_images = []
        # 原始图像
        resized_images.append(face_img)
        # 裁剪变体1 - 上部裁剪
        resized_images.append(face_img[2:45, :])
        # 裁剪变体2 - 轻微裁剪
        resized_images.append(face_img[1:47, :])
        # 水平翻转
        resized_images.append(cv2.flip(face_img[:, :], 1))

        # 重新调整大小并添加通道维度
        for i in range(len(resized_images)):
            resized_images[i] = cv2.resize(resized_images[i], (img_size, img_size))
            # 重要：添加通道维度
            resized_images[i] = np.expand_dims(resized_images[i], axis=-1)
        
        # 转换为numpy数组
        resized_images = np.array(resized_images)
        return resized_images
    
    def preprocess_face(self, face_img):
        """
        预处理单个人脸图像
        :param face_img: 人脸区域图像
        :return: 预处理后的图像
        """
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
        # 转为RGB格式用于BlazeFace检测
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 转为灰度图像用于情感分析
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 应用直方图均衡化以提高对比度
        gray = cv2.equalizeHist(gray)
        
        faces = []
        
        # 首先尝试BlazeFace检测
        if self.use_blaze and BLAZE_AVAILABLE:
            try:
                print("使用BlazeFace进行人脸检测...")
                blaze_faces = blaze_detect(image_rgb, scoreThreshold=0.7, iouThreshold=0.3)
                if blaze_faces is not None:
                    print(f"BlazeFace检测到 {len(blaze_faces)} 个人脸")
                    faces = blaze_faces
                    # 注意: blaze_detect返回[x, y, w, h]格式的人脸框
            except Exception as e:
                print(f"BlazeFace检测出错: {e}")
        
        # 如果BlazeFace失败或未启用，使用OpenCV级联分类器
        if len(faces) == 0:
            print("使用OpenCV进行人脸检测...")
            # 第一步：使用默认检测器进行人脸检测
            opencv_faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=3, 
                minSize=(30, 30)
            )
            
            print(f"OpenCV默认检测器检测到 {len(opencv_faces)} 个人脸")
            
            if len(opencv_faces) > 0:
                faces = opencv_faces
            else:
                # 尝试备用检测器
                opencv_faces_alt = self.alt_face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.05, 
                    minNeighbors=2, 
                    minSize=(30, 30)
                )
                print(f"备用检测器检测到 {len(opencv_faces_alt)} 个人脸")
                
                if len(opencv_faces_alt) > 0:
                    faces = opencv_faces_alt
        
        # 没有检测到人脸
        if len(faces) == 0:
            return []
        
        results = []
        for i, (x, y, w, h) in enumerate(faces):
            try:
                # 扩大人脸区域范围，以包含更多特征
                y_offset = int(h * 0.1)  # 向上扩展10%
                h_offset = int(h * 0.1)  # 向下扩展10%
                
                # 确保不会超出图像边界
                y_start = max(0, y - y_offset)
                y_end = min(image.shape[0], y + h + h_offset)
                x_start = max(0, x)
                x_end = min(image.shape[1], x + w)
                
                # 提取人脸区域
                face_roi = gray[y_start:y_end, x_start:x_end]
                
                print(f"处理人脸 #{i+1}, 尺寸: {face_roi.shape}")
                
                # 使用数据增强进行预测
                faces_augmented = self.generate_faces(face_roi)
                
                print(f"增广后的人脸形状: {faces_augmented.shape}")
                
                # 预测情绪 - 使用数据增强后的多个图像
                emotion_predictions_batch = self.model.predict(faces_augmented, verbose=0)
                
                # 合并多个预测结果
                emotion_predictions_sum = np.sum(emotion_predictions_batch, axis=0)
                
                # 获取最高概率的情绪
                emotion_idx = np.argmax(emotion_predictions_sum)
                emotion = self.emotions[emotion_idx]
                confidence = float(emotion_predictions_sum[emotion_idx] / np.sum(emotion_predictions_sum))
                
                print(f"检测到情绪: {emotion}, 置信度: {confidence}")
                
                # 存储结果
                result = {
                    'box': (x, y, w, h),
                    'emotion': emotion,
                    'confidence': confidence,
                    'all_emotions': {e: float(s / np.sum(emotion_predictions_sum)) 
                                    for e, s in zip(self.emotions, emotion_predictions_sum)}
                }
                
                results.append(result)
                
            except Exception as e:
                print(f"处理人脸时出错: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        return results