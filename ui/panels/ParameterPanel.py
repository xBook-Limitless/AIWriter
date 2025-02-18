import tkinter as tk
from tkinter import Toplevel, Label, ttk
from modules.GlobalModule import global_config
from utils.config_loader import get_version_info, load_config, save_config
from tkinter import messagebox

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

class ParameterPanel(ttk.Labelframe):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.style = ttk.Style()
        self.style.configure('TLabelframe.Label', font=('微软雅黑', 10, 'bold'))
        self.preset_configs = self._load_presets()  # 先加载预设
        self.response_formats = ["text", "json_object"]
        self._create_model_selector()  # 创建模型选择器
        self.create_widgets()  # 最后创建控件
        
    def _load_presets(self):
        return {
             '自定义': {},
        '法律合同审核': {
            'temperature': 0.0,
            'top_p': 0.1,
            'frequency_penalty': 1.2,
            'presence_penalty': 1.0,
            'max_tokens': 6000
        },
        '医疗报告分析': {
            'temperature': 0.0,
            'top_p': 0.1,
            'frequency_penalty': 0.8,
            'presence_penalty': 0.7,
            'max_tokens': 2000
        },
        '代码生成/数学解题': {
            'temperature': 0.0,
            'top_p': 0.1,
            'frequency_penalty': 0.5,
            'presence_penalty': 0.3,
            'max_tokens': 4096
        },
        '产品说明书': {
            'temperature': 0.1,
            'top_p': 0.2,
            'frequency_penalty': 0.9,
            'presence_penalty': 0.8,
            'max_tokens': 3000
        },
        '法律文书撰写': {
            'temperature': 0.1,
            'top_p': 0.2,
            'frequency_penalty': 0.9,
            'presence_penalty': 0.8,
            'max_tokens': 5000
        },
        '科研数据分析': {
            'temperature': 0.1,
            'top_p': 0.2,
            'frequency_penalty': 0.9,
            'presence_penalty': 0.8,
            'max_tokens': 4000
        },
        '技术文档编写': {
            'temperature': 0.2,
            'top_p': 0.3,
            'frequency_penalty': 0.8,
            'presence_penalty': 0.6,
            'max_tokens': 4000
        },
        '金融分析报告': {
            'temperature': 0.2,
            'top_p': 0.3,
            'frequency_penalty': 0.7,
            'presence_penalty': 0.6,
            'max_tokens': 5000
        },
        '新闻写作': {
            'temperature': 0.3,
            'top_p': 0.4,
            'frequency_penalty': 0.8,
            'presence_penalty': 0.7,
            'max_tokens': 1200
        },
        '学术摘要生成': {
            'temperature': 0.3,
            'top_p': 0.4,
            'frequency_penalty': 0.6,
            'presence_penalty': 0.5,
            'max_tokens': 500
        },
        '翻译': {
            'temperature': 0.3,
            'top_p': 0.8,
            'frequency_penalty': 1.0,
            'presence_penalty': 0.5,
            'max_tokens': 2000
        },
        '心理咨询对话': {
            'temperature': 0.4,
            'top_p': 0.7,
            'frequency_penalty': 0.1,
            'presence_penalty': 0.0,
            'max_tokens': 1200
        },
        '学术论文写作': {
            'temperature': 0.4,
            'top_p': 0.7,
            'frequency_penalty': 0.6,
            'presence_penalty': 0.4,
            'max_tokens': 6000
        },
        '商业计划书': {
            'temperature': 0.5,
            'top_p': 0.6,
            'frequency_penalty': 0.4,
            'presence_penalty': 0.3,
            'max_tokens': 3000
        },
        '教育辅导': {
            'temperature': 0.6,
            'top_p': 0.8,
            'frequency_penalty': 0.3,
            'presence_penalty': 0.2,
            'max_tokens': 1500
        },
        '通用对话': {
            'temperature': 0.7,
            'top_p': 0.9,
            'frequency_penalty': 0.2,
            'presence_penalty': 0.1,
            'max_tokens': 1024
        },
        '食谱生成': {
            'temperature': 0.8,
            'top_p': 0.6,
            'frequency_penalty': 0.3,
            'presence_penalty': 0.2,
            'max_tokens': 1000
        },
        '市场营销文案': {
            'temperature': 0.9,
            'top_p': 0.6,
            'frequency_penalty': 0.2,
            'presence_penalty': 0.1,
            'max_tokens': 1000
        },
        '数据抽取/分析': {
            'temperature': 1.0,
            'top_p': 0.5,
            'frequency_penalty': 0.7,
            'presence_penalty': 0.5,
            'max_tokens': 2048
        },
        '短篇小说创作': {
            'temperature': 1.0,
            'top_p': 0.7,
            'frequency_penalty': -0.2,
            'presence_penalty': 0.0,
            'max_tokens': 1500
        },
        '游戏NPC对话': {
            'temperature': 1.0,
            'top_p': 0.8,
            'frequency_penalty': -0.5,
            'presence_penalty': -0.2,
            'max_tokens': 300
        },
        '儿童故事创作': {
            'temperature': 1.1,
            'top_p': 0.7,
            'frequency_penalty': -0.4,
            'presence_penalty': -0.3,
            'max_tokens': 800
        },
        '社交媒体文案': {
            'temperature': 1.2,
            'top_p': 0.95,
            'frequency_penalty': -0.3,
            'presence_penalty': -0.2,
            'max_tokens': 280
        },
        '长篇小说创作': {
            'temperature': 1.2,
            'top_p': 0.85,
            'frequency_penalty': -0.4,
            'presence_penalty': -0.2,
            'max_tokens': 8192
        },
        '游戏剧情生成': {
            'temperature': 1.3,
            'top_p': 0.85,
            'frequency_penalty': -0.7,
            'presence_penalty': -0.5,
            'max_tokens': 3000
        },
        '剧本创作': {
            'temperature': 1.4,
            'top_p': 0.9,
            'frequency_penalty': -0.6,
            'presence_penalty': -0.4,
            'max_tokens': 2500
        },
        '脱口秀脚本': {
            'temperature': 1.5,
            'top_p': 0.95,
            'frequency_penalty': -1.2,
            'presence_penalty': -0.7,
            'max_tokens': 800
        },
        '创意类写作/诗歌创作': {
            'temperature': 1.5,
            'top_p': 1.0,
            'frequency_penalty': -0.5,
            'presence_penalty': -0.3,
            'max_tokens': 2000
        },
        '诗歌生成': {
            'temperature': 1.5,
            'top_p': 1.0,
            'frequency_penalty': -1.0,
            'presence_penalty': -0.8,
            'max_tokens': 500
        }
    }

    def create_widgets(self):
        self._create_preset_selector()
        self._create_temperature_control()
        self._create_top_p_control()
        self._create_penalty_controls()
        self._create_max_tokens()
        self._create_response_format()
        self._create_stream_switch()
        self._create_api_key_management()
        self._setup_layout()

    def _create_preset_selector(self):
        """创建预设场景选择控件"""
        # 标签布局参数：
        # row=1: 第二行（模型选择下方）
        # column=0: 第一列
        # sticky='ew': 水平拉伸
        # padx=20: 左侧间距
        preset_label = ttk.Label(self, text="预设场景:")
        preset_label.grid(row=1, column=0, sticky='ew', padx=20)
        
        # 新增预设标签提示
        self._add_tooltip(preset_label, 
            "选择预置参数组合\n自动设置下方参数"
        )
        
        # 初始化预设选择框
        self.preset_combo = ttk.Combobox(
            self,
            values=list(self.preset_configs.keys()),  # 使用预设配置的键名
            state="readonly",    # 只读模式
            height=10,           # 下拉列表显示20项
            width=18,            # 宽度与模型选择器一致
            font=('微软雅黑', 10)  # 指定字体
        )
        self.preset_combo.current(0)  # 默认选中第一个选项
        
        # 网格布局参数：
        # row=1: 第二行
        # column=1: 第二列
        # sticky='ew': 水平拉伸
        # padx=5: 右侧间距
        self.preset_combo.grid(row=1, column=1, sticky='ew', padx=5)
        
        # 绑定预设选择事件
        self.preset_combo.bind("<<ComboboxSelected>>", self._apply_preset)

    def _create_temperature_control(self):
        # 温度控件
        temp_label = ttk.Label(self, text="温度 (0.0-1.5):", anchor='w')
        temp_label.grid(row=2, column=0, sticky='ew', padx=20)
        # 温度标签提示
        self._add_tooltip(temp_label, 
            "控制生成随机性\n0.0-严谨准确\n1.0-富有创意"
        )
        self.temp_value = ttk.Label(self)
        self.temp_value.config(width=6, anchor='center')
        self.temp_slider = ttk.Scale(
            self, 
            from_=0.0, 
            to=1.5, 
            command=self._update_temp,
            length=200
        )
        self.temp_slider.set(global_config.generation_param.temperature)
        self.temp_slider.grid(row=2, column=1, sticky='', padx=5)

    def _update_temp(self, value):
        val = float(value)
        global_config.generation_param.temperature = val
        self.temp_value.config(text=f"{val:.1f}")

    def _create_top_p_control(self):
        """创建核心采样率控件"""
        top_p_label = ttk.Label(self, text="核心采样率 (0-1):", anchor='w')
        top_p_label.grid(row=3, column=0, sticky='ew', padx=20)
        # top_p标签提示
        self._add_tooltip(top_p_label,
            "控制采样范围\n0.1-仅考虑前10%可能\n1.0-考虑所有可能"
        )
        self.top_p_value = ttk.Label(self, text=f"{global_config.generation_param.top_p:.2f}")
        self.top_p_value.grid(row=3, column=2, padx=5)
        
        self.top_p_slider = ttk.Scale(
            self, 
            from_=0.0, 
            to=1.0,
            length=200,
            command=lambda v: [
                setattr(global_config.generation_param, 'top_p', float(v)),
                self.top_p_value.config(text=f"{float(v):.2f}")
            ]
        )
        self.top_p_slider.set(global_config.generation_param.top_p)
        self.top_p_slider.grid(row=3, column=1, sticky='', padx=5)

    def _create_penalty_controls(self):
        """创建惩罚系数相关控件"""
        # 频率惩罚
        freq_label = ttk.Label(self, text="重复惩罚 (-2.0-2.0):", anchor='w')
        freq_label.grid(row=4, column=0, sticky='ew', padx=20)
        self._add_tooltip(freq_label,
            "惩罚重复内容\n正值减少重复\n负值增加重复"
        )
        self.freq_penalty_value = ttk.Label(self, text=f"{global_config.generation_param.frequency_penalty:.1f}")
        self.freq_penalty_value.grid(row=4, column=2, padx=5)
        
        self.freq_penalty_slider = ttk.Scale(
            self,
            from_=-2.0,
            to=2.0,
            length=200,
            command=lambda v: [
                setattr(global_config.generation_param, 'frequency_penalty', float(v)),
                self.freq_penalty_value.config(text=f"{float(v):.1f}")
            ]
        )
        self.freq_penalty_slider.set(global_config.generation_param.frequency_penalty)
        self.freq_penalty_slider.grid(row=4, column=1, sticky='', padx=5)

        # 存在惩罚
        pres_label = ttk.Label(self, text="存在惩罚 (-2.0-2.0):", anchor='w')
        pres_label.grid(row=5, column=0, sticky='ew', padx=20)
        self._add_tooltip(pres_label,
            "惩罚已存在内容\n正值避免重复提及\n负值鼓励重复提及"
        )
        self.pres_penalty_value = ttk.Label(self, text=f"{global_config.generation_param.presence_penalty:.1f}")
        self.pres_penalty_value.grid(row=5, column=2, padx=5)
        
        self.pres_penalty_slider = ttk.Scale(
            self,
            from_=-2.0,
            to=2.0,
            length=200,
            command=lambda v: [
                setattr(global_config.generation_param, 'presence_penalty', float(v)),
                self.pres_penalty_value.config(text=f"{float(v):.1f}")
            ]
        )
        self.pres_penalty_slider.set(global_config.generation_param.presence_penalty)
        self.pres_penalty_slider.grid(row=5, column=1, sticky='', padx=5)

    def _create_max_tokens(self):
        """创建最大Token数输入控件"""
        # 标签布局
        max_token_label = ttk.Label(self, text="最大生成Token数:", anchor='w')
        max_token_label.grid(row=6, column=0, sticky='ew', padx=20)
        # Token数标签提示
        self._add_tooltip(max_token_label,
            "控制单次生成的最大长度\n建议值：不超过上下文窗口的80%\n当前模型窗口：{}".format(
                global_config.model_config.context_window
            )
        )
        
        # 范围提示标签
        ttk.Label(self, text="(1-8192)").grid(
            row=6, column=2, 
            sticky=tk.W
        )
        
        # 初始化Spinbox控件
        self.max_tokens_spin = ttk.Spinbox(
            self,
            from_=1,         # 最小值
            to=8192,         # 最大值
            increment=100,   # 步长
            validate='key',  # 启用键盘输入验证
            validatecommand=(self.register(self._validate_max_tokens), '%P')
        )
        
        # 设置初始值
        self.max_tokens_spin.set(global_config.generation_param.max_tokens)
        
        # 绑定焦点离开事件：确保输入值合法
        self.max_tokens_spin.bind("<FocusOut>", self._update_max_tokens)
        
        # 网格布局
        self.max_tokens_spin.grid(row=6, column=1, padx=5, sticky=tk.EW)

    def _create_response_format(self):
        """创建响应格式控件"""
        format_label = ttk.Label(self, text="响应格式:", anchor='w')
        format_label.grid(row=7, column=0, sticky='ew', padx=20, pady=(5, 0))
        
        # 响应格式标签提示
        self._add_tooltip(format_label,
            "设置返回格式\ntext-纯文本\njson_object-结构化JSON"
        )
        self.format_combo = ttk.Combobox(
            self,
            values=self.response_formats,
            state="readonly",
            width=10
        )
        self.format_combo.set(global_config.generation_param.response_format.get("type", "text"))
        self.format_combo.grid(row=7, column=1, sticky=tk.W, padx=5, pady=(5, 0))
        self.format_combo.bind("<<ComboboxSelected>>", self._update_response_format)

    def _update_response_format(self, event):
        selected = self.format_combo.get()
        global_config.generation_param.response_format = {"type": selected}

    def _create_stream_switch(self):
        """创建流式生成开关"""
        self.stream_var = tk.BooleanVar(value=global_config.generation_param.stream)
        self.stream_check = ttk.Checkbutton(
            self,
            text=" 启用流式生成",
            variable=self.stream_var,
            command=lambda: setattr(global_config.generation_param, 'stream', self.stream_var.get()),
            compound='left'
        )
        self.stream_check.grid(row=8, column=0, columnspan=3, sticky=tk.W, padx=20, pady=5)
        self._add_tooltip(self.stream_check, "实时逐字输出模式\n适合长文本但增加资源消耗")

    def _validate_max_tokens(self, new_value):
        """验证最大Token数输入"""
        if not new_value.isdigit():
            return False
        value = int(new_value)
        return 1 <= value <= 8192

    def _update_max_tokens(self, event):
        """更新最大Token数到全局配置"""
        try:
            value = int(self.max_tokens_spin.get())
            safe_value = max(1, min(value, 8192))
            global_config.generation_param.max_tokens = safe_value
            self.max_tokens_spin.set(safe_value)
        except ValueError:
            self.max_tokens_spin.set(global_config.generation_param.max_tokens)

    def _apply_preset(self, event):
        """应用预设配置"""
        preset_name = self.preset_combo.get()
        config = self.preset_configs.get(preset_name, {})
        
        if not config:
            return
        
        for param, value in config.items():
            if hasattr(global_config.generation_param, param):
                setattr(global_config.generation_param, param, value)
                
                # 更新各个控件
                if param == 'temperature':
                    self.temp_slider.set(value)
                elif param == 'top_p':
                    self.top_p_slider.set(value)
                elif param == 'frequency_penalty':
                    self.freq_penalty_slider.set(value)
                elif param == 'presence_penalty':
                    self.pres_penalty_slider.set(value)
                elif param == 'max_tokens':
                    safe_value = max(1, min(value, 8192))  # 确保不超过全局限制
                    self.max_tokens_spin.set(safe_value)
                    global_config.generation_param.max_tokens = safe_value
        
        self.update_idletasks()

    def _setup_layout(self):
        # 列配置
        self.columnconfigure(0, weight=0, minsize=120, pad=20)
        self.columnconfigure(1, weight=0, minsize=200)
        self.columnconfigure(2, weight=0, minsize=60)

    def _add_tooltip(self, widget, text):
        tooltip = Tooltip(widget, text)  # 需要确保Tooltip类可用

    def _create_model_selector(self):
        """创建模型选择控件"""
        # 从model_config.yaml直接加载模型配置
        model_config = load_config('model_config.yaml') or {}
        # 提取配置文件中models字典的所有键作为模型列表
        model_list = list(model_config.get('models', {}).keys())

        # 创建标签
        model_label = ttk.Label(self, text="AI模型:")
        model_label.grid(row=0, column=0, sticky='w', padx=20)
        # 将提示移到标签
        self._add_tooltip(model_label, 
            "选择要使用的AI模型\n配置来源：model_config.yaml"
        )
        
        # 初始化下拉选择框
        self.model_combo = ttk.Combobox(
            self,
            values=model_list,  # 使用配置文件的原始键名
            state="readonly",    # 禁止直接输入
            width=18             # 固定宽度为18字符
        )
        
        # 设置默认选中项逻辑：
        # 1. 尝试从user_config.yaml获取已保存的选择
        # 2. 如果不存在则选择第一个可用模型
        # 3. 如果没有模型则显示空字符串
        user_config = load_config('user_config.yaml') or {}
        default_model = user_config.get(
            'selected_model', 
            model_list[0] if model_list else ""
        )
        self.model_combo.set(default_model)
        
        # 网格布局参数说明：
        # row=0: 首行
        # column=1: 第二列
        # sticky='ew': 水平拉伸填充
        # padx=5: 水平间距
        # pady=5: 垂直间距
        self.model_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # 绑定选择事件：当用户选择新模型时触发_update_model方法
        self.model_combo.bind("<<ComboboxSelected>>", self._update_model)

    def _update_model(self, event):
        """
        处理模型选择更新事件
        参数说明：
        - event: tkinter事件对象（此处未直接使用）
        """
        # 获取用户选择的模型键名
        selected = self.model_combo.get()
        
        # 保存配置逻辑：
        # 直接覆盖user_config.yaml的selected_model字段
        # 保留其他可能存在的配置项
        save_config('user_config.yaml', {'selected_model': selected})
        
        # 通知全局配置更新
        # 注意：global_config.update_model需自行处理键名到配置的映射
        # 使用正确的配置对象
        if hasattr(global_config, 'update_model'):
            global_config.update_model(selected)
        else:
            # 兼容旧版本配置对象
            global_config.model_config.update_model(selected)

    def _create_api_key_management(self):
        """新增API密钥管理板块"""
        key_frame = ttk.Labelframe(self, text="用户认证管理")
        
        # 用户令牌输入
        ttk.Label(key_frame, text="用户令牌:").grid(row=0, column=0, padx=5)
        self.user_token_entry = ttk.Entry(key_frame, show="*", width=30)
        self.user_token_entry.grid(row=0, column=1, padx=5)
        ttk.Button(key_frame, text="刷新令牌", 
                  command=self._refresh_user_token).grid(row=0, column=2)
        
        # 状态指示灯
        self.token_status = ttk.Label(key_frame, text="●", foreground="gray")
        self.token_status.grid(row=0, column=3, padx=5)
        
        key_frame.grid(row=9, column=0, columnspan=3, sticky="ew", pady=5)
        self._add_tooltip(key_frame, "管理API访问凭证\n令牌有效期为1小时")

    def _refresh_user_token(self):
        """生成新的JWT令牌"""
        try:
            from modules.AuthModule import generate_jwt_token
            new_token = generate_jwt_token(self._get_device_id())
            self.user_token_entry.delete(0, tk.END)
            self.user_token_entry.insert(0, new_token)
            self._update_token_status(True)
        except Exception as e:
            self._update_token_status(False)
            messagebox.showerror("令牌生成错误", str(e))

    def _get_device_id(self):
        """获取设备唯一标识"""
        import hashlib, uuid
        return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()

    def _update_token_status(self, valid: bool):
        """更新令牌状态指示"""
        color = "green" if valid else "red"
        self.token_status.config(foreground=color)
        # 3秒后恢复灰色
        self.after(3000, lambda: self.token_status.config(foreground="gray")) 
