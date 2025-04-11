# 添加到系统路径
import os
import sys
# 获取当前文件所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将该目录添加到系统路径
sys.path.append(current_dir)

# 直接从本地模块导入
try:
    from emotion_detector import EmotionDetector
except ImportError:
    # 记录导入错误但不中断程序
    import traceback
    print(f"导入 EmotionDetector 失败：{traceback.format_exc()}")

from .model import CNN3

__all__ = ['EmotionDetector', 'CNN3']

