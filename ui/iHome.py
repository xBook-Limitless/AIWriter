import tkinter as tk
from tkinter import ttk
from modules.GlobalModule import global_config as global_api_config
from utils.config_loader import get_version_info
from tkinter import Toplevel, Label
from tkinter import messagebox
from ui.panels.ParameterPanel import ParameterPanel
from ui.panels.GetApiKey import GetApiKeyPanel

# 将Tooltip类定义移到文件顶部
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.showtip)
        self.widget.bind("<Leave>", self.hidetip)

    def showtip(self, event):
        if self.tipwindow:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tipwindow = Toplevel(self.widget)
        self.tipwindow.wm_overrideredirect(True)
        self.tipwindow.wm_geometry(f"+{x}+{y}")
        label = Label(self.tipwindow, text=self.text, justify='left',
                      background="#ffffe0", relief='solid', borderwidth=1)
        label.pack()

    def hidetip(self, event):
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None

root = None  # 添加全局变量

def change_theme():
    """临时主题切换处理"""
    messagebox.showinfo("开发中", "主题切换功能正在开发中")

def create_main_window():
    """创建自适应窗口"""
    global root  # 添加全局引用
    if not root:
        root = tk.Tk()
        version = get_version_info()
        root.title(f"AIWriter {version}")
        
        # 创建菜单栏
        menu_bar = tk.Menu(root)
        
        # 设置菜单
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="API密钥管理", command=lambda: show_api_key_panel(root))
        settings_menu.add_command(label="主题", command=lambda: change_theme())
        settings_menu.add_separator()
        settings_menu.add_command(label="退出程序", command=root.destroy)
        
        menu_bar.add_cascade(label="设置", menu=settings_menu)
        root.config(menu=menu_bar)
        
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

        # 添加参数面板
        param_panel = ParameterPanel(root)
        param_panel.pack(pady=10, padx=20, fill=tk.X, ipadx=10, ipady=5)

    return root

# 新增显示密钥面板的函数
def show_api_key_panel(parent):
    panel = Toplevel(parent)
    panel.title("API密钥管理")
    GetApiKeyPanel(panel).pack(padx=20, pady=20)

# 添加自定义验证函数
def validate_max_tokens(new_value):
    """验证最大Token数输入"""
    if not new_value.isdigit():
        return False
    value = int(new_value)
    return 1 <= value <= 6400

# app = Flask(__name__)
# login_manager = LoginManager()
# login_manager.init_app(app)

if __name__ == "__main__":
    root = create_main_window()
    root.mainloop()
