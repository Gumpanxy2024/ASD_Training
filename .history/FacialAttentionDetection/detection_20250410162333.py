import cv2
import dlib
import numpy as np
 
# 加载人脸检测器和面部标志物预测器
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
 
# 加载眼睛检测器（可根据实际需求选择合适的模型）
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
 
# 定义专注度阈值
DISTRACTION_THRESHOLD = 0.2
 
# 打开摄像头
cap = cv2.VideoCapture(0)
 
while True:
    # 读取当前帧
    ret, frame = cap.read()
 
    # 将当前帧转换为灰度图像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 
    # 检测人脸
    faces = detector(gray)
 
    for face in faces:
        # 检测面部标志物
        landmarks = predictor(gray, face)
        # 绘制人脸关键点
        for n in range(0, 68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
 
        # 提取左眼和右眼区域
        left_eye = landmarks.part(36).x, landmarks.part(36).y, \
                   landmarks.part(39).x - landmarks.part(36).x, \
                   landmarks.part(39).y - landmarks.part(36).y
        right_eye = landmarks.part(42).x, landmarks.part(42).y, \
                    landmarks.part(45).x - landmarks.part(42).x, \
                    landmarks.part(45).y - landmarks.part(42).y
 
        # 在眼睛区域内检测眼睛
        gray_face = gray[face.top():face.bottom(), face.left():face.right()]
        eyes = eye_cascade.detectMultiScale(gray_face, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
 
        # 计算眼睛平均开闭程度
        if len(eyes) > 0:
            total_eye_openness = 0.0
            for eye in eyes:
                eye_width = eye[2]
                eye_height = eye[3]
                total_eye_openness += (eye_height / left_eye[2]) + (eye_height / right_eye[2])
 
            eye_openness = total_eye_openness / len(eyes)
            #打印眼睛睁开大小
            print(eye_openness);
            # 判断专注度
            if eye_openness < DISTRACTION_THRESHOLD:
                cv2.putText(frame, "DISTRACTED", (face.left(), face.top() - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
 
    # 绘制人脸区域
    for face in faces:
        cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (0, 255, 0), 2)
 
    # 显示当前帧
    cv2.imshow('Face Distraction Detection', frame)
 
    # 按下 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
 
# 释放摄像头资源
cap.release()
 
# 关闭所有窗口
cv2.destroyAllWindows()