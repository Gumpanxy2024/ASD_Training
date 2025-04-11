import cv2
import dlib
import numpy as np
import time
from datetime import datetime
from record import DistractionRecorder

def calculate_ear(eye_landmarks):
    """计算眼睛纵横比(EAR)"""
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

def estimate_head_pose(landmarks):
    """估计头部姿态"""
    # 获取鼻子顶点
    nose = (landmarks.part(30).x, landmarks.part(30).y)
    # 获取两侧面部点
    left = (landmarks.part(0).x, landmarks.part(0).y)
    right = (landmarks.part(16).x, landmarks.part(16).y)
    # 计算中心点
    center_x = (left[0] + right[0]) // 2
    # 如果鼻子偏离中心太多，判断为头部转向
    return abs(nose[0] - center_x) > (right[0] - left[0]) * 0.15

# 加载人脸检测器和面部标志物预测器
detector = dlib.get_frontal_face_detector()
try:
    predictor = dlib.shape_predictor('./models/shape_predictor_68_face_landmarks.dat')
except RuntimeError:
    print("错误：无法加载面部关键点预测模型，请确保文件存在")
    exit()

# 定义专注度相关参数
EAR_THRESHOLD = 0.21  # 眼睛纵横比阈值
DISTRACTION_FRAMES = 3  # 连续多少帧分心才触发警告

# 初始化分心记录器
recorder = DistractionRecorder()

# 状态变量
distraction_counter = 0
is_currently_distracted = False
ear_history = []

# 打开摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("错误：无法打开摄像头")
    exit()

start_time = time.time()

while True:
    # 读取当前帧
    ret, frame = cap.read()
    if not ret:
        print("无法获取视频帧，退出中...")
        break

    # 将当前帧转换为灰度图像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 检测人脸
    faces = detector(gray)
    
    # 当前帧的分心状态
    current_frame_distracted = False
    
    # 在帧上显示当前运行时间
    elapsed_time = time.time() - start_time
    cv2.putText(frame, f"时间: {int(elapsed_time)}秒", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    if not faces:
        # 如果没有检测到人脸，显示警告
        cv2.putText(frame, "未检测到人脸", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        current_frame_distracted = True
    
    for face in faces:
        # 检测面部标志物
        landmarks = predictor(gray, face)
        
        # 提取左眼和右眼的关键点
        left_eye_landmarks = [landmarks.part(i) for i in range(36, 42)]
        right_eye_landmarks = [landmarks.part(i) for i in range(42, 48)]
        
        # 计算左眼和右眼的EAR
        left_ear = calculate_ear(left_eye_landmarks)
        right_ear = calculate_ear(right_eye_landmarks)
        
        # 取左右眼EAR的平均值
        ear = (left_ear + right_ear) / 2.0
        
        # 更新EAR历史记录
        ear_history.append(ear)
        if len(ear_history) > 10:  # 保持最近10帧记录
            ear_history.pop(0)
        avg_ear = sum(ear_history) / len(ear_history)
        
        # 检查头部姿态
        head_turned = estimate_head_pose(landmarks)
        
        # 绘制关键点（可选，调试用）
        for n in range(0, 68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
        
        # 绘制左右眼区域
        for eye_points in [left_eye_landmarks, right_eye_landmarks]:
            points = [(p.x, p.y) for p in eye_points]
            hull = cv2.convexHull(np.array(points))
            cv2.drawContours(frame, [hull], -1, (0, 255, 0), 1)
        
        # 状态分析
        if avg_ear < EAR_THRESHOLD or head_turned:
            current_frame_distracted = True
            distraction_counter += 1
        else:
            distraction_counter = max(0, distraction_counter - 1)
        
        # 显示眼睛状态
        cv2.putText(frame, f"眼睛开度: {avg_ear:.2f}", (face.left(), face.bottom() + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # 判断是否分心
        if distraction_counter >= DISTRACTION_FRAMES:
            cv2.putText(frame, "注意力分散", (face.left(), face.top() - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            
            # 绘制红色框表示分心
            cv2.rectangle(frame, (face.left(), face.top()), 
                          (face.right(), face.bottom()), (0, 0, 255), 2)
        else:
            # 绘制绿色框表示专注
            cv2.rectangle(frame, (face.left(), face.top()), 
                          (face.right(), face.bottom()), (0, 255, 0), 2)
    
    # 更新分心记录
    if current_frame_distracted and not is_currently_distracted:
        # 分心事件开始
        is_currently_distracted = True
        recorder.start_distraction_event()
    elif not current_frame_distracted and is_currently_distracted:
        # 分心事件结束
        is_currently_distracted = False
        recorder.end_distraction_event()
    
    # 显示分心统计数据
    total_time, event_count = recorder.get_statistics()
    cv2.putText(frame, f"分心次数: {event_count}", (10, frame.shape[0] - 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"总分心时间: {total_time:.1f}秒", (10, frame.shape[0] - 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # 显示当前帧
    cv2.imshow('面部注意力检测', frame)
    
    # 按下 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 保存分心记录
record_file = f"distraction_record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
recorder.save_to_file(record_file)
print(f"分心记录已保存至: {record_file}")

# 释放摄像头资源
cap.release()

# 关闭所有窗口
cv2.destroyAllWindows()