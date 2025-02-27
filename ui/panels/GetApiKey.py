# 新增API密钥管理面板
import tkinter as tk
from tkinter import ttk, messagebox
from utils.config_loader import save_api_key
import httpx
from core.api_client.deepseek import api_client
from modules.GlobalModule import global_config

class GetApiKeyPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent  # 保存父窗口引用
        self.parent.attributes('-toolwindow', True)  # 隐藏最大化按钮
        style = ttk.Style()
        style.configure('Small.TButton', font=('微软雅黑', 8), padding=2)
        self._center_window()  # 窗口居中
        self._create_provider_tabs()
        self._load_saved_keys()
        
    def _center_window(self):
        """使窗口居中显示"""
        self.parent.update_idletasks()
        width = 400
        height = 160
        x = (self.parent.winfo_screenwidth() // 2) - (width // 2)
        y = (self.parent.winfo_screenheight() // 2) - (height // 2)
        self.parent.geometry(f'{width}x{height}+{x}+{y}')
        self.parent.resizable(False, False)  # 禁止调整窗口大小

    def _create_provider_tabs(self):
        """创建提供商选项卡"""
        tab_control = ttk.Notebook(self)
        
        # DeepSeek选项卡
        deepseek_frame = ttk.Frame(tab_control)
        self._create_provider_ui(deepseek_frame, "DeepSeek")
        tab_control.add(deepseek_frame, text="DeepSeek")
        
        # 通义千问选项卡
        qwen_frame = ttk.Frame(tab_control)
        self._create_provider_ui(qwen_frame, "Qwen")
        tab_control.add(qwen_frame, text="通义千问")
        
        # 腾讯混元选项卡
        hunyuan_frame = ttk.Frame(tab_control)
        self._create_provider_ui(hunyuan_frame, "HunYuan")
        tab_control.add(hunyuan_frame, text="腾讯混元")
        
        tab_control.pack(expand=1, fill="both")

    def _create_provider_ui(self, parent, provider):
        """创建单个提供商界面"""
        main_frame = ttk.Frame(parent)
        
        # 输入区域（紧凑布局）
        input_frame = ttk.Frame(main_frame)
        ttk.Label(input_frame, text=f"{provider}密钥:", font=('微软雅黑', 9)).pack(side=tk.LEFT)
        entry = ttk.Entry(input_frame, show="*", width=32)  # 缩短输入框宽度
        entry.pack(side=tk.LEFT, padx=2)  # 减少水平间距
        input_frame.pack(pady=2)  # 减少垂直间距
        setattr(self, f"{provider.lower()}_entry", entry)

        # 操作按钮（更小尺寸）
        ttk.Button(
            main_frame, 
            text="验证并保存", 
            command=lambda: self._test_and_save(provider),
            style='Small.TButton'  # 使用小号按钮样式
        ).pack(pady=2)

        # 状态提示（更小字体）
        status_label = ttk.Label(main_frame, text="", foreground="gray", font=('微软雅黑', 8))
        status_label.pack()
        setattr(self, f"{provider.lower()}_status", status_label)

        main_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=2)  # 减少边距

    def _test_and_save(self, provider):
        """根据提供商验证并保存"""
        api_key = getattr(self, f"{provider.lower()}_entry").get().strip()
        if not api_key:
            self._update_status(provider, "请输入有效的API密钥", "red")
            return

        try:
            # 根据提供商选择测试接口
            test_url = {
                "DeepSeek": f"{global_config.model_config.base_url}/models",
                "Qwen": "https://dashscope.aliyuncs.com/api/v1/models",
                "HunYuan": "https://api.hunyuan.cloud.tencent.com/v1/models"
            }[provider]
            
            response = httpx.get(
                test_url,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5
            )
            response.raise_for_status()
            
            self._save_api_key(provider, api_key)
            self._update_status(provider, "验证成功，密钥已保存", "green")
            
        except httpx.HTTPStatusError as e:
            self._update_status(provider, f"验证失败: HTTP {e.response.status_code}", "red")
        except Exception as e:
            self._update_status(provider, f"连接错误: {str(e)}", "red")

    def _save_api_key(self, provider, api_key):
        """保存指定提供商的密钥"""
        from utils.config_loader import get_api_key, save_api_key
        config = get_api_key()
        config["providers"][provider] = api_key
        save_api_key(config)

    def _update_status(self, provider, text: str, color: str = "black"):
        """更新状态文字"""
        getattr(self, f"{provider.lower()}_status").config(text=text, foreground=color)
        self.after(3000, lambda: getattr(self, f"{provider.lower()}_status").config(text="", foreground="gray"))

    def _load_saved_keys(self):
        """加载所有已保存的密钥"""
        from utils.config_loader import get_api_key
        config = get_api_key()
        
        # 加载DeepSeek密钥
        deepseek_key = config["providers"].get("DeepSeek", "")
        if deepseek_key:
            self.deepseek_entry.delete(0, tk.END)
            self.deepseek_entry.insert(0, deepseek_key)
        
        # 加载Qwen密钥
        qwen_key = config["providers"].get("Qwen", "")
        if qwen_key:
            self.qwen_entry.delete(0, tk.END)
            self.qwen_entry.insert(0, qwen_key)
            
        # 加载HunYuan密钥
        hunyuan_key = config["providers"].get("HunYuan", "")
        if hunyuan_key:
            self.hunyuan_entry.delete(0, tk.END)
            self.hunyuan_entry.insert(0, hunyuan_key)
