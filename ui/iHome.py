import tkinter as tk
from tkinter import ttk
from modules.GlobalModule import global_config as global_api_config
from utils.config_loader import get_version_info
from tkinter import Toplevel, Label
from tkinter import messagebox
from ui.panels.ParameterPanel import ParameterPanel
from ui.panels.GetApiKey import GetApiKeyPanel
from tkinter import Menu

# 将Tooltip类定义移到文件顶部
class Tooltip:
    def __init__(self, widget, text_getter):
        self.widget = widget
        self.text_getter = text_getter  # 改为接受函数
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
        label = Label(self.tipwindow, text=self.text_getter(), justify='left',  # 动态获取
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

        # 在菜单栏下方添加控制按钮
        control_frame = ttk.Frame(root)

        # 先添加状态指示灯
        status_label = ttk.Label(
            control_frame, 
            text="●", 
            font=('Arial', 16),
            foreground="gray"
        )
        status_label.pack(side=tk.LEFT, padx=5)

        # 在创建status_label后添加Tooltip
        status_tooltip = Tooltip(
            status_label,
            lambda: (
                f"● 服务状态: {'已连接' if global_api_config.connection_monitor.status else '已断开'}\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"服务商: {global_api_config.model_config.provider}\n"
                f"AI模型: {global_api_config.model_config.model}\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"温度: {global_api_config.generation_param.temperature:.2f} (0.0-2.0)\n"
                f"核心采样: {global_api_config.generation_param.top_p:.2f}\n"
                f"频率惩罚: {global_api_config.generation_param.frequency_penalty:.1f}\n"
                f"存在惩罚: {global_api_config.generation_param.presence_penalty:.1f}\n"
                f"输出格式: {global_api_config.generation_param.response_format.get('type', 'text')}\n"
                f"流式输出: {'启用' if global_api_config.generation_param.stream else '禁用'}\n"
                f"最大长度: {global_api_config.generation_param.max_tokens:,} tokens"
            )
        )

        # 再添加参数设置按钮
        ttk.Button(
            control_frame, 
            text="参数设置", 
            command=lambda: show_parameter_panel(root)
        ).pack(side=tk.LEFT, padx=5)

        control_frame.pack(fill=tk.X, pady=5)

        # 启动连接监控
        global_api_config.connection_monitor.start_monitoring()
        
        # 添加状态更新循环
        def update_status():
            color = "green" if global_api_config.connection_monitor.status else "red"
            status_label.config(foreground=color)
            root.after(5000, update_status)
        
        update_status()

        # 在状态标签添加右键菜单
        def show_status_menu(event):
            menu = Menu(root, tearoff=0)
            menu.add_command(label="立即刷新", command=lambda: force_check_status(status_label))
            menu.post(event.x_root, event.y_root)

        status_label.bind("<Button-3>", show_status_menu)

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

# 新增独立参数窗口管理
_parameter_window = None

def show_parameter_panel(parent):
    global _parameter_window
    if not _parameter_window or not _parameter_window.winfo_exists():
        _parameter_window = Toplevel(parent)
        _parameter_window.title("参数设置")
        _center_window(_parameter_window, 500, 309)  # 窗口尺寸450x250
        ParameterPanel(_parameter_window)
    else:
        _parameter_window.lift()  # 窗口已存在则提到最前

def _center_window(window, width, height):
    """居中显示窗口"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2 - 50  # 视觉垂直居中
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.resizable(False, False)  # 禁止调整大小

def force_check_status(label):
    global_api_config.connection_monitor._check_status()
    color = "green" if global_api_config.connection_monitor.status else "red"
    label.config(foreground=color)

if __name__ == "__main__":
    root = create_main_window()
    root.mainloop()
