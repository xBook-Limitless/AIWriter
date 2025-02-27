import tkinter as tk
from tkinter import ttk, messagebox, Text, Scrollbar
from pathlib import Path
import yaml
import json
import re
import time
import random

class WorldViewPanel(ttk.Frame):
    """世界观构建面板"""
    
    def __init__(self, master):
        super().__init__(master)
        self.config_file = Path("data/configs/novel_structure.yaml")
        self.current_creation_type = ""  # 跟踪当前创作类型
        self.type_specific_panels = {}  # 存储不同类型的特定面板
        self.last_save_time = 0  # 上次保存时间
        self.changes_since_save = False  # 跟踪是否有未保存的更改
        
        # 创建基本界面
        self._create_widgets()
        self._load_config()
        
        # 启动观察者模式，监听配置文件变化
        self.after(1000, self._check_config_changes)
        
        # 启动自动保存
        self.after(10000, self._auto_save)
        
    def _create_widgets(self):
        """创建世界观面板组件"""
        # 创建提示框类
        self._create_tooltip_class()
        
        # 创建主容器框架
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建带滚动条的画布，用于支持滚动
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # 设置滚动区域
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # 创建滚动窗口并添加滚动框架
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 放置滚动区域组件
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 添加鼠标滚轮支持
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 各部分标题样式
        section_font = ("", 12, "bold")
        
        # 1. 核心构建部分 (原_create_base_framework内容)
        ttk.Label(scrollable_frame, text="【核心构建】", font=section_font).pack(anchor="w", padx=10, pady=(10, 5))
        self.base_frame = ttk.Frame(scrollable_frame)
        self.base_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self._create_base_framework()
        
        # 添加分隔线
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', padx=10, pady=10)
        
        # 2. 类型适配部分
        ttk.Label(scrollable_frame, text="【类型强化】", font=section_font).pack(anchor="w", padx=10, pady=(10, 5))
        self.type_frame = ttk.Frame(scrollable_frame)
        self.type_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        # 类型适配内容在update_by_creation_type方法中动态创建
        
        # 添加分隔线
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', padx=10, pady=10)
        
        # 3. 命名系统部分
        ttk.Label(scrollable_frame, text="【命名系统】", font=section_font).pack(anchor="w", padx=10, pady=(10, 5))
        self.naming_frame = ttk.Frame(scrollable_frame)
        self.naming_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self._create_naming_system()
        
        # 添加分隔线
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', padx=10, pady=10)
        
        # 4. 世界观建议部分
        ttk.Label(scrollable_frame, text="【世界观建议】", font=section_font).pack(anchor="w", padx=10, pady=(10, 5))
        self.suggestion_frame = ttk.Frame(scrollable_frame)
        self.suggestion_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self._create_suggestion_system()
        
        # 底部保存按钮和额外的状态信息框
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, pady=10)
        
        # 添加自动保存指示器
        self.autosave_var = tk.StringVar(value="自动保存: 已开启")
        autosave_label = ttk.Label(status_frame, textvariable=self.autosave_var, font=("", 8))
        autosave_label.pack(side=tk.LEFT, padx=10)
        
        # 保存按钮放在右侧
        self.save_button = ttk.Button(status_frame, text="保存世界观设置", command=self._save_config)
        self.save_button.pack(side=tk.RIGHT, padx=10)
    
    def _create_tooltip_class(self):
        """创建Tooltip类"""
        class ToolTip:
            active_tooltips = []  # 类变量，用于跟踪所有活动的提示窗口
            
            def __init__(self, widget, text):
                self.widget = widget
                self.text = text
                self.tooltip = None
                self.timer_id = None  # 用于自动超时
                self.widget.bind("<Enter>", self.show_tooltip)
                self.widget.bind("<Leave>", self.hide_tooltip)
                self.widget.bind("<ButtonPress>", self.hide_tooltip)  # 点击时也隐藏
                
                # 添加窗口销毁事件处理
                self.widget.bind("<Destroy>", self.cleanup)
            
            def show_tooltip(self, event=None):
                try:
                    # 取消任何可能的待处理定时器
                    if self.timer_id:
                        self.widget.after_cancel(self.timer_id)
                        self.timer_id = None
                        
                    # 如果已有提示窗口，先销毁
                    self.hide_tooltip()
                    
                    # 确保widget仍然存在且可见
                    if not self.widget.winfo_exists() or not self.widget.winfo_viewable():
                        return
                        
                    # 获取位置（更安全的方式）
                    try:
                        x, y, _, _ = self.widget.bbox("insert")
                        x += self.widget.winfo_rootx() + 25
                        y += self.widget.winfo_rooty() + 25
                    except:
                        # 对于某些widget可能没有insert索引
                        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
                        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
                    
                    # 创建一个顶级窗口
                    self.tooltip = tk.Toplevel(self.widget)
                    self.tooltip.wm_overrideredirect(True)  # 去掉窗口边框
                    self.tooltip.wm_geometry(f"+{x}+{y}")
                    
                    # 阻止提示窗口获取焦点
                    self.tooltip.wm_attributes("-topmost", 1)
                    
                    label = tk.Label(self.tooltip, text=self.text, justify=tk.LEFT,
                                    background="#ffffcc", relief=tk.SOLID, borderwidth=1,
                                    font=("微软雅黑", 9), wraplength=250)
                    label.pack(padx=3, pady=3)
                    
                    # 添加到活动提示列表
                    ToolTip.active_tooltips.append(self)
                    
                    # 设置自动超时（5秒后自动消失）
                    self.timer_id = self.widget.after(5000, self.hide_tooltip)
                except Exception as e:
                    print(f"显示提示时出错: {str(e)}")
                    self.hide_tooltip()  # 出错时尝试清理
            
            def hide_tooltip(self, event=None):
                try:
                    # 取消任何定时器
                    if self.timer_id:
                        try:
                            self.widget.after_cancel(self.timer_id)
                        except:
                            pass
                        self.timer_id = None
                        
                    # 销毁提示窗口
                    if self.tooltip:
                        try:
                            self.tooltip.destroy()
                        except:
                            pass  # 如果窗口已被销毁，忽略错误
                        self.tooltip = None
                        
                    # 从活动列表中移除
                    if self in ToolTip.active_tooltips:
                        ToolTip.active_tooltips.remove(self)
                except Exception as e:
                    print(f"隐藏提示时出错: {str(e)}")
                    # 确保设置为None
                    self.tooltip = None
                    self.timer_id = None
            
            def cleanup(self, event=None):
                """窗口销毁时清理资源"""
                self.hide_tooltip()
                try:
                    self.widget.unbind("<Enter>")
                    self.widget.unbind("<Leave>")
                    self.widget.unbind("<ButtonPress>")
                    self.widget.unbind("<Destroy>")
                except:
                    pass  # 忽略可能的错误
            
            @classmethod
            def hide_all(cls):
                """隐藏所有活动的提示窗口"""
                for tooltip in list(cls.active_tooltips):
                    tooltip.hide_tooltip()
        
        self.ToolTip = ToolTip
        
        # 为整个应用程序添加全局点击事件，点击任何地方都隐藏所有提示
        self.bind_all("<Button-1>", lambda e: ToolTip.hide_all())
    
    def _create_base_framework(self):
        """创建基础框架（时空维度、社会运行、生命系统）"""
        # 创建一个主容器来使用grid
        main_container = ttk.Frame(self.base_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板 - 时空维度体系
        time_space_frame = ttk.LabelFrame(main_container, text="时空维度体系")
        time_space_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # 时间结构
        time_label = ttk.Label(time_space_frame, text="时间结构:", font=("", 9, "bold"))
        time_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ToolTip(time_label, "决定故事世界中时间的流动方式和结构特点，影响因果关系和事件发展")
        
        self.time_structure = ttk.Combobox(time_space_frame, values=["线性时间", "环形时间", "碎片化时间轴", "多元时间"], width=15)
        self.time_structure.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.time_structure.current(0)
        self.time_structure.bind("<<ComboboxSelected>>", self._register_change)
        self.ToolTip(self.time_structure, "线性时间：传统顺序流动\n环形时间：周期性重复\n碎片化时间轴：非连续性片段\n多元时间：多重并行时间线")
        
        # 空间架构
        space_label = ttk.Label(time_space_frame, text="空间架构:", font=("", 9, "bold"))
        space_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ToolTip(space_label, "决定故事世界的空间组织方式，影响地理环境和世界观范围")
        
        self.space_structure = ttk.Combobox(time_space_frame, values=["单一世界", "多维宇宙", "平行世界", "位面系统"], width=15)
        self.space_structure.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.space_structure.current(0)
        self.space_structure.bind("<<ComboboxSelected>>", self._register_change)
        self.ToolTip(self.space_structure, "单一世界：一个完整连贯的世界\n多维宇宙：多个维度相互关联\n平行世界：多个现实版本并存\n位面系统：不同规则的空间层次")
        
        # 物理法则
        physics_label = ttk.Label(time_space_frame, text="物理法则:", font=("", 9, "bold"))
        physics_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.ToolTip(physics_label, "决定世界中的基本运行规则，影响可能性和限制")
        
        self.physics_rules = ttk.Combobox(time_space_frame, values=["现实物理", "魔法规则", "超能力系统", "科技进化"], width=15)
        self.physics_rules.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.physics_rules.current(0)
        self.physics_rules.bind("<<ComboboxSelected>>", self._register_change)
        self.ToolTip(self.physics_rules, "现实物理：遵循现实世界物理定律\n魔法规则：有确定规则的魔法体系\n超能力系统：特殊个体具备超常能力\n科技进化：科技突破现实限制")
        
        # 物理法则详情
        physics_detail_label = ttk.Label(time_space_frame, text="法则详情:", font=("", 9, "bold"))
        physics_detail_label.grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.ToolTip(physics_detail_label, "对所选物理法则进行详细说明，包括限制、成本和独特点")
        
        self.physics_detail = Text(time_space_frame, width=20, height=5, wrap="word")
        self.physics_detail.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.physics_detail.bind("<KeyRelease>", self._register_change)
        
        # 允许列拉伸
        time_space_frame.columnconfigure(1, weight=1)
        
        # 中间面板 - 社会运行逻辑
        society_frame = ttk.LabelFrame(main_container, text="社会运行逻辑")
        society_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # 权力结构
        power_label = ttk.Label(society_frame, text="权力结构:", font=("", 9, "bold"))
        power_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ToolTip(power_label, "决定社会中权力的分配和运作方式，影响政治冲突和决策过程")
        
        self.power_structure = ttk.Combobox(society_frame, values=["君主制", "共和制", "联邦制", "部落制", "神权制", "寡头制"], width=15)
        self.power_structure.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.power_structure.current(0)
        self.power_structure.bind("<<ComboboxSelected>>", self._register_change)
        self.ToolTip(self.power_structure, "君主制：单一统治者掌权\n共和制：选举产生统治者\n联邦制：多级政府分权\n部落制：基于血缘关系的组织\n神权制：宗教领袖控制\n寡头制：少数精英掌控")
        
        # 经济系统
        economy_label = ttk.Label(society_frame, text="经济系统:", font=("", 9, "bold"))
        economy_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ToolTip(economy_label, "决定社会资源分配和交换方式，影响阶层和财富分布")
        
        self.economy_system = ttk.Combobox(society_frame, values=["自然经济", "商品经济", "灵石体系", "功勋点数", "混合经济"], width=15)
        self.economy_system.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.economy_system.current(0)
        self.economy_system.bind("<<ComboboxSelected>>", self._register_change)
        self.ToolTip(self.economy_system, "自然经济：以物易物\n商品经济：货币交易\n灵石体系：修真世界通用货币\n功勋点数：基于贡献的价值体系\n混合经济：多种体系并存")
        
        # 文化基因
        culture_label = ttk.Label(society_frame, text="文化取向:", font=("", 9, "bold"))
        culture_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.ToolTip(culture_label, "决定社会核心价值观和文化偏好，影响人物行为和社会冲突")
        
        self.culture_orientation = ttk.Combobox(society_frame, values=["尚武", "崇文", "商业", "信仰", "科技", "艺术"], width=15)
        self.culture_orientation.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.culture_orientation.current(0)
        self.culture_orientation.bind("<<ComboboxSelected>>", self._register_change)
        self.ToolTip(self.culture_orientation, "尚武：崇尚武力与勇气\n崇文：重视知识与典籍\n商业：以利益与交易为重\n信仰：以宗教为核心\n科技：崇尚创新与发明\n艺术：推崇美学与表达")
        
        # 社会详情
        society_detail_label = ttk.Label(society_frame, text="社会详情:", font=("", 9, "bold"))
        society_detail_label.grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.ToolTip(society_detail_label, "进一步描述社会结构的细节，包括阶层、制度和特色")
        
        self.society_detail = Text(society_frame, width=20, height=5, wrap="word")
        self.society_detail.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.society_detail.bind("<KeyRelease>", self._register_change)
        
        # 允许列拉伸
        society_frame.columnconfigure(1, weight=1)
        
        # 右侧面板 - 生命系统设计
        life_frame = ttk.LabelFrame(main_container, text="生命系统设计")
        life_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        
        # 种族设定
        race_label = ttk.Label(life_frame, text="种族设定:", font=("", 9, "bold"))
        race_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ToolTip(race_label, "决定世界中存在的智能生命类型及其主导地位")
        
        self.race_setting = ttk.Combobox(life_frame, values=["人类主导", "多种族共存", "非人主导", "人造生命"], width=15)
        self.race_setting.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.race_setting.current(0)
        self.race_setting.bind("<<ComboboxSelected>>", self._register_change)
        self.ToolTip(self.race_setting, "人类主导：以人类为中心\n多种族共存：多种智能生命平等\n非人主导：非人类种族为主导\n人造生命：人造智能或克隆体系")
        
        # 能力体系
        ability_label = ttk.Label(life_frame, text="能力体系:", font=("", 9, "bold"))
        ability_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ToolTip(ability_label, "决定生命体获取和使用超常能力的方式")
        
        self.ability_system = ttk.Combobox(life_frame, values=["武学内功", "仙术法术", "科技改造", "血脉天赋", "职业技能"], width=15)
        self.ability_system.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.ability_system.current(0)
        self.ability_system.bind("<<ComboboxSelected>>", self._register_change)
        self.ToolTip(self.ability_system, "武学内功：通过修炼获得\n仙术法术：操控超自然力量\n科技改造：依靠科技增强\n血脉天赋：与生俱来的能力\n职业技能：特定领域专长")
        
        # 关系网络
        relation_label = ttk.Label(life_frame, text="关系网络:", font=("", 9, "bold"))
        relation_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.ToolTip(relation_label, "决定生命体之间的互动和关系模式")
        
        self.relationship_network = ttk.Combobox(life_frame, values=["共生合作", "竞争对抗", "主仆依存", "血缘宗族"], width=15)
        self.relationship_network.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.relationship_network.current(0)
        self.relationship_network.bind("<<ComboboxSelected>>", self._register_change)
        self.ToolTip(self.relationship_network, "共生合作：互利共赢\n竞争对抗：资源争夺\n主仆依存：等级明确\n血缘宗族：以血脉为纽带")
        
        # 生命系统详情
        life_detail_label = ttk.Label(life_frame, text="生命详情:", font=("", 9, "bold"))
        life_detail_label.grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.ToolTip(life_detail_label, "进一步描述生命系统的特点，包括寿命、进化和特殊能力")
        
        self.life_detail = Text(life_frame, width=20, height=5, wrap="word")
        self.life_detail.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.life_detail.bind("<KeyRelease>", self._register_change)
        
        # 允许列拉伸
        life_frame.columnconfigure(1, weight=1)
        
        # 允许整个容器的列均匀拉伸
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.columnconfigure(2, weight=1)
    
    def _create_naming_system(self):
        """创建优化版命名系统"""
        # 主容器框架（继续使用原来的命名框架）
        naming_container = ttk.Frame(self.naming_frame)
        naming_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ====== 主内容区 - 左侧选择、右侧编辑 ======
        main_frame = ttk.Frame(naming_container)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧 - 命名项目选择区
        select_frame = ttk.LabelFrame(main_frame, text="命名项目")
        select_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5), pady=5, expand=False)
        
        # 使用树形结构组织命名类别和条目
        self.naming_tree = ttk.Treeview(select_frame, selectmode="browse", height=18)
        self.naming_tree.column("#0", width=180)
        self.naming_tree.heading("#0", text="命名类别")
        self.naming_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加滚动条
        tree_scroll = ttk.Scrollbar(select_frame, orient="vertical", command=self.naming_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.naming_tree.configure(yscrollcommand=tree_scroll.set)
        
        # 添加命名类别和条目到树形结构
        naming_categories = {
            "地理命名": ["地名", "地点", "地图", "建筑"],
            "社会命名": ["社会组织", "文化符号", "规则制度"],
            "能力命名": ["境界", "功法", "战斗手段", "修炼体系"],
            "物品命名": ["道具", "外物辅助"],
            "系统命名": ["系统", "金手指"]
        }
        
        # 添加分类和条目
        category_ids = {}  # 存储分类ID
        for category, items in naming_categories.items():
            cat_id = self.naming_tree.insert("", "end", text=category, open=True)
            category_ids[category] = cat_id
            for item in items:
                self.naming_tree.insert(cat_id, "end", text=item, values=(category, item))
        
        # 右侧 - 命名内容编辑区
        edit_frame = ttk.LabelFrame(main_frame, text="命名内容编辑")
        edit_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0), pady=5, expand=True)
        
        # 命名条目标题
        self.naming_title_var = tk.StringVar(value="请在左侧选择命名项目")
        title_label = ttk.Label(edit_frame, textvariable=self.naming_title_var, font=("", 11, "bold"))
        title_label.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # 命名三原则（移至编辑区顶部）
        principles_frame = ttk.Frame(edit_frame, relief="groove", borderwidth=1)
        principles_frame.pack(fill=tk.X, padx=10, pady=5)
        
        principles_text = """【命名三原则】
1. 文化溯源：反映世界背景文化特征，从历史、种族、地理特征提取灵感
2. 语音美感：注重发音节奏与韵律，创造出朗朗上口且符合世界观特色的名称
3. 意义连贯：名称与所指代的事物、角色、地点有内在联系，便于读者记忆"""
        
        principles_label = ttk.Label(principles_frame, text=principles_text, justify=tk.LEFT, 
                                     font=("", 9), wraplength=400, background="#f8f8f8")
        principles_label.pack(padx=5, pady=5, fill=tk.X)
        
        # 命名提示说明
        self.naming_desc_var = tk.StringVar(value="")
        desc_label = ttk.Label(edit_frame, textvariable=self.naming_desc_var, wraplength=400, justify=tk.LEFT)
        desc_label.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 操作按钮区
        btn_frame = ttk.Frame(edit_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 显示示例按钮
        self.example_btn = ttk.Button(btn_frame, text="💡 显示示例", command=self._show_naming_example, state="disabled")
        self.example_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 生成按钮
        self.generate_btn = ttk.Button(btn_frame, text="✨ 生成名称", command=self._generate_naming, state="disabled")
        self.generate_btn.pack(side=tk.LEFT)
        
        # 编辑区
        edit_container = ttk.Frame(edit_frame)
        edit_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 文本编辑区
        self.naming_content = tk.Text(edit_container, height=15, width=40, wrap=tk.WORD)
        self.naming_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.naming_content.bind("<KeyRelease>", self._register_change)
        
        # 滚动条
        content_scroll = ttk.Scrollbar(edit_container, orient="vertical", command=self.naming_content.yview)
        content_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.naming_content.configure(yscrollcommand=content_scroll.set)
        
        # 初始状态下禁用编辑区
        self.naming_content.config(state="disabled")
        
        # 绑定选择事件
        self.naming_tree.bind("<<TreeviewSelect>>", self._on_naming_selection_changed)
        
        # 设置命名项目提示说明
        self.naming_descriptions = {
            "地名": "地名应反映地理环境特点和历史文化背景，是世界观中最基础的空间标识。",
            "地点": "地点名称应当具有鲜明的视觉或功能特征，便于读者形成空间想象。",
            "地图": "世界地图名称反映整体格局和文明范围，通常带有宏大史诗感。",
            "建筑": "建筑名称通常体现其用途和建筑风格，是文明发展水平的重要标志。",
            "社会组织": "组织名称应当反映其宗旨和社会定位，包含权力与等级的暗示。",
            "文化符号": "文化符号是凝聚社会认同的重要元素，通常具有历史渊源和神秘属性。",
            "规则制度": "制度名称体现社会运行的基本准则，应具有庄重感和合法性暗示。",
            "境界": "境界名称应当体现修炼进阶的本质变化，通常涉及存在形态的转变。",
            "功法": "功法名称通常包含核心属性和修炼特点，应富有意象美感。",
            "战斗手段": "战斗技能名称强调视觉效果和实用性，应当动感十足。",
            "修炼体系": "体系名称反映整体修炼路径和理念，包含世界观核心价值观。",
            "道具": "道具名称通常体现其功能和材质特点，应当简洁而印象深刻。",
            "外物辅助": "辅助工具名称应当直观表达用途，通常与主体道具形成体系。",
            "系统": "系统名称需体现核心功能和使用场景，通常具有现代感。",
            "金手指": "特殊能力名称应当简洁而具象化，容易让读者理解其效果。"
        }
        
        # 设置命名示例数据
        self.naming_examples = {
            "地名": ["东海", "西陵", "北冥", "星落原", "碧落山脉", "玄天峰", "沧澜城", "玉京都"],
            "地点": ["天墟城", "龙脊山脉", "碧落湖", "幽冥谷", "星辰海", "九幽渊", "天元谷", "玄武门"],
            "地图": ["九州大陆", "玄天界", "无尽海域", "太虚幻境", "蓬莱仙岛", "万法大陆", "星辰海"],
            "建筑": ["天阙宫", "缥缈峰", "沧海楼", "玄武门", "紫霄宫", "凌霄阁", "青云楼", "星陨塔"],
            "社会组织": ["天机阁", "玄天盟", "紫霄宗", "北斗阁", "青云派", "万剑盟", "丹鼎宗", "龙门"],
            "文化符号": ["玄天令", "上古卷轴", "天机图", "龙纹石", "龙渊剑", "混元珠", "星辰图", "九天符"],
            "规则制度": ["天道规则", "宗门百律", "九品官制", "天罚律", "星辰法典", "仙门条例", "万法宗规"],
            "境界": ["筑基", "金丹", "元婴", "化神", "大乘", "渡劫", "天人", "真仙", "太乙", "大罗"],
            "功法": ["混元功", "太虚剑诀", "九阳神功", "乾坤大挪移", "太极玄功", "紫薇诀", "万象归一"],
            "战斗手段": ["五行遁法", "天罡剑气", "玄阴掌", "乾坤一指", "九龙鞭法", "星辰剑阵", "太虚掌"],
            "修炼体系": ["天地灵气", "仙道修真", "武道极境", "神魂修炼", "内外兼修", "元神淬炼", "天人合一"],
            "道具": ["乾坤袋", "九天神剑", "太虚镜", "紫金葫芦", "混元珠", "星辰石", "玄天尺", "龙骨琴"],
            "外物辅助": ["聚灵阵", "引气符", "御兽铃", "炼丹炉", "天机罗盘", "传音玉简", "遮天符", "追踪石"],
            "系统": ["修仙模拟器", "万界商城", "诸天道藏", "天命系统", "灵境修炼室", "技能融合器"],
            "金手指": ["过目不忘", "时间暂停", "因果推演", "天地感应", "元素亲和", "信息解析", "空间折叠"]
        }
        
        # 命名数据存储
        self.naming_data = {}
        for category, items in naming_categories.items():
            for item in items:
                self.naming_data[item] = ""
        
        # 当前选中项
        self.current_naming_item = None
        self.example_index = 0  # 示例索引，用于循环显示
    
    def _on_naming_selection_changed(self, event=None):
        """处理命名项目选择变化"""
        selected_items = self.naming_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        item_values = self.naming_tree.item(item_id, "values")
        
        # 检查是否选择了条目而非分类
        if item_values:  # 如果有values值，说明是条目
            category = item_values[0]
            item_name = item_values[1]
            
            # 保存当前编辑内容（如果有）
            if self.current_naming_item:
                self.naming_data[self.current_naming_item] = self.naming_content.get("1.0", tk.END).strip()
            
            # 更新当前选中项
            self.current_naming_item = item_name
            
            # 更新界面
            self.naming_title_var.set(f"{category} - {item_name}")
            self.naming_desc_var.set(self.naming_descriptions.get(item_name, ""))
            
            # 启用按钮
            self.example_btn.config(state="normal")
            self.generate_btn.config(state="normal")
            
            # 更新编辑区内容
            self.naming_content.config(state="normal")
            self.naming_content.delete("1.0", tk.END)
            self.naming_content.insert("1.0", self.naming_data.get(item_name, ""))
        else:
            # 如果选择了分类而非条目
            self.naming_title_var.set("请选择具体命名项目")
            self.naming_desc_var.set("")
            
            # 禁用按钮和编辑区
            self.example_btn.config(state="disabled")
            self.generate_btn.config(state="disabled")
            
            self.naming_content.delete("1.0", tk.END)
            self.naming_content.config(state="disabled")
            
            self.current_naming_item = None
    
    def _show_naming_example(self, event=None):
        """显示命名示例"""
        if not self.current_naming_item:
            return
            
        examples = self.naming_examples.get(self.current_naming_item, [])
        if not examples:
            return
            
        # 循环显示示例
        self.example_index = (self.example_index + 1) % len(examples)
        example = examples[self.example_index]
        
        # 更新显示
        self.naming_content.delete("1.0", tk.END)
        self.naming_content.insert("1.0", example)
        
        # 更新数据
        self.naming_data[self.current_naming_item] = example
        
        # 标记有变更
        self._register_change()
    
    def _generate_naming(self, event=None):
        """生成命名内容"""
        if not self.current_naming_item:
            return
        
        # 根据创作类型调整生成风格
        style_adjustments = {
            "严肃小说": "偏向严肃、传统的命名风格",
            "网络小说": "偏向玄幻、奇幻的命名风格",
            "剧本": "偏向戏剧化的命名风格",
            "剧本杀": "偏向悬疑、紧张感的命名风格",
            "游戏剧情": "偏向游戏化、互动感的命名风格"
        }
        
        current_style = style_adjustments.get(self.current_creation_type, "通用命名风格")
        
        # 根据当前项生成3-5个名称
        import random
        examples = self.naming_examples.get(self.current_naming_item, [])
        
        if examples:
            # 随机选择3个不同的例子（如果有足够多的例子）
            count = min(3, len(examples))
            selected = random.sample(examples, count)
            
            # 生成结果
            result = "、".join(selected)
            
            # 更新显示
            self.naming_content.delete("1.0", tk.END)
            self.naming_content.insert("1.0", result)
            
            # 更新数据
            self.naming_data[self.current_naming_item] = result
            
            # 标记有变更
            self._register_change()
            
            # 提示用户
            messagebox.showinfo("命名生成", f"已根据{self.current_creation_type}的{current_style}生成{self.current_naming_item}示例")
    
    def update_by_creation_type(self, creation_type):
        """根据创作类型更新界面内容"""
        self.current_creation_type = creation_type
        
        # 重置类型适配页面
        for widget in self.type_frame.winfo_children():
            widget.destroy()
            
        # 根据创作类型创建对应的类型适配强化面板
        if creation_type == "严肃小说":
            self._create_serious_novel_panel()
        elif creation_type == "网络小说":
            self._create_web_novel_panel()
        elif creation_type == "剧本" or creation_type == "剧本杀":
            self._create_script_panel()
        elif creation_type == "游戏剧情":
            self._create_game_panel()
    
    def _create_serious_novel_panel(self):
        """创建严肃小说的类型适配面板"""
        frame = ttk.Frame(self.type_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 历史真实度验证
        ttk.Label(frame, text="历史真实度:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.history_authenticity = ttk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.history_authenticity.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(frame, text="0%").grid(row=0, column=2, sticky="w")
        
        # 社会矛盾推演
        ttk.Label(frame, text="社会矛盾推演:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.social_conflict = Text(frame, width=40, height=5, wrap="word")
        self.social_conflict.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # 人性探索深度
        ttk.Label(frame, text="人性探索深度:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.humanity_depth = ttk.Combobox(frame, values=["表层冲突", "社会批判", "哲学思辨", "灵魂探索"], width=15)
        self.humanity_depth.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.humanity_depth.current(0)
        
        # 确保可以拉伸
        frame.columnconfigure(1, weight=1)
        
        self.type_specific_panels["严肃小说"] = frame
    
    def _create_web_novel_panel(self):
        """创建网络小说的类型适配面板"""
        frame = ttk.Frame(self.type_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 力量等级量化系统
        ttk.Label(frame, text="力量等级:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        levels_frame = ttk.Frame(frame)
        levels_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        self.power_levels = []
        for i in range(5):
            entry = ttk.Entry(levels_frame, width=10)
            entry.pack(side=tk.LEFT, padx=2)
            self.power_levels.append(entry)
            
            # 默认值
            default_levels = ["凡人", "宗师", "天人", "真仙", "大罗"]
            if i < len(default_levels):
                entry.insert(0, default_levels[i])
        
        # 地图板块
        ttk.Label(frame, text="地图板块:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.map_regions = Text(frame, width=40, height=5, wrap="word")
        self.map_regions.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # 奇遇概率设置
        ttk.Label(frame, text="奇遇类型:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.adventure_types = ttk.Combobox(frame, values=["传承", "秘境", "天材地宝", "机缘巧合", "上古遗迹"], width=15)
        self.adventure_types.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.adventure_types.current(0)
        
        # 确保可以拉伸
        frame.columnconfigure(1, weight=1)
        
        self.type_specific_panels["网络小说"] = frame
    
    def _create_script_panel(self):
        """创建剧本/剧本杀的类型适配面板"""
        frame = ttk.Frame(self.type_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 场景冲突密度
        ttk.Label(frame, text="场景冲突密度:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.conflict_density = ttk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.conflict_density.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(frame, text="0%").grid(row=0, column=2, sticky="w")
        
        # 人物关系图
        ttk.Label(frame, text="人物关系:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.character_relationships = Text(frame, width=40, height=5, wrap="word")
        self.character_relationships.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # 悬念节奏
        ttk.Label(frame, text="悬念节奏:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.suspense_rhythm = ttk.Combobox(frame, values=["缓慢递进", "平稳波动", "急速转折", "高潮迭起"], width=15)
        self.suspense_rhythm.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.suspense_rhythm.current(0)
        
        # 确保可以拉伸
        frame.columnconfigure(1, weight=1)
        
        self.type_specific_panels["剧本"] = frame
        
    def _create_game_panel(self):
        """创建游戏剧情的类型适配面板"""
        frame = ttk.Frame(self.type_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 多线叙事
        ttk.Label(frame, text="叙事线数量:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.narrative_lines = ttk.Spinbox(frame, from_=1, to=10, width=5)
        self.narrative_lines.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.narrative_lines.set(3)
        
        # 玩家选择影响
        ttk.Label(frame, text="玩家选择影响:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.player_choice_impact = ttk.Combobox(frame, values=["剧情分支", "结局变化", "人物关系", "世界状态"], width=15)
        self.player_choice_impact.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.player_choice_impact.current(0)
        
        # 成就系统
        ttk.Label(frame, text="成就系统:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.achievement_system = Text(frame, width=40, height=5, wrap="word")
        self.achievement_system.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # 确保可以拉伸
        frame.columnconfigure(1, weight=1)
        
        self.type_specific_panels["游戏剧情"] = frame
    
    def _create_suggestion_system(self):
        """创建世界观建议系统"""
        # 两列布局
        button_frame = ttk.Frame(self.suggestion_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 左侧加入生成完整世界观按钮
        complete_worldview_frame = ttk.Frame(button_frame)
        complete_worldview_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 添加一个醒目的生成完整世界观按钮
        generate_complete_btn = ttk.Button(
            complete_worldview_frame, 
            text="✨ 一键生成完整世界观 ✨", 
            command=self._generate_complete_worldview,
            style="Accent.TButton"  # 使用强调样式
        )
        generate_complete_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加工具提示
        self.ToolTip(generate_complete_btn, 
                     "基于选定的创作类型和主题，自动生成完整的世界观框架，包括时空维度、社会逻辑、生命系统及命名体系")
        
        # 右侧建议和评估按钮
        button_container = ttk.Frame(button_frame)
        button_container.pack(side=tk.RIGHT)
        
        self.suggest_btn = ttk.Button(button_container, text="生成世界观建议", command=self._generate_suggestions)
        self.suggest_btn.pack(side=tk.LEFT, padx=5)
        
        evaluate_btn = ttk.Button(button_container, text="评估世界观", command=self._evaluate_world_building)
        evaluate_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加建议显示区域
        suggestion_display = ttk.LabelFrame(self.suggestion_frame, text="建议与评估")
        suggestion_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建文本区域显示建议
        self.suggestion_text = tk.Text(suggestion_display, wrap=tk.WORD, height=10, 
                                      font=("微软雅黑", 9),
                                      background="#f8f8f8",
                                      relief=tk.SUNKEN,
                                      borderwidth=1)
        self.suggestion_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 设置只读
        self.suggestion_text.config(state=tk.DISABLED)
    
    def _generate_complete_worldview(self):
        """一键生成完整世界观"""
        # 获取当前创作类型信息
        config_file = Path("data/configs/novel_structure.yaml")
        current_creation_type = ""
        current_main_type = ""
        current_sub_type = ""
        title = ""
        
        try:
            if config_file.exists():
                with open(config_file, "r", encoding='utf-8') as f:
                    all_config = yaml.safe_load(f) or {}
                base_config = all_config.get("base_config", {})
                title = base_config.get("title", "")
                current_creation_type = base_config.get("creation_type", "")
                current_main_type = base_config.get("main_type", "")
                current_sub_type = base_config.get("sub_type", "")
        except Exception as e:
            messagebox.showerror("错误", f"读取配置失败：{str(e)}")
            return
        
        if not current_creation_type or not current_main_type:
            messagebox.showwarning("提示", "请先在基础配置中选择创作类型、主类型和子类型")
            return
        
        # 更新建议区域提示生成正在进行
        self.suggestion_text.config(state=tk.NORMAL)
        self.suggestion_text.delete(1.0, tk.END)
        self.suggestion_text.insert(tk.END, f"正在为《{title or '未命名作品'}》生成完整世界观...\n\n")
        self.suggestion_text.insert(tk.END, f"创作类型: {current_creation_type}\n")
        self.suggestion_text.insert(tk.END, f"主类型: {current_main_type}\n")
        self.suggestion_text.insert(tk.END, f"子类型: {current_sub_type}\n\n")
        self.suggestion_text.insert(tk.END, "AI正在思考中，请稍候...\n")
        self.suggestion_text.config(state=tk.DISABLED)
        self.update_idletasks()  # 立即更新UI
        
        # 开始生成过程
        try:
            # 构建提示词
            prompt = self._build_worldview_prompt(title, current_creation_type, current_main_type, current_sub_type)
            
            # 调用API生成世界观内容
            from core.api_client.deepseek import api_client
            
            # 设置进度提示
            def update_progress(text):
                self.suggestion_text.config(state=tk.NORMAL)
                self.suggestion_text.insert(tk.END, f"{text}\n")
                self.suggestion_text.see(tk.END)
                self.suggestion_text.config(state=tk.DISABLED)
                self.update_idletasks()
            
            # 生成世界观内容
            update_progress("正在生成时空维度体系...")
            
            messages = [
                {"role": "system", "content": "你是世界观构建专家，擅长为不同类型的创作设计完整且协调的世界观框架。"},
                {"role": "user", "content": prompt}
            ]
            
            # 开始生成
            worldview_content = api_client.generate(messages)
            
            # 解析API返回的结果
            worldview_data = self._parse_generated_worldview(worldview_content)
            
            # 更新UI以显示生成结果
            update_progress("✅ 世界观框架已生成!")
            
            # 填充各个字段
            if worldview_data:
                self._fill_worldview_fields(worldview_data)
                update_progress("✅ 已自动填充所有字段!")
                
            # 保存配置
            self._save_config(show_message=False)
            update_progress("✅ 所有设置已保存!")
            
            # 更新建议区域，显示总结
            self.suggestion_text.config(state=tk.NORMAL)
            self.suggestion_text.delete(1.0, tk.END)
            self.suggestion_text.insert(tk.END, "✨ 完整世界观已成功生成 ✨\n\n")
            self.suggestion_text.insert(tk.END, "已为您创建了一个协调一致的世界观框架，包含以下内容：\n")
            self.suggestion_text.insert(tk.END, "• 时空维度体系\n• 社会运行逻辑\n• 生命系统设计\n• 完整命名系统\n\n")
            
            if current_creation_type == "网络小说":
                self.suggestion_text.insert(tk.END, "• 力量体系设计\n• 地图区域划分\n• 奇遇设计\n\n")
            elif current_creation_type == "严肃小说":
                self.suggestion_text.insert(tk.END, "• 主题与哲学\n• 历史背景\n• 社会矛盾\n\n")
            elif current_creation_type == "剧本" or current_creation_type == "剧本杀":
                self.suggestion_text.insert(tk.END, "• 场景设计\n• 情节架构\n• 冲突设计\n\n")
            elif current_creation_type == "游戏剧情":
                self.suggestion_text.insert(tk.END, "• 任务系统\n• 成长路线\n• 世界交互\n\n")
                
            self.suggestion_text.insert(tk.END, "现在您可以根据需要进一步微调每个部分，或者直接使用生成的世界观框架开始创作。\n\n")
            self.suggestion_text.insert(tk.END, "提示：使用\"评估世界观\"功能可以检查世界观的完整性、创新性和一致性。")
            self.suggestion_text.config(state=tk.DISABLED)
            
        except Exception as e:
            # 更新建议区域显示错误
            self.suggestion_text.config(state=tk.NORMAL)
            self.suggestion_text.delete(1.0, tk.END)
            self.suggestion_text.insert(tk.END, f"生成世界观时发生错误：{str(e)}\n\n")
            self.suggestion_text.insert(tk.END, "请检查网络连接或API设置，然后重试。")
            self.suggestion_text.config(state=tk.DISABLED)
            messagebox.showerror("生成失败", f"无法生成完整世界观：{str(e)}")
    
    def _build_worldview_prompt(self, title, creation_type, main_type, sub_type):
        """构建世界观生成提示词"""
        # 基本信息
        basic_info = f"""
        为以下作品创建完整的世界观框架:
        标题: {title or '未命名作品'}
        创作类型: {creation_type}
        主类型: {main_type}
        子类型: {sub_type}
        """
        
        # 根据不同创作类型调整提示词
        type_specific = ""
        if creation_type == "网络小说":
            type_specific = """
            请包含以下内容:
            1. 时空维度体系(时间结构、空间架构、物理法则)
            2. 社会运行逻辑(权力结构、经济系统、文化取向)
            3. 生命系统设计(种族设定、能力体系、关系网络)
            4. 力量体系与等级划分
            5. 地图与区域布局
            6. 世界命名系统(包含地理、社会、能力、物品的命名风格与示例)
            """
        elif creation_type == "严肃小说":
            type_specific = """
            请包含以下内容:
            1. 时空维度体系(时间背景、地理环境、社会规则)
            2. 社会运行逻辑(政治制度、经济形态、文化传统)
            3. 生命系统设计(人物群像、社会阶层、关系网络)
            4. 主题与哲学内涵
            5. 历史背景与社会矛盾
            6. 世界命名系统(包含地点、组织、概念、物品的命名风格与示例)
            """
        elif creation_type == "剧本" or creation_type == "剧本杀":
            type_specific = """
            请包含以下内容:
            1. 时空维度体系(时间背景、场景设置、世界规则)
            2. 社会运行逻辑(权力结构、冲突来源、文化背景)
            3. 角色系统设计(人物类型、关系网络、动机设定)
            4. 情节架构与悬念设计
            5. 场景设计与氛围营造
            6. 世界命名系统(包含场所、组织、关键物品的命名风格与示例)
            """
        elif creation_type == "游戏剧情":
            type_specific = """
            请包含以下内容:
            1. 时空维度体系(游戏时间、空间设计、物理规则)
            2. 社会运行逻辑(阵营体系、经济系统、文化背景)
            3. 生命系统设计(角色类型、能力系统、NPC关系)
            4. 任务系统与世界交互
            5. 成长路线与游戏进程
            6. 世界命名系统(包含地点、阵营、技能、道具的命名风格与示例)
            """
        
        # 输出格式指导
        output_format = """
        请以结构化JSON格式返回，包含以下字段:
        {
          "time_space": {
            "time_structure": "时间结构名称",
            "space_structure": "空间架构名称",
            "physical_laws": "物理法则名称",
            "details": "详细描述..."
          },
          "social_logic": {
            "power_structure": "权力结构名称",
            "economic_system": "经济系统名称",
            "culture_orientation": "文化取向名称",
            "details": "详细描述..."
          },
          "life_system": {
            "race_setting": "种族设定类型",
            "ability_system": "能力体系类型",
            "relationship_network": "关系网络类型",
            "details": "详细描述..."
          },
          "naming_system": {
            "geography": {
              "style": "地理命名风格描述",
              "examples": ["示例1", "示例2", "示例3", "示例4", "示例5"]
            },
            "society": {
              "style": "社会命名风格描述",
              "examples": ["示例1", "示例2", "示例3", "示例4", "示例5"]
            },
            "ability": {
              "style": "能力命名风格描述",
              "examples": ["示例1", "示例2", "示例3", "示例4", "示例5"]
            },
            "item": {
              "style": "物品命名风格描述",
              "examples": ["示例1", "示例2", "示例3", "示例4", "示例5"]
            },
            "system": {
              "style": "系统命名风格描述",
              "examples": ["示例1", "示例2", "示例3", "示例4", "示例5"]
            }
          }
        """
        
        # 根据创作类型添加特殊字段
        if creation_type == "网络小说":
            output_format += """,
          "special": {
            "power_levels": "力量等级体系描述",
            "map_regions": "地图区域描述",
            "adventure_types": "奇遇类型描述"
          }
        }
            """
        elif creation_type == "严肃小说":
            output_format += """,
          "special": {
            "themes": "主题与哲学描述",
            "historical_background": "历史背景描述",
            "social_conflicts": "社会矛盾描述"
          }
        }
            """
        elif creation_type == "剧本" or creation_type == "剧本杀":
            output_format += """,
          "special": {
            "scene_design": "场景设计描述",
            "plot_structure": "情节架构描述",
            "conflict_design": "冲突设计描述"
          }
        }
            """
        elif creation_type == "游戏剧情":
            output_format += """,
          "special": {
            "quest_system": "任务系统描述",
            "growth_path": "成长路线描述",
            "world_interaction": "世界交互描述"
          }
        }
            """
        else:
            output_format += "\n}"
        
        # 组合最终提示词
        final_prompt = f"""
        {basic_info}
        
        {type_specific}
        
        创建一个独特且内部一致的世界观，确保各元素之间相互协调，形成一个连贯的整体。
        
        {output_format}
        
        注意：请确保所有内容风格一致，各部分之间有内在联系，命名系统要符合作品类型特色。
        只返回JSON格式数据，不要添加其他说明。
        """
        
        return final_prompt
    
    def _parse_generated_worldview(self, content):
        """解析生成的世界观内容"""
        try:
            # 尝试从文本中提取JSON部分
            import re
            import json
            
            # 查找JSON内容（处理可能的多行代码块）
            json_match = re.search(r'```(?:json)?(.*?)```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # 如果没有代码块，尝试直接解析全文
                json_str = content.strip()
            
            # 解析JSON
            worldview_data = json.loads(json_str)
            return worldview_data
            
        except Exception as e:
            print(f"解析世界观内容时出错: {str(e)}")
            # 尝试自己构建一个基本结构
            messagebox.showwarning("解析提示", "解析AI回复时遇到问题，将使用基本结构。你可能需要手动调整一些内容。")
            return self._create_basic_worldview_structure()
    
    def _create_basic_worldview_structure(self):
        """创建基本世界观结构"""
        return {
            "time_space": {
                "time_structure": "线性时间",
                "space_structure": "现实世界",
                "physical_laws": "自然规律",
                "details": "基于现实世界的时空体系，遵循自然物理规律。"
            },
            "social_logic": {
                "power_structure": "民主制度",
                "economic_system": "市场经济",
                "culture_orientation": "多元文化",
                "details": "社会结构基于现代民主制度，经济遵循市场规律，文化呈多元化发展趋势。"
            },
            "life_system": {
                "race_setting": "人类社会",
                "ability_system": "现实能力",
                "relationship_network": "社会关系",
                "details": "以人类为主体的生命系统，能力范围在现实限制内，关系网络基于现代社会结构。"
            },
            "naming_system": {
                "geography": {
                    "style": "现代地名风格",
                    "examples": ["青山市", "长河镇", "松林村", "明珠广场", "东方公园"]
                },
                "society": {
                    "style": "现代组织命名",
                    "examples": ["未来科技公司", "青山文化协会", "星光娱乐集团", "先锋教育机构", "绿色环保联盟"]
                },
                "ability": {
                    "style": "职业技能命名",
                    "examples": ["数据分析", "创意设计", "战略规划", "危机管理", "公共演讲"]
                },
                "item": {
                    "style": "现代物品命名",
                    "examples": ["智能助手", "环保材料", "功能饮料", "多用途工具", "便携设备"]
                },
                "system": {
                    "style": "系统化命名",
                    "examples": ["信息管理系统", "资源分配网络", "社会信用体系", "能源循环系统", "防灾预警机制"]
                }
            }
        }
    
    def _fill_worldview_fields(self, data):
        """填充世界观字段"""
        try:
            # 1. 填充时空维度体系
            if "time_space" in data:
                ts = data["time_space"]
                # 设置下拉框
                if hasattr(self, 'time_structure') and ts.get("time_structure"):
                    self.time_structure.set(ts.get("time_structure"))
                if hasattr(self, 'space_structure') and ts.get("space_structure"):
                    self.space_structure.set(ts.get("space_structure"))
                if hasattr(self, 'physical_laws') and ts.get("physical_laws"):
                    self.physical_laws.set(ts.get("physical_laws"))
                # 设置详情文本
                if hasattr(self, 'time_space_details') and ts.get("details"):
                    self.time_space_details.delete(1.0, tk.END)
                    self.time_space_details.insert(1.0, ts.get("details"))
            
            # 2. 填充社会运行逻辑
            if "social_logic" in data:
                sl = data["social_logic"]
                # 设置下拉框
                if hasattr(self, 'power_structure') and sl.get("power_structure"):
                    self.power_structure.set(sl.get("power_structure"))
                if hasattr(self, 'economic_system') and sl.get("economic_system"):
                    self.economic_system.set(sl.get("economic_system"))
                if hasattr(self, 'culture_orientation') and sl.get("culture_orientation"):
                    self.culture_orientation.set(sl.get("culture_orientation"))
                # 设置详情文本
                if hasattr(self, 'social_logic_details') and sl.get("details"):
                    self.social_logic_details.delete(1.0, tk.END)
                    self.social_logic_details.insert(1.0, sl.get("details"))
            
            # 3. 填充生命系统设计
            if "life_system" in data:
                ls = data["life_system"]
                # 设置下拉框
                if hasattr(self, 'race_setting') and ls.get("race_setting"):
                    self.race_setting.set(ls.get("race_setting"))
                if hasattr(self, 'ability_system') and ls.get("ability_system"):
                    self.ability_system.set(ls.get("ability_system"))
                if hasattr(self, 'relationship_network') and ls.get("relationship_network"):
                    self.relationship_network.set(ls.get("relationship_network"))
                # 设置详情文本
                if hasattr(self, 'life_system_details') and ls.get("details"):
                    self.life_system_details.delete(1.0, tk.END)
                    self.life_system_details.insert(1.0, ls.get("details"))
            
            # 4. 填充类型强化部分(如有)
            if "special" in data:
                special = data["special"]
                # 获取当前创作类型
                config_file = Path("data/configs/novel_structure.yaml")
                creation_type = ""
                
                if config_file.exists():
                    with open(config_file, "r", encoding='utf-8') as f:
                        all_config = yaml.safe_load(f) or {}
                    base_config = all_config.get("base_config", {})
                    creation_type = base_config.get("creation_type", "")
                
                # 根据创作类型填充不同字段
                if creation_type == "网络小说":
                    if hasattr(self, 'power_levels_text') and special.get("power_levels"):
                        self.power_levels_text.delete(1.0, tk.END)
                        self.power_levels_text.insert(1.0, special.get("power_levels"))
                    if hasattr(self, 'map_regions_text') and special.get("map_regions"):
                        self.map_regions_text.delete(1.0, tk.END)
                        self.map_regions_text.insert(1.0, special.get("map_regions"))
                    if hasattr(self, 'adventure_types_text') and special.get("adventure_types"):
                        self.adventure_types_text.delete(1.0, tk.END)
                        self.adventure_types_text.insert(1.0, special.get("adventure_types"))
                        
                elif creation_type == "严肃小说":
                    if hasattr(self, 'themes_text') and special.get("themes"):
                        self.themes_text.delete(1.0, tk.END)
                        self.themes_text.insert(1.0, special.get("themes"))
                    if hasattr(self, 'historical_background_text') and special.get("historical_background"):
                        self.historical_background_text.delete(1.0, tk.END)
                        self.historical_background_text.insert(1.0, special.get("historical_background"))
                    if hasattr(self, 'social_conflicts_text') and special.get("social_conflicts"):
                        self.social_conflicts_text.delete(1.0, tk.END)
                        self.social_conflicts_text.insert(1.0, special.get("social_conflicts"))
                
                elif creation_type in ["剧本", "剧本杀"]:
                    if hasattr(self, 'scene_design_text') and special.get("scene_design"):
                        self.scene_design_text.delete(1.0, tk.END)
                        self.scene_design_text.insert(1.0, special.get("scene_design"))
                    if hasattr(self, 'plot_structure_text') and special.get("plot_structure"):
                        self.plot_structure_text.delete(1.0, tk.END)
                        self.plot_structure_text.insert(1.0, special.get("plot_structure"))
                    if hasattr(self, 'conflict_design_text') and special.get("conflict_design"):
                        self.conflict_design_text.delete(1.0, tk.END)
                        self.conflict_design_text.insert(1.0, special.get("conflict_design"))
                
                elif creation_type == "游戏剧情":
                    if hasattr(self, 'quest_system_text') and special.get("quest_system"):
                        self.quest_system_text.delete(1.0, tk.END)
                        self.quest_system_text.insert(1.0, special.get("quest_system"))
                    if hasattr(self, 'growth_path_text') and special.get("growth_path"):
                        self.growth_path_text.delete(1.0, tk.END)
                        self.growth_path_text.insert(1.0, special.get("growth_path"))
                    if hasattr(self, 'world_interaction_text') and special.get("world_interaction"):
                        self.world_interaction_text.delete(1.0, tk.END)
                        self.world_interaction_text.insert(1.0, special.get("world_interaction"))
            
            # 5. 填充命名系统
            if "naming_system" in data:
                ns = data["naming_system"]
                
                # 获取树状结构控件
                if hasattr(self, 'naming_tree'):
                    tree = self.naming_tree
                    
                    # 准备要填充的数据字典(使用与保存/加载配置兼容的格式)
                    naming_data = {}
                    
                    # 处理地理命名
                    if "geography" in ns:
                        geo = ns["geography"]
                        naming_data["geography"] = {
                            "style": geo.get("style", ""),
                            "examples": geo.get("examples", [])
                        }
                        
                    # 处理社会命名
                    if "society" in ns:
                        soc = ns["society"]
                        naming_data["society"] = {
                            "style": soc.get("style", ""),
                            "examples": soc.get("examples", [])
                        }
                        
                    # 处理能力命名
                    if "ability" in ns:
                        ab = ns["ability"]
                        naming_data["ability"] = {
                            "style": ab.get("style", ""),
                            "examples": ab.get("examples", [])
                        }
                        
                    # 处理物品命名
                    if "item" in ns:
                        it = ns["item"]
                        naming_data["item"] = {
                            "style": it.get("style", ""),
                            "examples": it.get("examples", [])
                        }
                        
                    # 处理系统命名
                    if "system" in ns:
                        sys = ns["system"]
                        naming_data["system"] = {
                            "style": sys.get("style", ""),
                            "examples": sys.get("examples", [])
                        }
                    
                    # 更新命名系统数据(与保存格式兼容)
                    self.naming_data = naming_data
                    
                    # 如果树已有选中项，更新编辑区域
                    selected = tree.selection()
                    if selected:
                        self._on_naming_selection_changed()
        
        except Exception as e:
            print(f"填充世界观字段时出错: {str(e)}")
            messagebox.showwarning("填充提示", f"填充部分字段时遇到问题: {str(e)}\n您可能需要手动完善某些内容。")
    
    def _generate_suggestions(self):
        """生成世界观建议"""
        try:
            creation_type = self.current_creation_type
            if not creation_type:
                messagebox.showinfo("提示", "请先在基础配置中选择创作类型")
                return
                
            # 获取当前配置
            with open(self.config_file, "r", encoding='utf-8') as f:
                all_config = yaml.safe_load(f) or {}
            
            base_config = all_config.get("base_config", {})
            main_type = base_config.get("main_type", "")
            sub_type = base_config.get("sub_type", "")
            
            # 根据创作类型生成建议
            suggestions = []
            
            # 基础建议
            suggestions.append(f"【{creation_type}】类型世界观构建建议：")
            suggestions.append("")
            
            if "玄幻" in main_type or "仙侠" in main_type:
                suggestions.append("1. 时空维度：考虑建立分明的修炼境界，每个境界的修炼者对时空的感知和操控能力应有差异")
                suggestions.append("2. 权力体系：可设计多层次宗门/势力结构，形成复杂的政治格局")
                suggestions.append("3. 生命形态：思考普通人与修炼者的共存方式，以及各种神异生物的生态位")
                suggestions.append("4. 能力系统：明确灵气/灵力的获取途径、流通方式和使用限制")
                
            elif "科幻" in main_type or "未来" in sub_type:
                suggestions.append("1. 时空规则：明确您的宇宙是否允许FTL(超光速)旅行，这决定了文明间的联系方式")
                suggestions.append("2. 社会结构：思考技术进步如何重塑社会阶层和政治制度")
                suggestions.append("3. 核心科技：设定1-3项突破性科技，并详细考虑其对社会各层面的影响")
                suggestions.append("4. 文明交互：如果有多文明，考虑它们的技术水平差异和交流模式")
                
            elif "历史" in main_type or "古代" in sub_type:
                suggestions.append("1. 时代背景：明确历史时期和地理范围，参考真实历史文化特征")
                suggestions.append("2. 社会制度：详细设计符合时代特征的政治和阶级制度")
                suggestions.append("3. 文化冲突：设计不同文化群体间的价值观差异和矛盾点")
                suggestions.append("4. 真实性平衡：决定在多大程度上忠于历史，以及在哪些方面进行创造性改编")
                
            elif "剧本" in creation_type or "剧本杀" in creation_type:
                suggestions.append("1. 密闭空间：设计一个地理上或社会上相对封闭的环境，增强角色互动")
                suggestions.append("2. 人物关系网：创建复杂但清晰的人物关系，每个角色都与核心冲突有关联")
                suggestions.append("3. 信息控制：设计信息如何在角色间流动，以及哪些关键信息被刻意隐藏")
                suggestions.append("4. 冲突升级：规划一条冲突逐步升级的路径，创造戏剧性高潮")
            
            elif "游戏" in creation_type:
                suggestions.append("1. 交互规则：明确玩家可以如何影响世界，以及这些影响的边界")
                suggestions.append("2. 成长系统：设计玩家角色的能力进阶路径和奖励机制")
                suggestions.append("3. 探索动机：创造足够的世界之谜和未知区域，激发探索欲")
                suggestions.append("4. 分支结构：设计关键抉择点和多条叙事路径，增强可重玩性")
            
            # 通用建议
            suggestions.append("")
            suggestions.append("通用建议：")
            suggestions.append("1. 确保世界观内部逻辑自洽，避免明显漏洞")
            suggestions.append("2. 为世界增加独特性元素，使其区别于同类作品")
            suggestions.append("3. 创建与主题呼应的符号系统和命名风格")
            suggestions.append("4. 考虑预留未展开的世界区域，为后续发展留下空间")
            
            # 更新建议文本
            self.suggestion_text.delete("1.0", tk.END)
            self.suggestion_text.insert("1.0", "\n".join(suggestions))
            
        except Exception as e:
            messagebox.showerror("错误", f"生成建议失败：{str(e)}")
    
    def _evaluate_world_building(self):
        """评估世界观构建"""
        try:
            # 简单评估世界观各方面的完成度
            world_config = {}
            
            # 读取现有配置
            if self.config_file.exists():
                with open(self.config_file, "r", encoding='utf-8') as f:
                    all_config = yaml.safe_load(f) or {}
                world_config = all_config.get("world_view", {})
            
            if not world_config:
                messagebox.showinfo("提示", "请先保存世界观设置后再进行评估")
                return
                
            # 评估完整性 (核心元素是否都已填写)
            completeness = self._calculate_completeness(world_config)
            completeness_text = f"{completeness}% - " + self._get_rating_text(completeness)
            self.completeness_var.set(completeness_text)
            
            # 评估创新性 (非默认选项的比例)
            innovation = self._calculate_innovation(world_config)
            innovation_text = f"{innovation}% - " + self._get_rating_text(innovation)
            self.innovation_var.set(innovation_text)
            
            # 评估一致性 (相关元素间的匹配度)
            coherence = self._calculate_coherence(world_config)
            coherence_text = f"{coherence}% - " + self._get_rating_text(coherence)
            self.coherence_var.set(coherence_text)
            
            # 使用更友好的对话框显示评估结果
            result = self._create_evaluation_report(completeness, innovation, coherence)
            
            # 创建自定义对话框
            evaluation_window = tk.Toplevel(self)
            evaluation_window.title("世界观评估报告")
            evaluation_window.geometry("500x400")
            evaluation_window.transient(self)  # 设置为模态
            evaluation_window.grab_set()
            
            # 添加报告内容
            ttk.Label(evaluation_window, text="世界观构建评估报告", font=("", 12, "bold")).pack(pady=10)
            
            # 创建带滚动条的文本区域
            report_frame = ttk.Frame(evaluation_window)
            report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            scrollbar = ttk.Scrollbar(report_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            report_text = Text(report_frame, wrap="word", yscrollcommand=scrollbar.set)
            report_text.pack(fill=tk.BOTH, expand=True)
            scrollbar.config(command=report_text.yview)
            
            # 插入报告内容（带格式）
            report_text.insert("1.0", result)
            report_text.config(state="disabled")  # 设为只读
            
            # 关闭按钮
            ttk.Button(evaluation_window, text="确定", command=evaluation_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("错误", f"评估失败：{str(e)}")
    
    def _create_evaluation_report(self, completeness, innovation, coherence):
        """创建详细的评估报告"""
        report = "======= 世界观评估详情 =======\n\n"
        
        # 总体评分
        overall_score = int((completeness + innovation + coherence) / 3)
        report += f"【总体评分】: {overall_score}% - {self._get_rating_text(overall_score)}\n\n"
        
        # 完整性评估
        report += f"【完整性】: {completeness}% - {self._get_rating_text(completeness)}\n"
        if completeness >= 90:
            report += "您的世界观构建非常完整，已经涵盖了所有核心元素。\n"
        elif completeness >= 70:
            report += "您的世界观已经具备了良好的完整性，但仍有一些细节可以补充。\n"
        else:
            report += "您的世界观还不够完整，建议继续补充以下核心设定：\n"
            # 检查缺失的核心元素
            missing = self._find_missing_elements()
            for item in missing:
                report += f"· {item}\n"
        report += "\n"
        
        # 创新性评估
        report += f"【创新性】: {innovation}% - {self._get_rating_text(innovation)}\n"
        if innovation >= 80:
            report += "您的世界观极具创新性，拥有许多独特的设定。\n"
        elif innovation >= 50:
            report += "您的世界观创新度良好，有一些特色设定。\n"
        else:
            report += "您的世界观创新度有限，建议考虑以下几点：\n"
            report += "· 尝试将常见设定进行独特组合\n"
            report += "· 考虑添加一些独特的规则或元素\n"
            report += "· 为现有的传统元素增加创新性解释\n"
        report += "\n"
        
        # 一致性评估
        report += f"【一致性】: {coherence}% - {self._get_rating_text(coherence)}\n"
        if coherence >= 80:
            report += "您的世界观内部非常协调一致，各元素之间逻辑连贯。\n"
        elif coherence >= 60:
            report += "您的世界观基本保持了内部一致性，但有少量潜在冲突。\n"
        else:
            report += "您的世界观存在一些内部冲突，建议关注以下方面：\n"
            conflicts = self._find_potential_conflicts()
            for conflict in conflicts:
                report += f"· {conflict}\n"
        
        return report
    
    def _find_missing_elements(self):
        """查找缺失的核心元素"""
        missing = []
        
        try:
            # 读取现有配置
            if self.config_file.exists():
                with open(self.config_file, "r", encoding='utf-8') as f:
                    all_config = yaml.safe_load(f) or {}
                world_config = all_config.get("world_view", {})
                
                # 检查时空元素
                if "time_space" not in world_config or not world_config["time_space"].get("time_structure"):
                    missing.append("时间结构设定")
                if "time_space" not in world_config or not world_config["time_space"].get("space_structure"):
                    missing.append("空间架构设定")
                if "time_space" not in world_config or not world_config["time_space"].get("physics_rules"):
                    missing.append("物理法则设定")
                    
                # 检查社会元素
                if "society" not in world_config or not world_config["society"].get("power_structure"):
                    missing.append("社会权力结构")
                if "society" not in world_config or not world_config["society"].get("economy_system"):
                    missing.append("经济系统设定")
                if "society" not in world_config or not world_config["society"].get("culture_orientation"):
                    missing.append("文化基因取向")
                    
                # 检查生命系统
                if "life_system" not in world_config or not world_config["life_system"].get("race_setting"):
                    missing.append("种族设定")
                if "life_system" not in world_config or not world_config["life_system"].get("ability_system"):
                    missing.append("能力体系")
        except Exception:
            # 如果出错，返回一个通用的建议
            missing = ["基本时空设定", "社会结构设定", "生命系统设定"]
            
        return missing
    
    def _find_potential_conflicts(self):
        """查找潜在的内部冲突"""
        conflicts = []
        
        try:
            # 读取现有配置
            if self.config_file.exists():
                with open(self.config_file, "r", encoding='utf-8') as f:
                    all_config = yaml.safe_load(f) or {}
                world_config = all_config.get("world_view", {})
                
                if "time_space" in world_config and "life_system" in world_config:
                    ts = world_config["time_space"]
                    ls = world_config["life_system"]
                    
                    # 检查物理法则与能力体系的冲突
                    if ts.get("physics_rules") == "现实物理" and ls.get("ability_system") in ["仙术法术", "武学内功"]:
                        conflicts.append("现实物理法则与超自然能力体系的冲突")
                    
                    # 检查空间架构与种族设定的冲突
                    if ts.get("space_structure") == "位面系统" and ls.get("race_setting") == "人类主导":
                        conflicts.append("位面系统通常包含多种生命形式，与人类主导设定存在潜在冲突")
                
                # 检查经济系统与权力结构
                if "society" in world_config:
                    soc = world_config["society"]
                    
                    # 检查经济与权力结构的冲突
                    if soc.get("economy_system") == "功勋点数" and soc.get("power_structure") == "君主制":
                        conflicts.append("功勋点数经济体系与传统君主制权力结构可能不太匹配")
                        
                    # 检查文化与权力结构的冲突
                    if soc.get("culture_orientation") == "商业" and soc.get("power_structure") == "神权制":
                        conflicts.append("商业文化取向与神权制权力结构之间的价值观冲突")
        except Exception:
            # 如果出错，返回一个通用的可能冲突
            conflicts = ["不同设定元素之间可能存在的逻辑冲突", "建议重新审视各主要设定之间的关系"]
            
        return conflicts if conflicts else ["未发现明显冲突，但建议继续完善设定间的逻辑关系"]
    
    def _auto_save(self):
        """自动保存功能"""
        try:
            # 检查是否有未保存的更改且距离上次保存超过30秒
            current_time = time.time()
            if self.changes_since_save and (current_time - self.last_save_time) > 30:
                self._save_config(show_message=False)
                self.last_save_time = current_time
                self.changes_since_save = False
                self.autosave_var.set("自动保存: 已保存")
            
            # 继续下一轮自动保存检查
            self.after(10000, self._auto_save)
        except Exception as e:
            print(f"自动保存出错: {str(e)}")
            self.after(10000, self._auto_save)  # 即使出错也继续检查
    
    def _save_config(self, show_message=True):
        """从UI组件中收集数据并保存到文件"""
        try:
            # 读取现有配置
            if self.config_file.exists():
                with open(self.config_file, "r", encoding='utf-8') as f:
                    all_config = yaml.safe_load(f) or {}
            else:
                all_config = {}
            
            # 构建世界观配置
            world_config = {}
            
            # 时空维度数据
            world_config["time_space"] = {
                "time_structure": self.time_structure.get(),
                "space_structure": self.space_structure.get(),
                "physics_rules": self.physics_rules.get(),
                "physics_detail": self.physics_detail.get("1.0", tk.END).strip()
            }
            
            # 社会运行逻辑数据
            world_config["society"] = {
                "power_structure": self.power_structure.get(),
                "economy_system": self.economy_system.get(),
                "culture_orientation": self.culture_orientation.get(),
                "society_detail": self.society_detail.get("1.0", tk.END).strip()
            }
            
            # 生命系统数据
            world_config["life_system"] = {
                "race_setting": self.race_setting.get(),
                "ability_system": self.ability_system.get(),
                "relationship_network": self.relationship_network.get(),
                "life_detail": self.life_detail.get("1.0", tk.END).strip()
            }
            
            # 命名系统数据 - 更新为新的存储方式
            naming_config = {}
            
            # 保存当前编辑的内容
            if self.current_naming_item:
                self.naming_data[self.current_naming_item] = self.naming_content.get("1.0", tk.END).strip()
            
            # 将命名数据按类别整理
            naming_categories = {
                "地理命名": ["地名", "地点", "地图", "建筑"],
                "社会命名": ["社会组织", "文化符号", "规则制度"],
                "能力命名": ["境界", "功法", "战斗手段", "修炼体系"],
                "物品命名": ["道具", "外物辅助"],
                "系统命名": ["系统", "金手指"]
            }
            
            # 按照类别组织数据
            for category, items in naming_categories.items():
                category_key = category.lower().replace("命名", "")
                naming_config[category_key] = {}
                for item in items:
                    naming_config[category_key][item] = self.naming_data.get(item, "")
            
            world_config["naming"] = naming_config
            
            # 类型特定配置
            if self.current_creation_type and self.current_creation_type in self.type_specific_panels:
                type_config = {}
                
                if self.current_creation_type == "严肃小说":
                    type_config["history_authenticity"] = self.history_authenticity.get()
                    type_config["social_conflict"] = self.social_conflict.get("1.0", tk.END).strip()
                    type_config["humanity_depth"] = self.humanity_depth.get()
                
                elif self.current_creation_type == "网络小说":
                    power_levels = [entry.get() for entry in self.power_levels]
                    type_config["power_levels"] = power_levels
                    type_config["map_regions"] = self.map_regions.get("1.0", tk.END).strip()
                    type_config["adventure_types"] = self.adventure_types.get()
                
                elif self.current_creation_type in ["剧本", "剧本杀"]:
                    type_config["conflict_density"] = self.conflict_density.get()
                    type_config["character_relationships"] = self.character_relationships.get("1.0", tk.END).strip()
                    type_config["suspense_rhythm"] = self.suspense_rhythm.get()
                
                elif self.current_creation_type == "游戏剧情":
                    type_config["narrative_lines"] = self.narrative_lines.get()
                    type_config["player_choice_impact"] = self.player_choice_impact.get()
                    type_config["achievement_system"] = self.achievement_system.get("1.0", tk.END).strip()
                
                world_config["type_specific"] = type_config
            
            # 更新配置
            all_config["world_view"] = world_config
            
            # 保存到文件
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding='utf-8') as f:
                yaml.dump(all_config, f, allow_unicode=True, sort_keys=False)
            
            # 更新状态
            self.last_save_time = time.time()
            self.changes_since_save = False
            self.autosave_var.set("自动保存: 已保存")
            
            if show_message:
                messagebox.showinfo("成功", "世界观设置已保存")
            
        except Exception as e:
            self.autosave_var.set("自动保存: 出错")
            if show_message:
                messagebox.showerror("错误", f"保存世界观配置失败：{str(e)}")
    
    def _register_change(self, event=None):
        """注册UI变化"""
        self.changes_since_save = True
        self.autosave_var.set("自动保存: 有未保存更改")
    
    def _load_config(self):
        """从YAML文件中加载世界观配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding='utf-8') as f:
                    all_config = yaml.safe_load(f) or {}
                
                # 获取基础配置信息
                base_config = all_config.get("base_config", {})
                creation_type = base_config.get("creation_type", "")
                
                if creation_type:
                    self.update_by_creation_type(creation_type)
                
                # 获取世界观配置
                world_config = all_config.get("world_view", {})
                if world_config:
                    # 加载时空维度数据
                    if "time_space" in world_config:
                        ts = world_config["time_space"]
                        if "time_structure" in ts:
                            self.time_structure.set(ts["time_structure"])
                        if "space_structure" in ts:
                            self.space_structure.set(ts["space_structure"])
                        if "physics_rules" in ts:
                            self.physics_rules.set(ts["physics_rules"])
                        if "physics_detail" in ts:
                            self.physics_detail.delete("1.0", tk.END)
                            self.physics_detail.insert("1.0", ts["physics_detail"])
                    
                    # 加载社会运行逻辑数据
                    if "society" in world_config:
                        soc = world_config["society"]
                        if "power_structure" in soc:
                            self.power_structure.set(soc["power_structure"])
                        if "economy_system" in soc:
                            self.economy_system.set(soc["economy_system"])
                        if "culture_orientation" in soc:
                            self.culture_orientation.set(soc["culture_orientation"])
                        if "society_detail" in soc:
                            self.society_detail.delete("1.0", tk.END)
                            self.society_detail.insert("1.0", soc["society_detail"])
                    
                    # 加载生命系统数据
                    if "life_system" in world_config:
                        ls = world_config["life_system"]
                        if "race_setting" in ls:
                            self.race_setting.set(ls["race_setting"])
                        if "ability_system" in ls:
                            self.ability_system.set(ls["ability_system"])
                        if "relationship_network" in ls:
                            self.relationship_network.set(ls["relationship_network"])
                        if "life_detail" in ls:
                            self.life_detail.delete("1.0", tk.END)
                            self.life_detail.insert("1.0", ls["life_detail"])
                    
                    # 加载命名系统数据 - 新的数据结构
                    if "naming" in world_config:
                        naming_data = world_config["naming"]
                        
                        # 清空当前数据
                        self.naming_data = {}
                        
                        # 定义类别映射关系
                        categories = {
                            "地理": ["地名", "地点", "地图", "建筑"],
                            "社会": ["社会组织", "文化符号", "规则制度"],
                            "能力": ["境界", "功法", "战斗手段", "修炼体系"],
                            "物品": ["道具", "外物辅助"],
                            "系统": ["系统", "金手指"]
                        }
                        
                        # 加载数据
                        for category_key, category_data in naming_data.items():
                            for category, items in categories.items():
                                if category_key == category.lower():
                                    for item_name, item_value in category_data.items():
                                        if item_name in items:
                                            self.naming_data[item_name] = item_value
                
                    # 类型特定配置数据已在update_by_creation_type中处理
            
            except Exception as e:
                messagebox.showerror("错误", f"加载世界观配置失败：{str(e)}")
    
    def _check_config_changes(self):
        """定期检查配置文件变化，更新界面"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding='utf-8') as f:
                    all_config = yaml.safe_load(f) or {}
                
                base_config = all_config.get("base_config", {})
                creation_type = base_config.get("creation_type", "")
                
                # 如果创作类型发生变化
                if creation_type and creation_type != self.current_creation_type:
                    self.update_by_creation_type(creation_type)
        except Exception as e:
            # 静默处理异常，不打断用户体验
            print(f"配置文件检查错误: {str(e)}")
            
        # 继续下一轮检查
        self.after(2000, self._check_config_changes)
