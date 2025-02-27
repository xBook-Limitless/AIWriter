import tkinter as tk
from tkinter import ttk
from modules.GlobalModule import global_config as global_api_config
from utils.config_loader import get_version_info
from tkinter import Toplevel, Label
from tkinter import messagebox
from ui.panels.ParameterPanel import ParameterPanel
from ui.panels.GetApiKey import GetApiKeyPanel
from tkinter import Menu
from ui.panels.BaseConfiguration import BaseConfiguration
from ui.panels.WorldView import WorldViewPanel
import json
from pathlib import Path
from tkinter import filedialog
import yaml

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
        settings_menu.add_command(label="导出小说框架", command=lambda: export_novel_structure(root))
        settings_menu.add_command(label="导入小说框架", command=lambda: import_novel_structure(root))
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
                f"温度: {global_api_config.generation_params.temperature:.2f} (0.0-2.0)\n"
                f"核心采样: {global_api_config.generation_params.top_p:.2f}\n"
                f"频率惩罚: {global_api_config.generation_params.frequency_penalty:.1f}\n"
                f"存在惩罚: {global_api_config.generation_params.presence_penalty:.1f}\n"
                f"输出格式: {global_api_config.generation_params.response_format.get('type', 'text')}\n"
                f"最大长度: {global_api_config.generation_params.max_tokens:,} tokens"
            )
        )

        # 再添加参数设置按钮
        ttk.Button(
            control_frame, 
            text="参数设置", 
            command=lambda: show_parameter_panel(root)
        ).pack(side=tk.LEFT, padx=5)

        control_frame.pack(fill=tk.X, pady=5)

        # 添加分页容器（在控制按钮下方）
        notebook = ttk.Notebook(root)
        
        # 创建小说框架分页
        novel_frame = ttk.Frame(notebook)
        notebook.add(novel_frame, text="小说框架")
        
        # 创建小说框架内部的分页
        novel_notebook = ttk.Notebook(novel_frame)
        novel_notebook.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # 基础配置页面
        base_config_frame = ttk.Frame(novel_notebook)
        novel_notebook.add(base_config_frame, text="基础配置")
        BaseConfiguration(base_config_frame).pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # 世界观页面
        world_view_frame = ttk.Frame(novel_notebook)
        novel_notebook.add(world_view_frame, text="世界观构建")
        WorldViewPanel(world_view_frame).pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

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

    # root.geometry("900x600")  # 确保窗口足够大
    # root.minsize(900, 600)   # 设置最小尺寸

    style = ttk.Style()
    style.theme_use("clam")  # 改为经典主题测试

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

def export_novel_structure(parent):
    """导出小说框架数据"""
    try:
        # 读取当前配置
        config_file = Path("data/configs/novel_structure.yaml")
        if not config_file.exists():
            messagebox.showwarning("提示", "没有可导出的配置")
            return
            
        with open(config_file, "r", encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # 获取作品名称
        base_config = data.get("base_config", {})
        title = base_config.get("title", "未命名作品").strip() or "未命名作品"
        
        # 创建保存路径
        save_dir = Path(f"data/NovelData/{title}")
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存JSON
        json_path = save_dir / f"{title}_框架.json"
        with open(json_path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        # 保存TXT
        txt_path = save_dir / f"{title}_框架.txt"
        with open(txt_path, "w", encoding='utf-8') as f:
            # 基础信息
            txt_content = f"作品名称：{base_config.get('title', '')}\n"
            txt_content += f"创作类型：{base_config.get('creation_type', '')}\n"
            txt_content += f"主类型：{base_config.get('main_type', '')}\n"
            txt_content += f"子类型：{base_config.get('sub_type', '')}\n\n"
            
            # 其他模块占位
            txt_content += "=== 其他模块配置 ===\n"
            txt_content += "（完整配置请查看JSON文件）"
            
            f.write(txt_content)
            
        messagebox.showinfo("导出成功", 
            f"已导出到：\n{save_dir}\n"
            f"JSON文件：{json_path.name}\n"
            f"TXT文件：{txt_path.name}")
            
    except Exception as e:
        messagebox.showerror("导出失败", f"错误信息：{str(e)}")

def import_novel_structure(parent):
    """导入小说框架数据"""
    try:
        file_path = filedialog.askopenfilename(
            parent=parent,
            title="选择要导入的框架文件",
            filetypes=[("JSON文件", "*.json"), ("YAML文件", "*.yaml"), ("所有文件", "*.*")]
        )
        if not file_path:
            return
            
        target_file = Path("data/configs/novel_structure.yaml")
        target_file.parent.mkdir(exist_ok=True)
        
        # 读取文件内容
        with open(file_path, "r", encoding='utf-8') as f:
            if file_path.endswith(".json"):
                data = json.load(f)
            else:  # 支持yaml格式
                data = yaml.safe_load(f)
        
        # 写入配置文件时添加sort_keys=False
        with open(target_file, "w", encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        
        messagebox.showinfo("导入成功", 
            "配置已导入，部分功能可能需要重启后生效\n"
            f"文件路径：{target_file}")
            
    except Exception as e:
        messagebox.showerror("导入失败", f"错误信息：{str(e)}")

if __name__ == "__main__":
    root = create_main_window()
    root.mainloop()
