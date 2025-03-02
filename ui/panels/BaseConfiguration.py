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
            "主类型": ["现实主义文学", "历史小说", "社会派小说", "纯文学", "传记文学", "战争文学", "心理小说"],
            "子类型": {
                "现实主义文学": ["乡土文学", "都市生活", "工业史诗", "军旅风云", "移民叙事", "阶层浮沉"],
                "历史小说": ["古代正史", "近代变革", "历史人物传", "战争史诗", "历史推理"],
                "社会派小说": ["体制批判", "人性实验室", "伦理困局", "政治隐喻", "犯罪镜像"],
                "纯文学": ["叙事实验", "意识之流", "诗性文本", "元小说", "存在主义", "魔幻写实"],
                "传记文学": ["虚构传记", "回忆重构", "口述档案", "家族秘史", "知识分子史"],
                "战争文学": ["战场纪实", "创伤记忆", "反战寓言", "军事谋略", "战後重建"],
                "心理小说": ["精神剖析", "情感拓扑", "记忆迷宮", "人格实验", "病态美学"]
            }
        },
        "网络小说": {
            "主类型": ["玄幻", "科幻", "仙侠", "诸天", "奇幻", "都市", "洪荒", "系统"],
            "子类型": {
                "玄幻": ["东方玄幻", "异世大陆", "高武世界", "王朝争霸"],
                "科幻": ["星际文明", "未来世界", "时空穿梭", "古武机甲", "末世危机", "超级科技", "进化变异"],
                "仙侠": ["修真文明", "幻想修真", "现代修真", "古典仙侠", "神话修真"],
                "诸天": ["无限流", "诸天万界", "综漫穿越"],
                "奇幻": ["历史神话", "西方奇幻", "史诗奇幻", "黑暗奇幻", "现代魔法", "剑与魔法", "魔法学院", "血统冒险", "异界传说", "另类幻想", "龙与地下城"],
                "都市": ["都市生活", "都市异能", "商战职场", "娱乐明星", "校园青春", "社会乡土", "侦探推理", "美食旅游", "重生逆袭", "神医兵王", "鉴宝收藏"],
                "洪荒": ["洪荒流", "上古神话", "混沌初开", "巫妖大战", "封神演义", "洪荒人族", "神话大罗", "鸿蒙大道", "重生洪荒", "西游封神"],
                "系统": ["任务奖励流", "加点升级流", "职业系统流", "幕后黑手流", "气运掠夺流", "躺平变强流", "多系统冲突", "反系统觉醒"]
            }
        },
        "剧本": {
            "主类型": ["电影剧本", "电视剧本", "舞台剧本", "动画剧本", "互动剧本"],
            "子类型": {
                "电影剧本": ["文艺片", "黑色电影", "公路片", "政治隐喻", "暴力美学", "赛博朋克", "社会寓言", "文献纪录片"],
                "电视剧本": ["单元剧", "年代戏", "职业剧", "悬疑推理", "女性成长", "黑色幽默", "末世废土", "平行时空"],
                "舞台剧本": ["沉浸式戏剧", "环境戏剧", "文献剧", "解构经典", "肢体剧场", "政治剧", "残酷戏剧", "教育剧场"],
                "动画剧本": ["成人动画", "机甲战斗", "治愈系", "妖怪异闻", "科幻寓言", "蒸汽朋克", "赛璐璐艺术", "独立动画"],
                "互动剧本": ["多线叙事游戏", "真人互动剧", "ARG现实游戏", "AI生成剧本", "分支电影", "虚拟现实戏剧", "跨媒体叙事", "元剧本实验"]
            }
        },
        "剧本杀": {
            "主类型": ["盒装", "独家", "城限", "线上本", "跨界联名"],
            "子类型": {
                "盒装": ["硬核推理", "情感沉浸", "机制博弈", "恐怖惊悚", "欢乐撕逼", "社会派", "儿童向"],
                "独家": ["全息剧场", "多线实景", "NPC互动剧", "电影级演绎", "环境机关", "AR增强", "暴风雪山庄"],
                "城限": ["阵营权谋", "TRPG跑团", "密码学解谜", "多结局抉择", "生存竞技", "艺术解构", "历史重演"],
                "线上本": ["语音推理", "视频搜证", "AI主持人", "虚拟场景", "异步剧本", "元宇宙剧场", "直播互动"],
                "跨界联名": ["IP衍生", "文旅实景", "品牌定制", "教育实训", "学术推演", "公益宣传", "艺术展览"]
            }
        },
        "游戏剧情": {
            "主类型": ["角色扮演(RPG)", "叙事冒险(AVG)", "沉浸模拟", "互动叙事", "开放叙事", "实验性叙事"],
            "子类型": {
                "角色扮演(RPG)": ["日式王道", "美式CRPG", "武侠修仙", "赛博朋克", "克苏鲁神话", "魂系碎片化"],
                "叙事冒险(AVG)": ["文字推理", "视觉小说", "交互式电影", "恐怖解谜", "历史重构", "生存抉择"],
                "沉浸模拟": ["环境叙事", "物件考古", "AI生态", "多视角叙事", "动态世界", "伦理困境"],
                "互动叙事": ["分支宇宙", "元游戏叙事", "玩家共创", "实时演化", "人格影响", "多媒介叙事"],
                "开放叙事": ["网状任务", "文明演进", "生态模拟", "随机事件流", "NPC人生", "文明冲突"],
                "实验性叙事": ["时间悖论", "维度穿越", "意识入侵", "叙事解构", "情感算法", "后设游戏"]
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

    def register_type_callback(self, callback):
        """注册创作类型变更的回调函数"""
        # 先保存回调函数
        self.type_callbacks = getattr(self, 'type_callbacks', [])
        self.type_callbacks.append(callback)
        
        # 为创作类型下拉框添加事件绑定
        self.creation_type.bind("<<ComboboxSelected>>", self._on_type_changed)

    def _on_type_changed(self, event=None):
        """处理创作类型变更事件"""
        # 只更新界面，不保存配置
        self._update_main_types()
        
        # 调用所有注册的回调函数
        for callback in getattr(self, 'type_callbacks', []):
            try:
                callback()
            except Exception as e:
                print(f"回调函数执行错误：{str(e)}")
    
    def get_creation_type(self):
        """获取当前选择的创作类型"""
        return self.creation_type.get()
