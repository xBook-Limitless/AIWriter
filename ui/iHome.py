import tkinter as tk
from tkinter import ttk
from utils.config_loader import get_version_info

def create_main_window():
    """创建自适应窗口"""
    root = tk.Tk()
    version = get_version_info()
    root.title(f"AIWriter {version}")
    
    # 获取屏幕尺寸
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # 计算80%的屏幕尺寸
    window_width = int(screen_width * 0.7)
    window_height = int(screen_height * 0.7)
    
    # 设置窗口尺寸并居中
    root.geometry(f"{window_width}x{window_height}")
    root.resizable(True, True)  # 允许调整窗口大小
    
    # 计算居中位置（带视觉修正）
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2 - 50  # 增加垂直偏移量
    
    root.geometry(f"+{x}+{y}")
    return root
