import tkinter as tk
from tkinter import ttk
import yaml
from pathlib import Path
from tkinter import messagebox
from ui.panels.RoleConfiguration import RoleConfiguration

class BaseConfiguration(ttk.Frame):
    """作品基础配置面板"""
    
    CREATION_TYPES = {
        "严肃小说": {
            "主类型": ["现实主义文学", "历史小说", "社会派小说", "纯文学", "传记文学"],
            "子类型": {
                "现实主义文学": ["乡土文学", "都市生活", "工业题材", "军旅生活"],
                "历史小说": ["古代历史", "近代风云", "历史传记", "历史架空"],
                "社会派小说": ["社会批判", "人性探索", "伦理困境", "政治寓言"],
                "纯文学": ["实验文学", "意识流", "诗化小说", "元小说"],
                "传记文学": ["人物传记", "回忆录", "口述历史", "家族史诗"]
            }
        },
        "网络小说": {
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
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.NONE, expand=False, anchor=tk.NW)  # 完全禁止扩展

        # 基础属性框（宽度调整为原0.8倍）
        base_width = int(320 * 0.8)  # 原320→256
        base_frame = ttk.LabelFrame(main_frame, text="基础属性", width=base_width, height=300)
        base_frame.pack_propagate(False)
        base_frame.pack(side=tk.LEFT, padx=5, pady=5, anchor=tk.NW, fill=tk.NONE, expand=False)

        # 角色设定框（保持固定尺寸）
        role_frame = ttk.LabelFrame(main_frame, text="角色设定", width=720, height=295)
        role_frame.pack_propagate(False)
        role_frame.pack(side=tk.LEFT, padx=5, pady=5, anchor=tk.NW, fill=tk.NONE, expand=False)

        # 调整基础属性框内部组件宽度
        ttk.Label(base_frame, text="作品名称:").grid(row=0, column=0, padx=5, pady=5, sticky="e")  # 缩小间距
        self.title_entry = ttk.Entry(base_frame, width=22)  # 原22→18
        self.title_entry.grid(row=0, column=1, padx=5, pady=3, sticky="w")

        # 创作类型
        ttk.Label(base_frame, text="创作类型:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.creation_type = ttk.Combobox(base_frame, values=list(self.CREATION_TYPES.keys()), 
                                        state="readonly", width=20)
        self.creation_type.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.creation_type.bind("<<ComboboxSelected>>", self._update_main_types)

        # 主类型
        ttk.Label(base_frame, text="主类型:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.main_type = ttk.Combobox(base_frame, state="readonly", width=20)
        self.main_type.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.main_type.bind("<<ComboboxSelected>>", self._update_sub_types)

        # 子类型
        ttk.Label(base_frame, text="子类型:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.sub_type = ttk.Combobox(base_frame, state="readonly", width=20)
        self.sub_type.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # 按钮容器
        btn_frame = ttk.Frame(base_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        # 保存按钮
        ttk.Button(btn_frame, text="保存属性", command=self._save_config).pack(side=tk.LEFT, padx=5)

        # 角色配置组件
        self.role_config = RoleConfiguration(role_frame)
        self.role_config.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _update_main_types(self, event=None):
        """更新主类型选项"""
        selected = self.creation_type.get()
        if selected:
            main_types = self.CREATION_TYPES[selected]["主类型"]
            self.main_type["values"] = main_types
            # 触发角色配置更新
            self.role_config.update_by_creation_type(selected)
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
            
            # 通知世界观面板更新
            creation_type = self.creation_type.get()
            # 如果在同一个窗口层级有世界观面板，可以直接触发更新
            world_view_panel = self._find_world_view_panel()
            if world_view_panel:
                world_view_panel.update_by_creation_type(creation_type)
                
            messagebox.showinfo("成功", "基础属性已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")
            
    def _find_world_view_panel(self):
        """查找世界观面板实例"""
        try:
            # 尝试在应用程序中查找WorldViewPanel实例
            parent = self.winfo_toplevel()
            
            # 递归查找特定类型的组件
            def find_panel(widget):
                from ui.panels.WorldView import WorldViewPanel
                if isinstance(widget, WorldViewPanel):
                    return widget
                    
                for child in widget.winfo_children():
                    result = find_panel(child)
                    if result:
                        return result
                return None
                
            return find_panel(parent)
        except Exception as e:
            print(f"查找世界观面板出错: {str(e)}")
            return None
