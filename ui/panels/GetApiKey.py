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
        self._center_window()  # 窗口居中
        self._create_widgets()
        self._load_saved_key()
        
    def _center_window(self):
        """使窗口居中显示"""
        self.parent.update_idletasks()
        width = 400
        height = 150
        x = (self.parent.winfo_screenwidth() // 2) - (width // 2)
        y = (self.parent.winfo_screenheight() // 2) - (height // 2)
        self.parent.geometry(f'{width}x{height}+{x}+{y}')

    def _load_saved_key(self):
        """加载已保存的密钥"""
        from utils.config_loader import get_api_key
        saved_key = get_api_key().get("api_key", "")
        if saved_key:
            self.api_key_entry.insert(0, saved_key)

    def _create_widgets(self):
        """创建简化版输入界面"""
        main_frame = ttk.Frame(self)
        
        # 输入区域
        input_frame = ttk.Frame(main_frame)
        ttk.Label(input_frame, text="API密钥:").pack(side=tk.LEFT)
        self.api_key_entry = ttk.Entry(input_frame, show="*", width=40)
        self.api_key_entry.pack(side=tk.LEFT, padx=5)
        input_frame.pack(pady=10)

        # 单一操作按钮
        ttk.Button(
            main_frame, 
            text="验证并保存", 
            command=self._test_and_save
        ).pack(pady=5)

        # 文字状态提示
        self.status_label = ttk.Label(main_frame, text="", foreground="gray")
        self.status_label.pack()

        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

    def _test_and_save(self):
        """静默验证并保存"""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            self._update_status("请输入有效的API密钥", "red")
            return

        try:
            # 测试连接
            response = httpx.get(
                f"{global_config.model_config.base_url}/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5
            )
            response.raise_for_status()
            
            # 保存密钥
            self._save_api_key(api_key)
            self._update_status("验证成功，密钥已保存", "green")
            
        except httpx.HTTPStatusError as e:
            self._update_status(f"验证失败: HTTP {e.response.status_code}", "red")
        except Exception as e:
            self._update_status(f"连接错误: {str(e)}", "red")

    def _save_api_key(self, api_key: str):
        """无长度验证的保存方法"""
        try:
            from utils.config_loader import save_api_key
            save_api_key({"api_key": api_key})
        except Exception as e:
            messagebox.showerror("保存失败", str(e))
            raise

    def _update_status(self, text: str, color: str = "black"):
        """更新状态文字"""
        self.status_label.config(text=text, foreground=color)
        self.after(3000, lambda: self.status_label.config(text="", foreground="gray"))
