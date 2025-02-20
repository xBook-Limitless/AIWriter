import tkinter as tk
from tkinter import ttk
import yaml
from pathlib import Path
from tkinter import messagebox

class BaseConfiguration(ttk.Frame):
    """作品基础配置面板"""
    
    CREATION_TYPES = {
        "小说": {
            "主类型": ["玄幻", "科幻", "机甲", "仙侠", "诸天"],
            "子类型": {
                "玄幻": ["东方玄幻", "异世大陆", "高武世界", "王朝争霸"],
                "科幻": ["星际文明", "未来世界", "时空穿梭"],
                "机甲": ["古武机甲", "末世危机", "超级科技", "进化变异"],
                "仙侠": ["修真文明", "幻想修真", "现代修真", "古典仙侠", "神话修真"],
                "诸天": ["无限流", "诸天万界", "综漫穿越"]
            }
        },
        "剧本": {
            "主类型": ["电影剧本", "电视剧本", "舞台剧本"],
            "子类型": {
                "电影剧本": ["动作", "喜剧", "悬疑", "科幻"],
                "电视剧本": ["都市", "古装", "谍战", "家庭伦理"],
                "舞台剧本": ["话剧", "音乐剧", "实验剧"]
            }
        },
        "剧本杀": {
            "主类型": ["盒装", "独家", "城限"],
            "子类型": {
                "盒装": ["推理", "情感", "机制", "恐怖"],
                "独家": ["大型演绎", "沉浸式", "实景"],
                "城限": ["阵营对抗", "跑团", "解谜"]
            }
        },
        "游戏剧情": {
            "主类型": ["RPG", "AVG", "开放世界"],
            "子类型": {
                "RPG": ["日式", "美式", "沙盒"],
                "AVG": ["文字冒险", "视觉小说", "互动电影"],
                "开放世界": ["都市", "奇幻", "科幻"]
            }
        }
    }

    def __init__(self, master):
        super().__init__(master)
        self.config_file = Path("data/configs/novel_structure.yaml")
        self._create_widgets()
        self._load_config()

    def _create_widgets(self):
        """创建界面组件"""
        # 创建带边框的容器
        frame = ttk.LabelFrame(self, text="基础设置", width=400, height=220)
        frame.pack_propagate(False)  # 固定容器大小
        frame.pack(side=tk.LEFT, anchor='nw', padx=0, pady=0, fill=tk.NONE, expand=False)

        # 作品名称
        ttk.Label(frame, text="作品名称：").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.title_entry = ttk.Entry(frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")  # 取消合并列

        # 创作类型
        ttk.Label(frame, text="创作类型：").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.creation_type = ttk.Combobox(frame, values=list(self.CREATION_TYPES.keys()), 
                                        state="readonly", width=27)
        self.creation_type.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.creation_type.bind("<<ComboboxSelected>>", self._update_main_types)

        # 主类型
        ttk.Label(frame, text="主类型：").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.main_type = ttk.Combobox(frame, state="readonly", width=27)
        self.main_type.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.main_type.bind("<<ComboboxSelected>>", self._update_sub_types)

        # 子类型
        ttk.Label(frame, text="子类型：").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.sub_type = ttk.Combobox(frame, state="readonly", width=27)
        self.sub_type.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # 按钮容器
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        # 保存按钮
        ttk.Button(btn_frame, text="保存配置", command=self._save_config).pack(side=tk.LEFT, padx=5)
        # 新增导入按钮
        ttk.Button(btn_frame, text="导入配置", command=self._import_config).pack(side=tk.LEFT, padx=5)

    def _update_main_types(self, event=None):
        """更新主类型选项"""
        selected = self.creation_type.get()
        if selected:
            main_types = self.CREATION_TYPES[selected]["主类型"]
            self.main_type["values"] = main_types
            # 自动选择第一个选项并触发子类型更新
            if main_types:
                self.main_type.set(main_types[0])
                self._update_sub_types()

    def _update_sub_types(self, event=None):
        """更新子类型选项"""
        creation = self.creation_type.get()
        main_type = self.main_type.get()
        if creation and main_type:
            sub_types = self.CREATION_TYPES[creation]["子类型"][main_type]
            self.sub_type["values"] = sub_types
            # 自动选择第一个选项
            if sub_types:
                self.sub_type.set(sub_types[0])

    def _load_config(self):
        """加载已有配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding='utf-8') as f:
                    all_config = yaml.safe_load(f) or {}
                config = all_config.get("base_config", {})
                
                self.title_entry.insert(0, config.get("title", ""))
                self.creation_type.set(config.get("creation_type", ""))
                self._update_main_types()
                self.main_type.set(config.get("main_type", ""))
                self._update_sub_types()
                self.sub_type.set(config.get("sub_type", ""))
            except Exception as e:
                messagebox.showerror("错误", f"加载配置失败：{str(e)}")

    def _save_config(self):
        """保存配置到文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding='utf-8') as f:
                    all_config = yaml.safe_load(f) or {}
            else:
                all_config = {}

            # 调整字段顺序，title放在第一个
            all_config["base_config"] = {
                "title": self.title_entry.get(),  # 第一行
                "creation_type": self.creation_type.get(),
                "main_type": self.main_type.get(),
                "sub_type": self.sub_type.get()
            }

            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, "w", encoding='utf-8') as f:
                yaml.dump(all_config, f, allow_unicode=True, sort_keys=False)  # 禁止自动排序
            messagebox.showinfo("成功", "配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")

    def _import_config(self):
        """导入配置文件"""
        try:
            with open(self.config_file, "r", encoding='utf-8') as f:
                all_config = yaml.safe_load(f) or {}
            config = all_config.get("base_config", {})
            
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, config.get("title", ""))
            self.creation_type.set(config.get("creation_type", ""))
            self._update_main_types()
            self.main_type.set(config.get("main_type", ""))
            self._update_sub_types()
            self.sub_type.set(config.get("sub_type", ""))
            messagebox.showinfo("成功", "配置已导入")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败：{str(e)}")
