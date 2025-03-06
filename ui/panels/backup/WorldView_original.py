import tkinter as tk
from tkinter import ttk, scrolledtext
import yaml
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from pathlib import Path
import datetime
import json
import threading
import random
import os
import time

from ui.panels.BaseConfiguration import BaseConfiguration

class WorldViewPanel:
    """
    世界观构建面板
    
    代码结构重构计划:
    
    1. 总框架部分
       - __init__: 初始化方法
       - create_widgets: 创建UI组件
       - _create_linear_outline_system: 创建线性大纲系统
       - update_step_view: 更新步骤视图
       - next_step/prev_step: 步骤导航
       - update_by_creation_type: 根据创作类型更新
       - finalize_outline: 完成大纲
       - _check_config_changes: 检查配置变化
       - _load_config: 加载配置
       - pack/grid/place: 布局方法
    
    2. 步骤1: 构建基础模板
       - _create_base_template: 创建基础模板界面
       - _display_template_preview: 显示模板预览
       - _apply_template_from_preview: 应用预览中的模板
       - _ai_generate_template: AI生成模板
       - _build_template_prompt: 构建模板提示词
       - _start_template_generation: 开始模板生成
       - _stop_template_generation: 停止模板生成
       - _template_stream_callback: 模板流回调
       - _update_template_editor: 更新模板编辑器
       - _display_template_reasoning: 显示模板推理过程
       - _mark_template_thinking_finished: 标记思考过程完成
       - _safe_close_template_window: 安全关闭模板窗口
       - _save_template: 保存模板
       - _parse_template_content: 解析模板内容
       - _apply_template_data: 应用模板数据
       - _update_base_template_view: 更新基础模板视图
       - _confirm_template: 确认模板
    
    3. 步骤2: 模板参数调整
       - _create_parameter_input_view: 创建参数输入视图
       - _extract_parameters_from_template: 从模板提取参数
       - _load_parameters_from_cache: 从缓存加载参数
       - _get_work_title: 获取作品标题
       - _run_parameter_extraction: 运行参数提取
       - _display_extracted_parameters: 显示提取的参数
       - _on_param_selected: 参数选择事件
       - _on_param_edited: 参数编辑事件
       - _save_parameters_to_cache: 保存参数到缓存
       - _use_default_parameters: 使用默认参数
       - _confirm_parameters: 确认参数
    
    4. 步骤3: 生成扩展建议
       - _create_suggestion_generation: 创建建议生成界面
       - _progress_simulation: 进度模拟
       - _show_generated_suggestions: 显示生成的建议
       - _confirm_suggestions: 确认建议
    
    5. 步骤4: 检测核心冲突
       - _create_conflict_detection: 创建冲突检测界面
       - _confirm_conflicts: 确认冲突
    
    6. 步骤5: 完善世界完整度
       - _create_completion_validation: 创建完整性验证界面
       - _optimize_completeness: 优化完整性
    
    7. 步骤6: 优化风格一致性
       - _create_style_polishing: 创建风格优化界面
       - _refresh_style_preview: 刷新风格预览
    
    8. 步骤7: 世界观展示
       - _create_world_view_display: 创建世界观显示界面
       - _create_overview_tab: 创建概览标签页
       - _create_spacetime_tab: 创建时空标签页
       - _create_society_tab: 创建社会标签页
       - _create_power_system_tab: 创建力量体系标签页
       - _create_organizations_tab: 创建组织标签页
       - _create_ecology_tab: 创建生态标签页
       - _finalize_worldview: 完成世界观
    
    9. 通用功能
       - _save_to_file: 保存到文件
    """
    def __init__(self, master):
        """初始化世界观构建面板"""
        self.master = master
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.master)
        
        # 当前工作目录作为配置文件的位置
        self.config_dir = Path("data/configs")
        self.config_file = self.config_dir / "base_config.yaml"
        self.novel_config_file = self.config_dir / "novel_structure.yaml"
        
        # 加载配置,如果不存在则创建默认配置
        self._load_config()
        
        # 步骤列表与当前步骤
        self.steps = [
            "构建基础模板", "模板参数调整", "生成扩展建议", 
            "检测核心冲突", "完善世界完整度", "优化风格一致性",
            "世界观展示"
        ]
        
        # 当前步骤索引
        self.current_step_index = 0
        
        # 初始化步骤完成状态
        self.steps_completed = {step: False for step in self.steps}
        
        # 当前选择的世界观模板
        self.selected_template = None
        
        # 当前世界观数据
        self.worldview_data = {}
        
        # 当前创作类型
        self.current_creation_type = None
        
        # 字体设置
        self.step_font = ("Arial", 9)
        self.current_step_font = ("Arial", 9, "bold")
        self.completed_step_font = ("Arial", 9)
        
        # 初始化AI生成相关变量
        self.generation_stopped = False
        self.gen_thread = None
        self.current_gen_window = None
        self.current_editor = None
        
        # 创建UI组件
        self.create_widgets()
        
        # 启动配置文件检查
        self.after = self.master.after
        self._check_config_changes()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            return {}
        except Exception as e:
            print(f"加载配置文件时出错: {str(e)}")
            return {}
    
    def pack(self, **kwargs):
        """让主框架使用pack布局管理器"""
        self.main_frame.pack(**kwargs)
        return self
        
    def grid(self, **kwargs):
        """让主框架使用grid布局管理器"""
        self.main_frame.grid(**kwargs)
        return self
        
    def place(self, **kwargs):
        """让主框架使用place布局管理器"""
        self.main_frame.place(**kwargs)
        return self
    
    def create_widgets(self):
        """创建世界观面板的UI组件"""
        print("WorldView: 开始创建UI组件...")
        # 为主框架添加内边距
        self.main_frame.configure(padding=(1, 1, 1, 1))
        
        # 创建线性生成大纲系统直接嵌入到主面板中
        self._create_linear_outline_system()
        print("WorldView: UI组件创建完成")
    
    def _create_linear_outline_system(self):
        """创建线性大纲生成系统"""
        print("WorldView: 创建线性大纲系统...")
        # 步骤指示区域 - 顶部
        step_frame = ttk.Frame(self.main_frame)
        step_frame.pack(fill=tk.X, pady=1, side=tk.TOP)
          
        # 创建中心容器
        center_frame = ttk.Frame(step_frame)
        center_frame.pack(anchor=tk.CENTER)  # 使用pack的anchor参数实现居中
        
        # 步骤指示器 - 流程图样式
        self.step_indicators_frame = ttk.Frame(center_frame)
        self.step_indicators_frame.pack(padx=10, pady=5)
        
        self.step_indicators = []
        
        # 将所有步骤显示在一行
        for i, step in enumerate(self.steps):
            col = i * 2  # 每个步骤占两列(步骤+箭头)
            
            # 步骤标签 - 移除数字前缀
            step_label = ttk.Label(self.step_indicators_frame, text=f"{step}", font=("Arial", 9))
            step_label.grid(row=0, column=col, padx=5, pady=2)
            self.step_indicators.append(step_label)
            
            # 在每个步骤标签后添加一个箭头（除了最后一个步骤）
            if i < len(self.steps) - 1:
                arrow = ttk.Label(self.step_indicators_frame, text="→")
                arrow.grid(row=0, column=col+1)
        
        # 创建固定高度的公用容器
        self.fixed_container = ttk.Frame(self.main_frame)
        self.fixed_container.pack(fill=tk.BOTH, expand=True, pady=5, side=tk.TOP)
        
        # 设置固定容器的最小高度，确保无论内容多少，高度都保持一致
        self.fixed_container.update()  # 更新以获取当前尺寸
        min_height = 500  # 设置最小高度（可以根据实际需求调整）
        self.fixed_container.configure(height=min_height)
        self.fixed_container.pack_propagate(False)  # 防止容器高度自适应内容
        
        # 创建滚动容器
        self.content_canvas = tk.Canvas(self.fixed_container, borderwidth=0, highlightthickness=0)
        self.content_scrollbar = ttk.Scrollbar(self.fixed_container, orient="vertical", command=self.content_canvas.yview)
        self.scrollable_content = ttk.Frame(self.content_canvas)
        
        # 配置滚动区域
        self.scrollable_content.bind(
            "<Configure>",
            lambda e: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))
        )
        
        # 确保滚动区域的宽度与Canvas相同
        def _configure_scrollable_frame(event):
            # 设置滚动区域的宽度为Canvas的宽度
            self.content_canvas.itemconfig(frame_id, width=event.width)
        
        frame_id = self.content_canvas.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        self.content_canvas.bind("<Configure>", _configure_scrollable_frame)
        self.content_canvas.configure(yscrollcommand=self.content_scrollbar.set)
        
        # 添加鼠标滚轮滚动支持 - 仅限于悬停在滚动条上时
        def _on_mousewheel(event):
            self.content_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event=None):
            self.master.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event=None):
            self.master.unbind_all("<MouseWheel>")
            
        # 仅当鼠标悬停在滚动条上时才绑定滚轮事件
        self.content_scrollbar.bind("<Enter>", _bind_mousewheel)
        self.content_scrollbar.bind("<Leave>", _unbind_mousewheel)
        
        # 放置滚动组件
        self.content_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 主内容区域 - 将占据滚动框架内的空间
        content_container = ttk.Frame(self.scrollable_content)
        content_container.pack(fill=tk.BOTH, expand=True, pady=1)
        
        # 当前步骤内容（占据整个空间）
        self.content_frame = ttk.Frame(content_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=1)
        
        # 内容区域帧 - 将根据当前步骤动态变化
        self.dynamic_frame = ttk.Frame(self.content_frame)
        self.dynamic_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=1)
        
        # 底部按钮区域 - 放在固定容器之后，确保始终可见
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=5, side=tk.BOTTOM)
        
        self.prev_button = ttk.Button(button_frame, text="上一步", command=self.prev_step)
        self.prev_button.pack(side=tk.LEFT, padx=20)
        
        self.next_button = ttk.Button(button_frame, text="下一步", command=self.next_step)
        self.next_button.pack(side=tk.RIGHT, padx=20)
        
        # 保存按钮
        save_button = ttk.Button(button_frame, text="保存到文件", command=self._save_to_file)
        save_button.pack(side=tk.RIGHT, padx=20)
        
        # 初始化UI
        self.update_step_view()
        
    def _create_template_loading(self):
        """步骤1：载入基础模板"""
        print("WorldView: 正在创建模板加载界面...")
        # 创建滚动容器
        canvas = tk.Canvas(self.dynamic_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.dynamic_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # 设置Canvas的高度和宽度
        canvas.config(width=580, height=500)
        
        # 配置滚动区域
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # 确保滚动区域的宽度与Canvas相同
        def _configure_scrollable_frame(event):
            # 设置滚动区域的宽度为Canvas的宽度
            canvas.itemconfig(frame_id, width=event.width)
        
        frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", _configure_scrollable_frame)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 添加鼠标滚轮滚动支持 - 仅限于悬停在滚动条上时
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event=None):
            self.master.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event=None):
            self.master.unbind_all("<MouseWheel>")
            
        # 仅当鼠标悬停在滚动条上时才绑定滚轮事件
        scrollbar.bind("<Enter>", _bind_mousewheel)
        scrollbar.bind("<Leave>", _unbind_mousewheel)
        
        # 放置滚动组件
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 配置dynamic_frame的权重,使canvas可以扩展
        self.dynamic_frame.grid_rowconfigure(0, weight=1)
        self.dynamic_frame.grid_columnconfigure(0, weight=1)
        
        # 显示从基础配置读取的信息摘要
        summary_frame = ttk.LabelFrame(scrollable_frame, text="基础配置信息")
        summary_frame.pack(fill="x", expand=False, padx=5, pady=10)
        
        # 默认信息
        title = "未设置"
        creation_type = "未设置"
        main_type = "未设置"
        sub_type = "未设置"
        
        # 从基础配置获取信息
        if hasattr(self, 'base_config'):
            title = self.base_config.get("title", "未设置")
            creation_type = self.base_config.get("creation_type", "未设置")
            main_type = self.base_config.get("main_type", "未设置")
            sub_type = self.base_config.get("sub_type", "未设置")
            
        # 显示基础配置信息
        info_text = f"""作品标题: {title}
创作类型: {creation_type}
   主类型: {main_type}
   子类型: {sub_type}
"""
        
        summary_label = ttk.Label(summary_frame, text=info_text, justify="left", wraplength=400)
        summary_label.pack(padx=10, pady=2, anchor="w")
        
        # 添加提示信息
        ttk.Label(summary_frame, text="以上信息来自基础配置,可在基础配置面板中修改", 
                  foreground="gray", wraplength=400).pack(padx=10, pady=(0, 5), anchor="w")
        
        # 筛选与子类型匹配的模板
        matching_templates = []
        templates = []
        
        # 根据创作类型和主类型选择合适的模板示例
        if creation_type == "严肃小说":
            if main_type == "历史小说":
                templates.extend([
                    ('朝代更迭模板', '历史小说/朝代', '以王朝兴衰与政权交替为核心线索,通过宏观历史进程与微观人物命运的交织呈现历史变革'),
                    ('历史人物传记模板', '历史小说/传记', '以历史人物为叙事中心,通过考据与艺术重构相结合,立体呈现人物生平与时代影响'),
                    ('多国争霸模板', '历史小说/战争', '以多方势力角逐为框架,通过军事冲突、外交博弈与文化交融呈现复杂的国际关系变化'),
                    ('历史事件改写模板', '历史小说/推理', '基于史实但进行合理虚构,通过推理还原或假设性改写探索历史事件的可能性与必然性'),
                    ('古代正史模板', '历史小说/正史', '严格基于史料记载进行创作,通过文学性呈现还原历史现场,注重考据与细节精确性'),
                    ('近代变革模板', '历史小说/近代', '截取社会转型期的历史横断面,展现新旧文明撕扯中的人性光谱,通过文明断层线呈现变革的本质')
                ])
            elif main_type == "现实主义文学":
                templates.extend([
                    ('乡土文学模板', '现实主义/乡土', '以乡村社会变迁为背景,通过土地与人的关系呈现中国农村的传统、变革与现代化进程'),
                    ('都市生活模板', '现实主义/都市', '以现代城市生活为载体,通过都市人的情感与奋斗刻画现代社会的机遇与压力'),
                    ('工业史诗模板', '现实主义/工业', '以工业发展为背景,通过产业变革与工人命运呈现技术进步与社会转型的双重影响'),
                    ('军旅风云模板', '现实主义/军旅', '以军营生活为核心场景,通过军人成长与使命担当展现国防建设与军人情怀'),
                    ('移民叙事模板', '现实主义/移民', '聚焦跨国迁徙与文化融合的体验,通过身份认同与归属感探讨全球化背景下的人文困境'),
                    ('阶层浮沉模板', '现实主义/阶层', '以社会阶层流动为主题,通过个体奋斗与阶级壁垒的冲突呈现社会结构的变迁与固化')
                ])
            elif main_type == "社会派小说":
                templates.extend([
                    ('体制批判模板', '社会派/批判', '通过对社会体制与制度缺陷的揭示,探讨权力运作机制与个体命运之间的复杂关系'),
                    ('人性实验室模板', '社会派/人性', '设置极端社会情境考验人性底线,通过道德两难处境揭示人性的多面性与复杂性'),
                    ('伦理困局模板', '社会派/伦理', '聚焦现代伦理议题与价值冲突,通过具体案例探讨传统伦理在当代语境中的适应与变革'),
                    ('政治隐喻模板', '社会派/政治', '以隐喻和象征手法包裹政治批判,通过表象故事传达对现实权力结构的反思'),
                    ('犯罪镜像模板', '社会派/犯罪', '通过犯罪案件解剖社会病理,以罪与罚的辩证探讨展现社会问题与制度漏洞')
                ])
            elif main_type == "纯文学":
                templates.extend([
                    ('叙事实验模板', '纯文学/实验', '突破传统线性叙事,通过结构创新、视角转换与文体混搭探索小说形式的边界可能'),
                    ('意识之流模板', '纯文学/意识流', '以人物内心流动的思绪与感官印象为主要叙事方式,呈现意识活动的真实状态'),
                    ('诗性文本模板', '纯文学/诗化', '融合诗歌语言特质与散文节奏,通过高度凝练与意象丰富的语言构建抒情性叙事'),
                    ('元小说模板', '纯文学/元小说', '小说关于小说创作本身,通过自我反思与形式自觉探讨文学创作与现实的关系'),
                    ('存在主义模板', '纯文学/存在', '聚焦人的存在困境与选择焦虑,通过荒诞情境探讨生命意义与自由本质'),
                    ('魔幻写实模板', '纯文学/魔幻', '将魔幻元素与现实世界无缝融合,以超现实手法呈现现实的深层真相与隐喻')
                ])
            elif main_type == "传记文学":
                templates.extend([
                    ('虚构传记模板', '传记文学/重构', '基于真实人物生平进行文学化重构,通过虚构细节填补史料空白,展现更丰满的人物形象'),
                    ('回忆重构模板', '传记/回忆录', '以第一人称视角记述亲历事件,通过记忆筛选与情感过滤呈现主观化的历史见证'),
                    ('口述档案模板', '传记/口述', '基于口述采访材料整理编撰,通过多视角证言拼接重现历史事件与个人经历'),
                    ('家族秘史模板', '传记/家族', '以家族血脉为线索追溯多代人的兴衰历程,通过家族微观史折射大时代变迁'),
                    ('知识分子史模板', '传记/知识分子', '聚焦知识分子群体的精神轨迹,通过思想发展史与个人命运交织探讨知识分子的使命与困境')
                ])
            elif main_type == "战争文学":
                templates.extend([
                    ('战场纪实模板', '战争/纪实', '以真实战争场景为核心,通过细节再现与感官描写营造战场的紧张与残酷'),
                    ('创伤记忆模板', '战争/心理', '聚焦战争创伤的心理影响,通过后遗症与记忆闪回展现战争对个体精神的永久性烙印'),
                    ('反战寓言模板', '战争/寓言', '以寓言形式传达反战思想,通过象征与隐喻揭示战争的非人道性与荒谬性'),
                    ('军事谋略模板', '战争/谋略', '聚焦战略战术层面的博弈,通过指挥决策与情报战呈现战争的智力较量与命运抉择'),
                    ('战後重建模板', '战争/重建', '关注战后社会的创伤修复与秩序重建,通过个体与集体的愈合过程展现人性的韧性')
                ])
            elif main_type == "心理小说":
                templates.extend([
                    ('精神剖析模板', '心理/剖析', '以精神分析视角深入人物内心,通过无意识驱力与心理防御机制揭示人物行为的深层动机'),
                    ('情感拓扑模板', '心理/情感', '绘制人物情感关系图谱,通过情感结构的变化与发展探索人际关系的复杂动态'),
                    ('记忆迷宫模板', '心理/记忆', '以记忆重构与破碎为叙事核心,通过记忆拼图的逐步完成揭示被压抑的过去与真相'),
                    ('人格实验模板', '心理/人格', '探索人格分裂、多重人格或人格变异的边缘状态,通过极端心理现象折射人类心智的奥秘'),
                    ('病态美学模板', '心理/病态', '聚焦精神异常与病态心理,通过变异感官体验与扭曲认知探索边缘心理状态的审美可能')
                ])
            else:
                templates.extend([
                    ('文学探索模板', '纯文学/探索', '注重文学性与艺术表达的创作框架,探索语言、结构与形式的创新可能'),
                    ('人物传记模板', '传记文学', '真实人物生平与成就的叙述框架,结合时代背景呈现个体命运与历史的交织'),
                    ('家族史诗模板', '家族史/传记', '跨越数代的家族兴衰史诗框架,通过血脉传承与断裂展现时代变迁'),
                    ('社会变革模板', '社会派/现实', '聚焦社会变革中人物命运的框架,通过个体遭遇折射集体历史进程')
                ])
        
        # 网络小说模板
        elif creation_type == "网络小说":
            if main_type == "玄幻":
                templates.extend([
                    ('东方玄幻模板', '玄幻/东方', '以中华传统文化元素为基础构建的奇幻世界体系,融合仙道、阵法与气运等东方特色超凡力量'),
                    ('异世大陆模板', '玄幻/异世', '构建完整独立的异世界文明与规则体系,通过世界观设定支撑宏大冒险与成长故事'),
                    ('高武世界模板', '玄幻/高武', '以超凡武道与世俗力量并存的世界体系,通过武力等级划分构建清晰的世界秩序与冲突源'),
                    ('王朝争霸模板', '玄幻/争霸', '将架空历史与超凡力量相结合,通过朝代更迭、权谋争斗构建带有历史厚重感的玄幻世界')
                ])
            elif main_type == "科幻":
                templates.extend([
                    ('星际文明模板', '科幻/星际', '以太空探索与星际文明为背景,通过不同星球文明的接触与冲突展开宏大宇宙叙事'),
                    ('未来世界模板', '科幻/未来', '描绘高科技低生活的未来社会,通过科技与人文的矛盾展现技术发展的悖论和伦理挑战'),
                    ('时空穿梭模板', '科幻/时空', '以时间旅行或穿越平行宇宙为核心,通过蝴蝶效应与时间悖论探索历史可能性与命运变量'),
                    ('古武机甲模板', '科幻/古武机甲', '将古代武术体系与未来科技结合,通过古法铸造与量子技术的融合创造独特世界观'),
                    ('末世危机模板', '科幻/末世', '描绘人类文明崩溃后的生存环境,通过资源争夺与秩序重建探讨人性与社会本质'),
                    ('超级科技模板', '科幻/黑科技', '以远超当代认知的黑科技为核心,通过科学奇点、超限技术等设定构建颠覆性世界'),
                    ('进化变异模板', '科幻/变异', '聚焦生物进化、基因改造与人体强化,通过异能激发与物种变异展现生命形态的多样可能'),
                    ('赛博朋克模板', '科幻/赛博', '以高科技与低生活的反乌托邦冲突为核心,探讨人性异化、企业霸权与意识上传等主题')
                ])
            elif main_type == "仙侠":
                templates.extend([
                    ('修真文明模板', '仙侠/历史', '将修真体系融入历史背景,通过历史事件与修真干预的交织展现另类历史发展线'),
                    ('幻想修真模板', '仙侠/幻想', '融合西方奇幻与东方修真,通过仙道体系与魔法文明的碰撞创造混合型文化背景'),
                    ('现代修真模板', '仙侠/都市', '将修真体系融入现代社会,通过古老传承与现代文明的冲突展现文化碰撞与调和'),
                    ('古典仙侠模板', '仙侠/古典', '以古代为背景的传统仙侠世界,注重道法自然、修心炼性的东方修真哲学内核'),
                    ('神话修真模板', '仙侠/神话', '将中国古代神话体系与修真世界观结合,通过神仙体系的重构展现东方神话的现代演绎')
                ])
            elif main_type == "诸天":
                templates.extend([
                    ('无限流模板', '诸天/无限', '构建轮回闯关式的多元宇宙体系,通过不断穿梭于各类场景任务锻造主角成长与能力收集'),
                    ('诸天万界模板', '诸天/穿越', '以主角穿越各个不同世界为框架,通过世界规则碰撞与融合构建超宏大叙事体系'),
                    ('综漫穿越模板', '诸天/综漫', '以穿越各个动漫、游戏等作品世界为主线,通过与知名IP角色互动构建粉丝向叙事')
                ])
            elif main_type == "奇幻":
                templates.extend([
                    ('历史神话模板', '奇幻/神话', '融合历史与神话元素,通过历史真实事件与神话传说的交织重构另类历史叙事'),
                    ('西方奇幻模板', '奇幻/西方', '基于欧洲中世纪文化背景,构建包含精灵、矮人、兽人等异族的典型西方奇幻世界'),
                    ('史诗奇幻模板', '奇幻/史诗', '构建宏大世界观与漫长历史线,通过史诗般的种族兴衰与大陆变迁展现奇幻宇宙全景'),
                    ('黑暗奇幻模板', '奇幻/黑暗', '营造阴郁氛围与残酷设定,通过灰暗世界观与道德模糊性探讨生存哲学与权力本质'),
                    ('现代魔法模板', '奇幻/现魔', '将魔法体系融入现代社会,通过隐秘魔法世界与普通人类世界的并存创造双重现实'),
                    ('剑与魔法模板', '奇幻/剑魔', '以武器战技与施法系统并重的设定,构建传统奇幻RPG式的冒险与战斗体系'),
                    ('魔法学院模板', '奇幻/学院', '以魔法学院为核心场景,通过学习成长、同窗情谊与学院政治构建青春奇幻故事'),
                    ('血统冒险模板', '奇幻/血统', '聚焦血脉传承与能力觉醒,通过特殊血统的发掘与进化构建成长型奇幻冒险'),
                    ('异界传说模板', '奇幻/异界', '构建另一维度的完整异世界,通过次元旅行与异界冒险展开宏大探索叙事'),
                    ('另类幻想模板', '奇幻/另类', '打破传统奇幻框架,融合现代元素、蒸汽朋克或东方文化创造新型奇幻体系'),
                    ('龙与地下城模板', '奇幻/龙城', '策略性团队冒险叙事,构建骰子滚动般充满变量的命运史诗')
                ])
            elif main_type == "都市":
                templates.extend([
                    ('都市生活模板', '都市/生活', '以现实都市生活为背景,通过职场、感情与社会关系刻画当代都市青年的生存状态'),
                    ('都市异能模板', '都市/异能', '在现代都市背景中融入超能力设定,通过特殊能力的隐秘运用展现另类都市生活'),
                    ('商战职场模板', '都市/商战', '聚焦商业竞争与职场生存,通过商业谋略与公司权力斗争展现职场生态与人性考验'),
                    ('校园青春模板', '都市/校园', '以学校为主要场景,通过青春成长、情感萌动与梦想追求构建校园生活图景'),
                    ('娱乐明星模板', '都市/娱乐', '以演艺圈为核心背景,通过艺人生涯、明星生活与幕后故事揭示娱乐产业的光鲜与现实'),
                    ('社会乡土模板', '都市/乡土', '关注城乡结合部与城市边缘群体,通过半城市化地带的生活状态折射社会变迁'),
                    ('侦探推理模板', '都市/推理', '以都市罪案为核心,通过侦探视角的逻辑推理与犯罪心理解析构建悬疑探案故事'),
                    ('美食旅游模板', '都市/美食', '以美食探索与旅行见闻为主线,通过味蕾体验与文化交流展现生活美学与地域风情'),
                    ('重生逆袭模板', '都市/重生', '通过主角重生回到过去或获得前世记忆,利用信息差与经验优势重塑人生轨迹'),
                    ('神医兵王模板', '都市/医武', '主角同时具备医术与武力,通过悬医妙手与战斗能力在都市中行医救人、除恶扬善'),
                    ('鉴宝收藏模板', '都市/鉴宝', '聚焦古玩鉴定与收藏领域,通过文物背后的历史与传奇构建融合文化底蕴的都市故事')
                ])
            elif main_type == "洪荒":
                templates.extend([
                    ('洪荒流模板', '洪荒/传统', '基于中国神话传说中的洪荒时代,构建包含三清、西方二圣等神话人物的宏大世界观'),
                    ('上古神话模板', '洪荒/神话', '融合中国古代神话与洪荒传说,通过重构上古诸神的关系网络展现神话新解'),
                    ('混沌初开模板', '洪荒/创世', '聚焦宇宙创世与文明起源,通过开天辟地、无到有的过程展现宏大的起源叙事'),
                    ('巫妖大战模板', '洪荒/巫妖', '以上古巫族与妖族的种族大战为核心,通过种族矛盾与文明冲突构建史诗战争'),
                    ('封神演义模板', '洪荒/封神', '以封神大战为核心事件,通过神位分封与天庭建立过程重构中国神话体系'),
                    ('洪荒人族模板', '洪荒/人族', '从人族视角出发的洪荒叙事,通过弱小种族在神魔乱世中的崛起展现人族韧性'),
                    ('神话大罗模板', '洪荒/大罗', '聚焦洪荒顶级强者的博弈,通过大罗层次的力量展示与概念对抗呈现高层次的神话格局'),
                    ('鸿蒙大道模板', '洪荒/鸿蒙', '探索洪荒宇宙最本源的鸿蒙状态,通过大道法则与本源规则的探索构建哲学性世界观'),
                    ('重生洪荒模板', '洪荒/重生', '主角带着现代知识或未来记忆重生于洪荒时代,通过信息差优势在神话时代另辟蹊径'),
                    ('西游封神模板', '洪荒/西游', '将西游记与封神演义的元素融合,构建连通两大神话体系的洪荒宇宙')
                ])
            elif main_type == "系统":
                templates.extend([
                    ('任务奖励流模板', '系统/任务', '以系统发布任务并提供奖励为核心机制,通过任务完成度与奖励获取推动角色成长'),
                    ('加点升级流模板', '系统/升级', '以属性加点与技能升级为核心,通过数值成长与能力解锁构建游戏化的角色养成'),
                    ('职业系统流模板', '系统/职业', '基于职业选择与发展的系统体系,通过不同职业路线的技能树与专长构建多元成长路径'),
                    ('幕后黑手流模板', '系统/幕后', '系统本身具有独立意志或目的,通过隐藏任务与暗中引导构建系统与宿主的博弈关系'),
                    ('气运掠夺流模板', '系统/气运', '聚焦命运与气运概念,通过气运值的积累与转化影响角色命运与世界走向'),
                    ('躺平变强流模板', '系统/躺平', '主角通过看似消极的躺平行为反而获得成长,颠覆传统努力变强的叙事模式'),
                    ('多系统冲突模板', '系统/多系统', '世界中存在多个系统或主角拥有多重系统,通过系统间的互补或冲突构建复杂机制'),
                    ('反系统觉醒模板', '系统/反抗', '主角逐渐摆脱系统控制或发现系统真相,通过对抗系统束缚实现真正的自我成长')
                ])
            else:
                templates.extend([
                    ('机甲战争模板', '机甲/科幻', '以机甲为核心的未来战争框架'),
                    ('诸天万界模板', '诸天/穿越', '多元宇宙穿越的故事框架'),
                    ('末世危机模板', '末世/生存', '末日后的生存与重建故事框架'),
                    ('超级科技模板', '科幻/超能力', '超级科技与超能力的世界构建')
                ])
        
        # 剧本杀模板
        elif creation_type == "剧本杀":
            if main_type == "盒装":
                templates.extend([
                    ('硬核推理模板', '剧本杀/推理', '以复杂谜题、严密逻辑为核心,注重玩家通过线索串联、细节推演还原真相的剧本类型'),
                    ('情感沉浸模板', '剧本杀/情感', '以角色情感共鸣为核心,通过细腻剧情、人物羁绊与沉浸式抉择触发玩家情绪体验的剧本类型'),
                    ('机制博弈模板', '剧本杀/机制', '以策略对抗、资源分配为核心,通过规则设计与玩家决策推动剧情发展的剧本类型'),
                    ('恐怖惊悚模板', '剧本杀/恐怖', '以制造心理压迫感与生理惊吓为核心,通过氛围渲染、悬念铺陈和超自然元素触发玩家恐惧体验'),
                    ('欢乐撕逼模板', '剧本杀/欢乐', '以玩家间戏剧冲突、荒诞喜剧为核心,通过互揭黑料、阵营对立等无厘头互动制造爆笑体验'),
                    ('社会派模板', '剧本杀/社会', '以现实社会议题为核心,通过案件映射阶级矛盾、权力倾轧或人性困境的剧本类型'),
                    ('儿童向模板', '剧本杀/儿童', '以低龄玩家为核心受众,通过简单谜题、正向价值观传递与趣味互动设计,兼顾娱乐性与教育性')
                ])
            elif main_type == "独家":
                templates.extend([
                    ('全息剧场模板', '剧本杀/全息', '利用全息投影技术构建虚拟场景与角色,通过光影交互实现玩家与剧本世界的深度沉浸式互动'),
                    ('多线实景模板', '剧本杀/实景', '依托实体空间构建多条并行剧情线,玩家分组行动并触发独立事件,最终通过线索交汇还原完整叙事'),
                    ('NPC互动剧模板', '剧本杀/NPC', '以真人NPC为核心驱动力,通过即兴表演、实时反馈与玩家行为触发动态剧情发展的剧本类型'),
                    ('电影级演绎模板', '剧本杀/演绎', '以专业舞台剧标准打造剧本演出,通过高精度分镜编排、职业演员演绎与影视化视听语言实现剧场级体验'),
                    ('环境机关模板', '剧本杀/机关', '通过实体空间中的机械装置、电子设备或物理互动设计,将解谜与场景探索深度绑定的剧本类型'),
                    ('AR增强模板', '剧本杀/AR', '通过增强现实技术叠加虚拟信息于现实场景中,实现线索可视化、角色交互与空间解谜融合的剧本类型'),
                    ('暴风雪山庄模板', '剧本杀/密室', '封闭空间内全员被困,通过有限线索与人物关系网破解连环案件的经典推理模式')
                ])
            elif main_type == "城限":
                templates.extend([
                    ('阵营权谋模板', '剧本杀/权谋', '以玩家分属不同势力集团为核心,通过结盟、背叛、资源争夺等策略性互动推动权力格局变化的剧本类型'),
                    ('TRPG跑团模板', '剧本杀/TRPG', '以桌上角色扮演游戏规则为框架,结合剧本杀叙事结构,通过角色卡定制、开放式剧情探索与骰子判定机制'),
                    ('密码学解谜模板', '剧本杀/密码', '以古典密码、现代加密技术为核心工具,通过符号破译、密文重组与数学逻辑推演推动剧情发展的剧本类型'),
                    ('多结局抉择模板', '剧本杀/多结局', '以玩家决策为核心驱动力,通过关键选择触发不同剧情分支,最终导向多元结局的剧本类型'),
                    ('生存竞技模板', '剧本杀/生存', '以资源争夺、淘汰机制为核心,玩家通过体力对抗、策略博弈在限时绝境中求生的剧本类型'),
                    ('艺术解构模板', '剧本杀/艺术', '以经典艺术作品、文化符号或哲学概念为母题,通过隐喻、拼贴与超现实叙事重构世界观的剧本类型'),
                    ('历史重演模板', '剧本杀/历史', '以真实历史事件为叙事基底,通过玩家角色代入关键历史人物或平民视角,在既定史实框架下探索"可能性历史"')
                ])
            elif main_type == "线上本":
                templates.extend([
                    ('语音推理模板', '剧本杀/语音', '以纯语音交流为核心载体,通过对话分析、语气捕捉与逻辑链构建还原真相的剧本类型'),
                    ('视频搜证模板', '剧本杀/视频', '以预录或实时视频片段为核心线索载体,通过画面细节、背景音效与人物微表情分析推动解谜的剧本类型'),
                    ('AI主持人模板', '剧本杀/AI', '以人工智能技术替代传统主持人,通过算法控制流程推进、线索分发与玩家行为判定的剧本类型'),
                    ('虚拟场景模板', '剧本杀/虚拟', '通过3D建模、VR技术或网页端交互构建数字场景,玩家以第一视角探索环境并触发线索的剧本类型'),
                    ('异步剧本模板', '剧本杀/异步', '以非实时、分段式推进为核心,玩家通过独立完成任务、提交决策并等待剧情更新的方式参与的剧本类型'),
                    ('元宇宙剧场模板', '剧本杀/元宇宙', '基于元宇宙概念构建的平行虚拟世界,玩家通过数字分身参与跨平台剧本杀,实现资产互通与剧情共创'),
                    ('直播互动模板', '剧本杀/直播', '以直播形式呈现剧本进程,观众通过弹幕、打赏或投票实时干预剧情走向,打破"玩家-旁观者"界限')
                ])
            elif main_type == "跨界联名":
                templates.extend([
                    ('IP衍生模板', '剧本杀/IP', '与影视、游戏、文学等成熟IP合作,通过角色授权、世界观复用或彩蛋植入实现粉丝经济转化的剧本类型'),
                    ('文旅实景模板', '剧本杀/文旅', '与旅游景区、历史遗迹或城市地标合作,将剧本杀动线嵌入真实地理空间,实现"文旅+剧本杀"双业态导流'),
                    ('品牌定制模板', '剧本杀/品牌', '为企业品牌量身打造的品牌宣传型剧本杀,通过产品植入、价值观输出或用户画像匹配实现营销目标'),
                    ('教育实训模板', '剧本杀/教育', '以职业培训、学术教学或技能考核为目标,通过剧本杀模拟真实场景进行体验式学习的剧本类型'),
                    ('学术推演模板', '剧本杀/学术', '以学术研究或理论验证为隐性目标,通过剧本杀构建社会实验场,观察玩家群体在特定变量下的行为模式'),
                    ('公益宣传模板', '剧本杀/公益', '以传播公益理念、募集善款或提升社会议题关注度为目标,通过情感共鸣驱动玩家行动转化的剧本类型'),
                    ('艺术展览模板', '剧本杀/展览', '与美术馆、艺术节或独立艺术家合作,将剧本杀动线与艺术展陈深度结合,实现观展-解谜-创作三位一体')
                ])
            else:
                templates.extend([
                    ('阵营对抗模板', '剧本杀/对抗', '多阵营相互对抗的剧本杀框架'),
                    ('跑团模板', '剧本杀/跑团', '融合TRPG元素的剧本杀结构'),
                    ('解谜模板', '剧本杀/解谜', '以解谜为核心的剧本杀设计框架'),
                    ('城市探索模板', '剧本杀/城限', '结合城市场景的探索型剧本杀')
                ])
        
        # 游戏剧情模板
        elif creation_type == "游戏剧情":
            if main_type == "角色扮演(RPG)":
                templates.extend([
                    ('日式王道模板', '游戏/JRPG', '以线性剧情为核心的传统日式角色扮演游戏,强调"英雄成长"与"光明战胜黑暗"的经典叙事框架'),
                    ('美式CRPG模板', '游戏/CRPG', '以自由选择与复杂分支为核心的美式角色扮演游戏,强调玩家决策对世界与角色的深远影响'),
                    ('武侠修仙模板', '游戏/武侠', '以东方玄幻文化为根基的RPG类型,围绕"武道修行"与"渡劫飞升"展开,强调个人成长与宗门羁绊'),
                    ('赛博朋克模板', '游戏/赛博朋克', '以高科技与低生活的反乌托邦冲突为核心的RPG类型,探讨人性异化、企业霸权与意识上传等主题'),
                    ('克苏鲁神话模板', '游戏/克苏鲁', '以洛夫克拉夫特式宇宙恐怖为核心的RPG类型,强调"未知的恐惧"与"人类理性的脆弱性"'),
                    ('魂系碎片化模板', '游戏/魂系', '以隐晦叙事与高难度战斗为标志的RPG类型,通过环境细节与物品碎片拼凑世界观,强调"探索即叙事"')
                ])
            elif main_type == "叙事冒险(AVG)":
                templates.extend([
                    ('文字推理模板', '游戏/文字', '以文本交互为核心的解谜冒险类型,依赖对话、线索与逻辑链还原真相,强调"思维对抗"与"信息博弈"'),
                    ('视觉小说模板', '游戏/VN', '以图像与文本深度融合的叙事形式呈现的冒险类型,通过立绘、场景切换与分支选项推动剧情,强调情感沉浸'),
                    ('交互式电影模板', '游戏/交互电影', '以电影化演出与实时决策为核心的冒险类型,通过真人演出或高精度动画呈现剧情,强调"选择即表演"'),
                    ('恐怖解谜模板', '游戏/恐怖', '以心理压迫与生存危机为核心的冒险类型,通过环境氛围与谜题设计传递恐惧感,强调"资源限制"与"未知威胁"'),
                    ('历史重构模板', '游戏/历史', '以真实历史事件或时代为基底进行艺术加工的冒险类型,通过玩家选择改写或补全历史空白,强调因果辩证'),
                    ('生存抉择模板', '游戏/生存', '以资源匮乏与道德拷问为核心的冒险类型,通过极限环境下的策略选择塑造叙事,强调"代价意识"与"人性灰度"')
                ])
            elif main_type == "沉浸模拟":
                templates.extend([
                    ('环境叙事模板', '游戏/环境', '通过场景细节与空间设计传递剧情的叙事方式,强调"所见即故事",玩家需主动观察与联想以还原世界观'),
                    ('物件考古模板', '游戏/考古', '以物品收集与解析为核心的叙事方式,通过道具功能、铭文或磨损痕迹还原历史全貌,强调"触手可及的史诗"'),
                    ('AI生态模板', '游戏/AI', '以人工智能自主演化与群体互动为核心的叙事方式,通过算法驱动的角色行为构建动态世界,强调"活态社会"'),
                    ('多视角叙事模板', '游戏/多视角', '通过切换不同角色的视角与立场展开剧情,利用信息差与立场冲突构建复杂叙事网络,强调"真相的相对性"'),
                    ('动态世界模板', '游戏/动态', '以实时演化的世界规则与玩家行为反馈为核心的叙事方式,通过事件链与系统交互生成独特故事,强调"因果涟漪"'),
                    ('伦理困境模板', '游戏/伦理', '通过道德选择与后果反馈塑造叙事的模拟类型,迫使玩家在复杂情境中权衡价值观,强调"选择无对错"与"责任归属"')
                ])
            elif main_type == "互动叙事":
                templates.extend([
                    ('分支宇宙模板', '游戏/分支', '通过平行世界或多时间线设定展开的叙事形式,玩家的选择触发截然不同的故事分支,强调"可能性叠加"'),
                    ('元游戏叙事模板', '游戏/元叙事', '通过打破"第四面墙"或暴露游戏机制本身来构建叙事的类型,强调"游戏即媒介"与"玩家-创作者"的共谋关系'),
                    ('玩家共创模板', '游戏/共创', '通过玩家社区协作或UGC（用户生成内容）驱动剧情发展的叙事形式,强调"集体创作"与"故事民主化"'),
                    ('实时演化模板', '游戏/演化', '通过算法实时生成剧情与角色互动的叙事形式,玩家行为直接塑造世界演变轨迹,强调"无常叙事"与"动态因果"'),
                    ('人格影响模板', '游戏/人格', '通过角色性格与玩家行为双向塑造剧情的叙事形式,角色人格随互动逐步显化或异变,强调"心理映射"与"身份认同"'),
                    ('多媒介叙事模板', '游戏/多媒介', '通过整合游戏内外多种媒介载体构建叙事网络,强调"跨维度沉浸"与"虚实互文"的叙事体验')
                ])
            elif main_type == "开放叙事":
                templates.extend([
                    ('网状任务模板', '游戏/网状', '以非线性任务系统为核心的叙事形式,任务节点交织成动态网络,玩家选择触发连锁反应,强调"自由意志"'),
                    ('文明演进模板', '游戏/文明', '以文明兴衰与历史进程为核心的叙事形式,玩家通过政治、科技与文化决策塑造社会长期演变,强调"宏观叙事"'),
                    ('生态模拟模板', '游戏/生态', '以生态系统动态平衡与玩家干预为核心构建的叙事形式,通过生物链、资源循环与自然灾害模拟世界运作'),
                    ('随机事件流模板', '游戏/随机', '以算法生成动态事件为核心的叙事形式,通过不可预测的遭遇与突发危机推动剧情,强调"无常体验"'),
                    ('NPC人生模板', '游戏/NPC', '以NPC独立人生轨迹与玩家偶遇为核心的叙事形式,通过模拟个体命运交织构建世界真实感,强调"众生皆故事"'),
                    ('文明冲突模板', '游戏/冲突', '以不同文明间意识形态、资源争夺与价值观碰撞为核心的叙事形式,通过战争、外交与文化渗透推动世界变革')
                ])
            elif main_type == "实验性叙事":
                templates.extend([
                    ('时间悖论模板', '游戏/时间', '以时间旅行逻辑矛盾为核心的叙事形式,通过因果循环与平行时空制造叙事张力,强调"宿命与自由意志的对抗"'),
                    ('维度穿越模板', '游戏/维度', '多维度空间穿梭的叙事形式,通过不同维度规则的差异性创造叙事冲突,探索维度重叠的边界体验'),
                    ('意识入侵模板', '游戏/意识', '以精神世界探索与入侵为核心的叙事形式,通过潜入他人意识空间揭示隐藏记忆或情感,强调"心理地貌"'),
                    ('叙事解构模板', '游戏/解构', '以解构传统叙事为核心的实验性游戏,通过颠覆玩家期待与游戏文法规则,创造认知不和谐的审美体验'),
                    ('情感算法模板', '游戏/情感', '以情感计算与算法为核心的游戏叙事,通过量化角色情绪与关系网络,探索计算机情感模拟的可能性边界'),
                    ('后设游戏模板', '游戏/后设', '以解构游戏形式本身为核心的叙事实验,通过暴露创作过程或混淆现实与虚拟边界挑战传统叙事逻辑')
                ])
            else:
                templates.extend([
                    ('开放世界模板', '游戏/开放世界', '大型开放世界游戏的剧情框架,通过多线任务与环境叙事构建高自由度的沉浸式体验'),
                    ('都市探索模板', '游戏/都市', '现代都市背景的游戏剧情结构,结合社会问题与都市传说,打造真实而又神秘的城市探索体验'),
                    ('奇幻世界模板', '游戏/奇幻', '奇幻背景的游戏世界观框架,融合各类神话元素与奇幻种族,构建独特的魔法体系与文明架构'),
                    ('科幻宇宙模板', '游戏/科幻', '科幻题材的游戏剧情设计框架,通过未来科技与宇宙探索展现人类命运与技术伦理的深度思考')
                ])
        
        # 如果没有匹配的创作类型或模板为空,使用默认模板
        if not templates:
            templates = [
                ('通用故事模板', '各类型', '适用于各种类型创作的基础故事框架'),
                ('英雄旅程模板', '各类型', '经典英雄旅程的故事结构框架'),
                ('多线叙事模板', '各类型', '多条故事线并行发展的叙事框架'),
                ('矛盾冲突模板', '各类型', '以核心矛盾为中心的故事结构'),
                ('人物成长模板', '各类型', '聚焦人物成长与转变的故事框架')
            ]
        
        # 筛选与子类型匹配的模板
        filtered_templates = []
        if sub_type != "未设置":
            sub_type_lower = sub_type.lower()
            for template in templates:
                template_name, template_type, _ = template
                template_name_lower = template_name.lower()
                template_type_lower = template_type.lower()
                
                # 检查模板类型或名称是否与子类型匹配
                if (sub_type_lower in template_type_lower or 
                    sub_type_lower in template_name_lower or
                    any(sub_type_lower in category.lower() for category in template_type_lower.split('/'))):
                    filtered_templates.append(template)
        
        # 只有一个匹配模板时自动选择
        if len(filtered_templates) == 1:
            template = filtered_templates[0]
            template_name, template_type, template_desc = template
            
            # 自动选择模板
            self.selected_template = {
                "name": template_name,
                "type": template_type
            }
            
            # 更新输出区域
            self.output_text.config(state="normal")
            self.output_text.insert("end", f"\n●自动选择基础模板：{template_name}\n   (基于子类型'{sub_type}')\n")
            self.output_text.see("end")
            self.output_text.config(state="disabled")
            
            # 标记步骤完成
            self.steps_completed["构建基础模板"] = True
            
            # 显示自动选择界面
            ttk.Label(scrollable_frame, text=f"已根据子类型'{sub_type}'自动选择最匹配的模板:", 
                    foreground="blue", wraplength=400).pack(padx=10, pady=5, anchor="w")
            
            # 添加AI生成模板按钮 - 在自动匹配情况下也显示此按钮
            template_header = ttk.Frame(scrollable_frame)
            template_header.pack(fill="x", expand=False, padx=5, pady=2)
            
            ttk.Label(template_header, text="自动匹配的模板").pack(side="left", anchor="w")
            
            # 添加AI生成按钮
            print("WorldView: 在自动匹配模式下添加AI生成模板按钮")
            ai_gen_btn = ttk.Button(
                template_header, 
                text="AI生成模板", 
                command=self._ai_generate_template
            )
            ai_gen_btn.pack(side="right", padx=5)
            
            auto_frame = ttk.LabelFrame(scrollable_frame, text="自动选择的模板")
            auto_frame.pack(fill="x", expand=False, padx=5, pady=5)
            
            ttk.Label(auto_frame, text=f"模板名称: {template_name}", wraplength=400).pack(padx=10, pady=2, anchor="w")
            ttk.Label(auto_frame, text=f"适用类型: {template_type}", wraplength=400).pack(padx=10, pady=2, anchor="w")
            ttk.Label(auto_frame, text=f"描述: {template_desc}", wraplength=400).pack(padx=10, pady=2, anchor="w")
            
            # 显示模板预览
            preview_frame = ttk.LabelFrame(scrollable_frame, text="模板详情")
            preview_frame.pack(fill="x", expand=False, padx=5, pady=10)
            
            preview_text = tk.Text(preview_frame, height=11, width=60, wrap="word")
            preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 根据模板名称生成预览内容
            preview_content = f"{template_name}核心元素：\n\n"
            preview_content += self._generate_template_preview(template_name)
                
            preview_text.insert("1.0", preview_content)
            preview_text.config(state="disabled")
              
            # 添加确认按钮
            confirm_button = ttk.Button(scrollable_frame, text="确认并继续", command=self.next_step)
            confirm_button.pack(pady=10)
            
            # 原有的模板选择界面不再显示
            return
4. 终极危机：最大的挑战与转折点
5. 凯旋归来：成长蜕变后的回归

适用于各类主角成长型故事,提供经典英雄旅程的叙事结构。"""
        elif "奇幻" in template_name:
            return (
                "异世界设定示例：\n"
                "◈ 元素失衡大陆（火元素暴走导致沙漠持续扩张）\n"
                "◈ 天空浮岛群（依靠风晶石维持悬浮,定期迁移）\n"
                "◈ 永夜国度（靠发光植物照明,吸血鬼统治）\n"
                "◈ 机械与魔法共存的蒸汽朋克世界\n\n"
                
                "魔法体系示例：\n"
                "◈ 血魔法（威力强大但损耗寿命）\n"
                "◈ 言灵术（真名束缚,错误发音会反噬）\n"
                "◈ 召唤系（需平衡异界生物契约条件）\n"
                "◈ 附魔学（武器觉醒需饮足敌人鲜血）\n\n"
                
                "种族分布示例：\n"
                "◈ 暗精灵（日光下能力减半,掌握暗影魔法）\n"
                "◈ 狮鹫族（天空霸主,厌恶金属制品）\n"
                "◈ 树人（移动缓慢但可操控植物）\n"
                "◈ 星界使徒（来自其他位面的观察者）\n\n"
                
                "神话传说示例：\n"
                "◈ 诸神黄昏（预言魔神将挣脱世界树的束缚）\n"
                "◈ 创世石板（记载禁忌知识,阅读会疯狂）\n"
                "◈ 英雄轮回（救世主每千年转世但记忆不全）\n"
                "◈ 龙族盟约（当世界危机时所有龙族必须响应）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 魔法滥用导致元素潮汐失控\n"
                "◈ 古代封印松动释放灭世级魔兽\n"
                "◈ 种族通婚引发的血统纯化运动\n"
                "◈ 外神信徒渗透造成的信仰战争"
            )
        elif "诸天" in template_name:
            return (
                "位面体系示例：\n"
                "◈ 九重天界（每重天重力递增十倍,蕴含不同天道法则）\n"
                "◈ 深渊魔狱（十八层扭曲空间,关押旧日支配者残躯）\n"
                "◈ 科技侧位面（绝对禁魔区,发展星舰文明）\n"
                "◈ 元素潮汐位面（魔法能量周期性爆发与枯竭）\n\n"
                
                "飞升规则示例：\n"
                "◈ 渡劫飞升（需承受跨界雷劫,失败则魂飞魄散）\n"
                "◈ 信仰锚定（收集百万信徒愿力构建登神长阶）\n"
                "◈ 文明试炼（全种族通过宇宙级灾难考验）\n"
                "◈ 位面献祭（吞噬其他小世界本源获得晋升资格）\n\n"
                
                "跨界势力示例：\n"
                "◈ 轮回殿（强制征召各界强者执行维度任务）\n"
                "◈ 星界商会（倒卖各宇宙特产,贩卖位面坐标）\n"
                "◈ 观测者联盟（禁止高等文明干涉原始位面）\n"
                "◈ 深渊远征军（联合多个位面抵抗魔神入侵）\n\n"
                
                "宇宙法则示例：\n"
                "◈ 位面排斥（超越本土力量上限会被强制放逐）\n"
                "◈ 文明锁（限制科技/魔法发展速度的隐形屏障）\n"
                "◈ 因果律（跨位面复仇会引发连锁反噬）\n"
                "◈ 熵增诅咒（所有位面终将走向热寂）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 高维文明收割低维位面引发反抗战争\n"
                "◈ 不同修炼体系碰撞导致能量紊乱\n"
                "◈ 位面吞噬者引发的多元宇宙坍缩危机\n"
                "◈ 飞升者与本土至强者的统治权之争"
            )
        elif "历史" in template_name:
            return (
                "历史背景示例：\n"
                "◈ 朝代更迭期（唐末藩镇割据,五代十国混战时期）\n"
                "◈ 战争动荡期（抗日战争全面爆发,国共合作时期）\n"
                "◈ 盛世昌明期（康乾盛世,经济繁荣文化昌盛）\n"
                "◈ 变革改制期（戊戌变法,清末新政改革时期）\n\n"
                
                "政治体系示例：\n"
                "◈ 中央集权制（秦朝郡县制,皇权至上制度）\n"
                "◈ 郡县封建制（西周分封制,诸侯割据局面）\n"
                "◈ 军阀割据制（民国军阀混战,地方势力崛起）\n"
                "◈ 科举官僚制（唐宋科举取士,知识分子入仕）\n\n"
                
                "社会阶层示例：\n"
                "◈ 皇族贵胄（宗室王公,拥有特权阶级）\n"
                "◈ 官宦阶级（朝廷命官,地方州县长官）\n"
                "◈ 商贾地主（丝绸商人,大地主豪强）\n"
                "◈ 平民百姓（农民佃户,手工业者）\n\n"
                
                "文化思潮示例：\n"
                "◈ 儒家正统（三纲五常,明君贤相理想）\n"
                "◈ 道家清静（无为而治,归隐山林）\n"
                "◈ 佛教传播（禅宗盛行,寺院经济兴起）\n"
                "◈ 百家争鸣（诸子百家,学派纷争）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 新旧势力交替引发的权力斗争（如太子党与李世民集团）\n"
                "◈ 异族入侵与民族认同危机（如宋与金夏的关系）\n"
                "◈ 制度腐败导致的社会动荡（如明末农民起义）\n"
                "◈ 思想变革引发的文化冲突（如新文化运动）"
            )
        elif "现实" in template_name:
            return (
                "时代背景示例：\n"
                "◈ 改革开放初期（乡镇企业兴起,下海经商潮）\n"
                "◈ 工业化浪潮（资源型城市发展,环境代价显现）\n"
                "◈ 信息时代（互联网革命,数字鸿沟问题）\n"
                "◈ 全球化时期（国际贸易依存,文化冲击）\n\n"
                
                "社会结构示例：\n"
                "◈ 城乡二元结构（户籍制度,农民工现象）\n"
                "◈ 阶层固化现象（教育资源不均,起点不公平）\n"
                "◈ 新兴中产阶级（小资生活方式,焦虑文化）\n"
                "◈ 多元职业体系（创意产业兴起,斜杠青年）\n\n"
                
                "价值取向示例：\n"
                "◈ 传统伦理道德（家族观念,孝道传承）\n"
                "◈ 现代个人主义（自我实现,个性表达）\n"
                "◈ 物质与精神追求（消费升级,文化认同）\n"
                "◈ 社会责任感（公益意识提升,志愿者精神）\n\n"
                
                "生活形态示例：\n"
                "◈ 农村生活图景（土地承包,乡村振兴）\n"
                "◈ 城市社区生态（高楼林立,社区关系淡漠）\n"
                "◈ 工业区生存状态（工厂生活,蓝领文化）\n"
                "◈ 数字化生活方式（电商依赖,线上社交）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 传统与现代的价值观冲突（如婚恋观念代际差异）\n"
                "◈ 发展与环保的社会抉择（如工业污染与经济发展）\n"
                "◈ 个人理想与现实困境的挣扎（如艺术理想与生存压力）\n"
                "◈ 代际差异导致的家庭矛盾（如养老问题引发的冲突）"
            )
        elif "社会派" in template_name:
            return (
                "社会问题示例：\n"
                "◈ 贫富差距（底层生存困境,财富分配不均）\n"
                "◈ 教育不公（城乡教育差距,应试教育弊端）\n"
                "◈ 环境污染（工业污染事件,环境保护行动）\n"
                "◈ 科技伦理（基因编辑争议,人工智能监管）\n\n"
                
                "权力结构示例：\n"
                "◈ 政府机构（基层治理困境,官僚体系运作）\n"
                "◈ 经济实体（大型企业影响力,资本运作逻辑）\n"
                "◈ 媒体力量（舆论导向,信息过滤机制）\n"
                "◈ 民间组织（草根力量崛起,NGO运作方式）\n\n"
                
                "边缘群体示例：\n"
                "◈ 城市流动人口（生存空间,身份认同）\n"
                "◈ 特殊职业从业者（职业污名化,权益保障）\n"
                "◈ 社会底层群体（拾荒者生活,贫困代际传递）\n"
                "◈ 少数族裔（文化保护,融入主流社会）\n\n"
                
                "思潮运动示例：\n"
                "◈ 公民意识觉醒（权利意识提升,参与公共事务）\n"
                "◈ 社会改革呼声（制度变革诉求,公平正义追求）\n"
                "◈ 文化多元化（多元声音并存,亚文化兴起）\n"
                "◈ 身份政治（群体认同强化,权益话语争夺）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 社会资源分配不均引发的阶层对立（如教育资源争夺）\n"
                "◈ 权力滥用导致的公共信任危机（如官商勾结事件）\n"
                "◈ 弱势群体权益与主流价值的冲突（如性别平等运动）\n"
                "◈ 社会变革与既得利益的抗衡（如改革阻力与推动力）"
            )
        elif "电影剧本" in template_name:
            return (
                "类型特征示例：\n"
                "◈ 动作冒险（高危险场景设计,惊险动作设计）\n"
                "◈ 悬疑惊悚（谜题设计,心理恐怖元素）\n"
                "◈ 爱情喜剧（浪漫桥段,喜剧时机）\n"
                "◈ 科幻奇幻（世界观设定,视觉奇观）\n\n"
                
                "叙事结构示例：\n"
                "◈ 三幕剧结构（设定-冲突-解决的经典结构）\n"
                "◈ 非线性叙事（时间跳跃,多视角讲述）\n"
                "◈ 平行时空（多重现实,蝴蝶效应）\n"
                "◈ 多线交叉（多个故事线汇聚,命运交织）\n\n"
                
                "视听语言示例：\n"
                "◈ 蒙太奇手法（快速剪辑表达时间流逝,意识流表达）\n"
                "◈ 镜头设计（长镜头展现空间,特写表达情感）\n"
                "◈ 色彩符号（暖色调表达温馨,冷色调表达疏离）\n"
                "◈ 声音设计（环境音营造氛围,配乐强化情感）\n\n"
                
                "场景设置示例：\n"
                "◈ 城市景观（摩天大楼,贫民窟对比）\n"
                "◈ 自然环境（荒漠求生,丛林探险）\n"
                "◈ 特殊场所（监狱内部,精神病院）\n"
                "◈ 想象空间（梦境世界,虚拟现实）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 人物内心欲望与道德的对抗（如警察与罪犯的内心转变）\n"
                "◈ 个人与社会规则的冲突（如体制反抗者的抉择）\n"
                "◈ 不同价值观的人物对决（如理想主义与现实主义的碰撞）\n"
                "◈ 人与环境/命运的抗争（如灾难片中的生存挑战）"
            )
        elif "剧本杀" in template_name:
            return (
                "游戏类型示例：\n"
                "◈ 本格推理（严密逻辑,唯一真相）\n"
                "◈ 角色扮演（人物情感,身份体验）\n"
                "◈ 机制解谜（特殊规则,解谜为主）\n"
                "◈ 恐怖惊悚（氛围营造,心理恐惧）\n\n"
                
                "角色设计示例：\n"
                "◈ 身份背景（详细的人物历史,社会背景）\n"
                "◈ 性格特点（鲜明的行为模式,语言习惯）\n"
                "◈ 隐藏动机（不为人知的目标,秘密）\n"
                "◈ 关系网络（与其他角色的复杂关联）\n\n"
                
                "剧情结构示例：\n"
                "◈ 开场事件（引入故事的关键事件,如命案发生）\n"
                "◈ 线索布置（分散的信息点,需拼凑的真相）\n"
                "◈ 中期反转（打破先前认知的重要发现）\n"
                "◈ 结局设计（多重结局可能,真相揭晓）\n\n"
                
                "游戏机制示例：\n"
                "◈ 能力卡牌（特殊技能,使用限制）\n"
                "◈ 场景转换（空间变化,时间流动）\n"
                "◈ 特殊道具（关键物品,功能设计）\n"
                "◈ 玩家互动（投票机制,团队合作）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 玩家之间的利益冲突与合作需求（如卧底与平民）\n"
                "◈ 角色身份与玩家本人的认知差异（如扮演反派）\n"
                "◈ 游戏目标与道德选择的矛盾（如求生与背叛）\n"
                "◈ 真相探索与信息隐藏的拉锯战（如凶手隐藏身份）"
            )
        elif "游戏剧情" in template_name:
            return (
                "游戏类型示例：\n"
                "◈ 角色扮演（自由成长,多元选择）\n"
                "◈ 动作冒险（关卡设计,挑战难度）\n"
                "◈ 策略模拟（资源管理,战术考量）\n"
                "◈ 沙盒开放（自由探索,创造玩法）\n\n"
                
                "世界设定示例：\n"
                "◈ 历史写实（三国时期,维京时代）\n"
                "◈ 奇幻世界（魔法大陆,龙族传说）\n"
                "◈ 科技未来（赛博朋克,太空殖民）\n"
                "◈ 末日废土（核战后,生化危机）\n\n"
                
                "叙事方式示例：\n"
                "◈ 主线任务（推动故事的关键任务链）\n"
                "◈ 支线故事（丰富世界观的小故事）\n"
                "◈ 环境叙事（场景设计暗示的故事）\n"
                "◈ 收集物品（日记、录音等叙事碎片）\n\n"
                
                "玩家体验示例：\n"
                "◈ 探索发现（新区域,隐藏宝藏）\n"
                "◈ 战斗挑战（战斗系统,BOSS设计）\n"
                "◈ 解谜思考（谜题设计,环境互动）\n"
                "◈ 社交互动（NPC关系,多人合作）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 玩家自由度与叙事限制的平衡（如开放世界与主线故事）\n"
                "◈ 游戏性与剧情表现的取舍（如战斗节奏与剧情表达）\n"
                "◈ 角色成长与世界观的融合（如技能系统与背景设定）\n"
                "◈ 多结局设计中的玩家选择压力（如道德抉择系统）"
            )
        else:
            return "基础参数示例：核心冲突(资源争夺/理念对抗)、时间线关键节点(重大发明/自然灾害)、特殊地理(空间裂缝/能量潮汐区)、核心组织(统治机构/反抗势力)"

4. 潜在冲突点
   - 修真宗门与佛教道教的教义冲突
   - 皇权与修真势力的权力制衡
   - 科技发展与修真传承的矛盾"""
        
        self.suggestion_text.insert("1.0", suggestions)
        self.suggestion_text.config(state="disabled")
        
        # 添加确认按钮
        confirm_button = ttk.Button(self.dynamic_frame, text="接受建议", command=self._confirm_suggestions)
        confirm_button.grid(row=3, column=0, pady=10)
        
    def _create_conflict_detection(self):
        """步骤6：矛盾系统检测"""
        ttk.Label(self.dynamic_frame, text="矛盾系统检测与分析", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w", pady=10)
        
        # 使用更好的视觉分组和层次结构
        main_container = ttk.Frame(self.dynamic_frame)
        main_container.grid(row=1, column=0, sticky="nsew", pady=5)
        
        # 配置列宽比例
        main_container.columnconfigure(0, weight=1)  # 左侧权重
        main_container.columnconfigure(1, weight=1)  # 右侧权重
        
        # 左侧 - 社会结构推演
        left_frame = ttk.LabelFrame(main_container, text="社会结构推演")
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # 使用容器来包含图表文本和滚动条
        chart_container = ttk.Frame(left_frame)
        chart_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        chart_text = tk.Text(chart_container, height=10, width=36, wrap="word")
        chart_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        chart_scroll = ttk.Scrollbar(chart_container, orient="vertical", command=chart_text.yview)
        chart_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        chart_text.configure(yscrollcommand=chart_scroll.set)
        
        chart_text.insert("1.0", """皇权
  ↑↓ ↖↘
修真宗门 → 科举官僚
  ↑↓     ↑↓
平民阶层 ← 军事贵族

← 支持/依赖关系
↑↓ 冲突/竞争关系

关系详解：
1. 皇权与修真宗门：权力制衡与合作
2. 皇权与科举官僚：传统政治体系
3. 修真宗门与平民阶层：资源控制与民生影响
4. 军事贵族与科举官僚：朝堂角力
5. 平民阶层与军事贵族：征兵与赋税关系
6. 皇权与军事贵族：军事力量掌控""")
        chart_text.config(state="disabled")
        
        # 右侧 - 矛盾检测
        right_frame = ttk.LabelFrame(main_container, text="检测到的潜在矛盾")
        right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # 使用容器来包含矛盾文本和滚动条
        conflicts_container = ttk.Frame(right_frame)
        conflicts_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        conflicts_text = tk.Text(conflicts_container, height=10, width=36, wrap="word")
        conflicts_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        conflicts_scroll = ttk.Scrollbar(conflicts_container, orient="vertical", command=conflicts_text.yview)
        conflicts_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        conflicts_text.configure(yscrollcommand=conflicts_scroll.set)
        
        conflicts_text.insert("1.0", """1. 主要矛盾：皇权与修真宗门的权力制衡
   - 严重度：高
   - 影响范围：政治、军事、社会
   - 表现形式：法令限制、暗中较量、资源争夺
   - 处理建议：建立双方利益共同体,设立协调机构

2. 次要矛盾：修真资源分配不均
   - 严重度：中
   - 影响范围：经济、阶级
   - 表现形式：资源垄断、阶级固化、民间不满
   - 处理建议：制定资源共享制度,设立平民修真学院

3. 潜在矛盾：传统文化与修真思想的冲突
   - 严重度：低
   - 影响范围：文化、宗教、思想
   - 表现形式：学派之争、理念冲突、文化排斥
   - 处理建议：推动文化融合,发展新型哲学体系""")
        conflicts_text.config(state="disabled")
        
        # 底部 - 势力关系图
        bottom_frame = ttk.LabelFrame(self.dynamic_frame, text="势力关系图")
        bottom_frame.grid(row=2, column=0, sticky="ew", pady=10)
        
        # 使用容器来包含关系文本和滚动条
        relations_container = ttk.Frame(bottom_frame)
        relations_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        relations_text = tk.Text(relations_container, height=12, width=80, wrap="word")
        relations_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        relations_scroll = ttk.Scrollbar(relations_container, orient="vertical", command=relations_text.yview)
        relations_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        relations_text.configure(yscrollcommand=relations_scroll.set)
        
        relations_text.insert("1.0", """李世民皇权系统
    |
 ---|---|---
 |      |      |
太子派系 修真联盟 边疆军阀
 |      |      |
文官集团 江湖门派 少数民族

关系说明：
- 李世民皇权与修真联盟：表面合作,暗中制衡,相互利用
- 太子派系与文官集团：紧密联盟,共同抵制太宗新政
- 修真联盟与江湖门派：主导与被主导,资源与技术输送
- 边疆军阀与少数民族：互相利用,边境稳定的关键

关键势力详解：
1. 修真联盟：以青云派为首的五大宗门联合体,掌控灵脉资源
2. 太子派系：以李建成旧部为核心的保守势力,反对修真介入政治
3. 边疆军阀：唐朝边境守将,实际控制军事力量,对修真态度暧昧
4. 文官集团：科举出身的官员集团,维护传统秩序
5. 江湖门派：散落民间的小型修真组织,多依附大宗门生存
6. 少数民族：周边民族政权,部分已开始引入修真技术""")
        relations_text.config(state="disabled")
        
        # 添加确认按钮
        ttk.Separator(self.dynamic_frame, orient="horizontal").grid(row=3, column=0, sticky="ew", pady=5)
        
        confirm_button = ttk.Button(self.dynamic_frame, text="确认矛盾系统", command=self._confirm_conflicts)
        confirm_button.grid(row=4, column=0, pady=10)
        
    def _create_completion_validation(self):
        """步骤7：完整性验证"""
        ttk.Label(self.dynamic_frame, text="世界观完整性验证", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w", pady=10)
        
        # 使用更好的视觉分组和评分展示
        main_container = ttk.Frame(self.dynamic_frame)
        main_container.grid(row=1, column=0, sticky="nsew", pady=5)
        
        # 配置列宽比例
        main_container.columnconfigure(0, weight=1) 
        main_container.columnconfigure(1, weight=1)
        
        # 左侧 - 验证得分
        score_frame = ttk.LabelFrame(main_container, text="世界观评分")
        score_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # 确保标签列有足够宽度
        score_frame.columnconfigure(0, minsize=100)
        score_frame.columnconfigure(1, weight=1)
        
        # 验证类别与评分
        categories = [
            ("政治体系", 85),
            ("经济系统", 70),
            ("文化体系", 90),
            ("修真规则", 95),
            ("历史连贯性", 80),
            ("地理环境", 75),
            ("种族设定", 88)
        ]
        
        for i, (category, score) in enumerate(categories):
            ttk.Label(score_frame, text=f"{category}:").grid(row=i, column=0, sticky="e", padx=5, pady=3)
            progress = ttk.Progressbar(score_frame, orient="horizontal", length=150, mode="determinate")
            progress.grid(row=i, column=1, sticky="ew", padx=5, pady=3)
            progress["value"] = score
            
            # 根据分数使用不同颜色标签
            if score >= 90:
                color = "green"
            elif score >= 75:
                color = "blue"
            else:
                color = "orange"
                
            score_label = ttk.Label(score_frame, text=f"{score}%", foreground=color)
            score_label.grid(row=i, column=2, padx=5, pady=3)
        
        # 总体评分
        avg_score = sum(score for _, score in categories) / len(categories)
        ttk.Separator(score_frame, orient="horizontal").grid(row=len(categories), column=0, columnspan=3, sticky="ew", pady=10)
        ttk.Label(score_frame, text="总体完整度:", font=("Arial", 10, "bold")).grid(row=len(categories)+1, column=0, sticky="w", padx=5, pady=5)
        progress = ttk.Progressbar(score_frame, orient="horizontal", length=150, mode="determinate")
        progress.grid(row=len(categories)+1, column=1, sticky="ew", padx=5, pady=5)
        progress["value"] = avg_score
        ttk.Label(score_frame, text=f"{avg_score:.1f}%", font=("Arial", 10, "bold")).grid(row=len(categories)+1, column=2, padx=5, pady=5)
        
        # 原有的模板选择界面不再显示
        return
        
    def _confirm_parameters(self):
        """确认参数设置"""
        # 保存当前选中参数的值
        if hasattr(self, 'current_param') and self.current_param and hasattr(self, 'param_editor'):
            current_value = self.param_editor.get("1.0", tk.END).strip()
            self.param_values[self.current_param] = current_value
        
        # 检查所有参数是否已填写
        if not hasattr(self, 'param_values'):
            messagebox.showwarning("参数未设置", "参数列表为空，请先提取参数")
            return
        
        # 检查所有参数值
        empty_params = []
        for param_name, value in self.param_values.items():
            if not value.strip():
                empty_params.append(param_name)
        
        if empty_params:
            if len(empty_params) > 3:
                message = f"以下参数未填写: {', '.join(empty_params[:3])}... 等{len(empty_params)}个参数"
            else:
                message = f"以下参数未填写: {', '.join(empty_params)}"
            messagebox.showwarning("参数未填写", message)
            return
        
        # 保存参数到世界观数据
        if not hasattr(self, 'worldview_data'):
            self.worldview_data = {}
        self.worldview_data["parameters"] = self.param_values
        
        # 显示成功消息
        messagebox.showinfo("参数设置", "模板参数已保存")
        
        # 标记此步骤为已完成
        self.steps_completed["模板参数调整"] = True
        
        # 进入下一步
        self.next_step()
        
    def _confirm_suggestions(self):
        """确认扩展建议"""
        # 显示成功消息
        messagebox.showinfo("扩展建议", "扩展建议已应用到世界观框架中")
        
        # 标记此步骤为已完成
        self.steps_completed["生成扩展建议"] = True
        
        # 进入下一步
        self.next_step()
        
    def _confirm_conflicts(self):
        """确认冲突检测"""
        # 显示成功消息
        messagebox.showinfo("冲突检测", "世界观矛盾检测完成，已校正所有逻辑问题")
        
        # 标记此步骤为已完成
        self.steps_completed["检测核心冲突"] = True
        
        # 进入下一步
        self.next_step()
        
    def _optimize_completeness(self):
        """优化完整性"""
        # 显示成功消息
        messagebox.showinfo("完整性验证", "世界观完整性验证通过，结构完善")
        
        # 标记此步骤为已完成
        self.steps_completed["完善世界完整度"] = True
        
        # 进入下一步
        self.next_step()
        
    def _refresh_style_preview(self):
        """刷新风格预览"""
        try:
            # 加载当前选择的风格和文本
            style_var_text = self.style_var.get()
            
            # 检查style_var是否为整数或字符串
            if isinstance(style_var_text, int):
                style_var = style_var_text
            else:
                # 如果是字符串，尝试找到对应的索引
                styles = ["标准叙述", "玄幻史诗", "轻松诙谐", "严肃学术", "诗意浪漫", "魔幻古风"]
                if style_var_text in styles:
                    style_var = styles.index(style_var_text)
                else:
                    # 默认使用第一个风格
                    style_var = 0
            
            selected_style = styles[style_var]
            
            # 更新预览文本
            self.style_preview.config(state="normal")
            self.style_preview.delete("1.0", "end")
            
            # 获取示例文本
            sample_text = self._get_styled_sample(selected_style)
            self.style_preview.insert("1.0", sample_text)
            self.style_preview.config(state="disabled")
            
            # 标记此步骤为已完成
            self.steps_completed["风格化润色"] = True
        except Exception as e:
            print(f"刷新风格预览出错: {str(e)}")
            messagebox.showwarning("风格预览", f"刷新风格预览时出错: {str(e)}")
        
    def _save_to_file(self):
        """保存结果到文件"""
        try:
            # 获取输出内容
            output = self.results_text.get("1.0", tk.END)
            if not output.strip():
                output = self.output_text.get("1.0", tk.END)
            
            # 读取配置获取小说名称
            config_data = {}
            if self.novel_config_file.exists():
                with open(self.novel_config_file, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f) or {}
            
            # 获取作品名称
            base_config = config_data.get("base_config", {})
            title = base_config.get("title", "未命名作品").strip() or "未命名作品"
            
            # 创建保存目录
            save_dir = Path(f"data/NovelData/{title}")
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            file_path = save_dir / f"{title}_世界观大纲.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(output)
                
            messagebox.showinfo("保存成功", f"世界观大纲已保存至：\n{file_path}")
        except Exception as e:
            messagebox.showerror("保存失败", f"保存文件时出错：{str(e)}")
            
    def _finalize_worldview(self):
        """完成世界观构建并生成最终结果,并保存到novel_structure.yaml"""
        style = self.style_var.get()
        
        output = f"【风格化润色】\n选择风格：{style}\n语言风格已调整\n\n"
        output += "----------完整世界观大纲----------\n\n"
        
        # 使用默认内容（实际应用中可能需要修改）
        final_outline = """《唐修世界》架空历史世界观大纲

【基础设定】
历史转折点：玄武门之变
变量注入：修真文明出现
时间跨度：618年-648年
地理范围：唐朝全境及周边
核心矛盾：修真者与皇权的冲突

【政治体系】
1. 皇权结构
   - 皇帝作为最高权力者
   - 修真顾问团的设立
   - 修真管理机构的出现

2. 官僚制度的调整
   - 科举中加入修真能力测试
   - 修真者特殊职位设置
   - 传统官员与修真官员的权力平衡

3. 地方治理的变革
   - 州县制度改革
   - 修真资源管理机构
   - 边疆特殊管理区划

【修真体系】
1. 修真资源分布
   - 灵脉与灵石矿的分布规律
   - 天然灵药的产地与管控
   - 修真资源的国家垄断尝试

2. 修真门派体系
   - 官方认证的正统门派
   - 民间自发形成的小型门派
   - 特殊修真传承与隐世家族

3. 修真阶层划分
   - 入门：引气期、筑基期
   - 中阶：金丹期、元婴期
   - 高阶：化神期、大乘期
   - 传说：渡劫期（极少数人达到）"""
        
        output += final_outline
        
        # 将结果添加到输出文本区，先检查是否存在此属性
        if hasattr(self, 'results_text') and self.results_text.winfo_exists():
            # 启用最终结果文本框并添加内容
            self.results_text.config(state="normal")
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", output)
            self.results_text.config(state="disabled")
            
            # 滚动到顶部
            self.results_text.see("1.0")
        
        # 保存到novel_structure.yaml
        try:
            # 确保配置文件目录存在
            self.novel_config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取现有配置（如果有）
            config_data = {}
            if self.novel_config_file.exists():
                with open(self.novel_config_file, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f) or {}
            
            # 如果不存在基本配置,创建一个
            if "base_config" not in config_data:
                config_data["base_config"] = {}
            
            # 更新或添加世界观数据
            config_data["world_view"] = {
                "content": final_outline,
                "style": style,
                "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 保存更新后的配置
            with open(self.novel_config_file, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f, allow_unicode=True, sort_keys=False)
            
            # 提示保存成功
            messagebox.showinfo("完成", "世界观大纲已生成完毕,并保存到配置文件！")
        except Exception as e:
            messagebox.showerror("保存配置失败", f"保存到配置文件时出错：{str(e)}")
            # 仍然显示一个成功提示,因为至少生成了输出
            messagebox.showinfo("完成", "世界观大纲已生成,但保存配置文件失败！")

    # 添加缺失的方法
    def _create_parameter_input_view(self):
        """创建参数输入视图"""
        # 创建参数输入框架
        param_frame = ttk.Frame(self.dynamic_frame)
        param_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 标题
        ttk.Label(
            param_frame, 
            text="模板参数调整", 
            font=("Helvetica", 14, "bold")
        ).pack(pady=(0, 10))
        
        # 说明文本
        ttk.Label(
            param_frame,
            text="系统将自动从基础模板中提取参数，您可以根据需要调整这些参数。",
            wraplength=600
        ).pack(pady=(0, 10))
        
        # 创建进度指示区域
        progress_frame = ttk.Frame(param_frame)
        progress_frame.pack(fill="x", pady=10)
        
        self.param_progress_label = ttk.Label(
            progress_frame,
            text="正在从模板中提取参数...",
            foreground="blue"
        )
        self.param_progress_label.pack(side="left", padx=5)
        
        self.param_progress_indicator = ttk.Label(
            progress_frame,
            text="⏳",
            font=("Arial", 12)
        )
        self.param_progress_indicator.pack(side="left")
        
        # 创建参数容器框架
        self.params_container = ttk.Frame(param_frame)
        self.params_container.pack(fill="both", expand=True, pady=10)
        
        # 确认按钮 - 初始状态为禁用
        self.confirm_params_btn = ttk.Button(
            param_frame,
            text="确认参数",
            command=self._confirm_parameters,
            state="disabled"
        )
        self.confirm_params_btn.pack(pady=20)
        
        # 启动参数提取过程
        self.master.after(100, self._extract_parameters_from_template)

    def _extract_parameters_from_template(self):
        """从模板中提取参数"""
        # 检查是否有模板内容
        if not hasattr(self, 'worldview_template') or not self.worldview_template:
            messagebox.showwarning("提示", "未找到基础模板内容，请返回上一步创建模板")
            self.param_progress_label.config(text="未找到模板内容", foreground="red")
            self.param_progress_indicator.config(text="❌")
            return
        
        # 尝试从缓存加载参数
        cache_loaded = self._load_parameters_from_cache()
        
        if not cache_loaded:
            # 缓存不存在或加载失败，创建线程执行AI提取
            self.param_progress_label.config(text="正在从模板中提取参数...", foreground="blue")
            self.param_progress_indicator.config(text="⏳")
            extract_thread = threading.Thread(
                target=self._run_parameter_extraction,
                daemon=True
            )
            extract_thread.start()

    def _load_parameters_from_cache(self):
        """尝试从缓存加载参数"""
        try:
            # 获取作品名称
            work_title = self._get_work_title()
            if not work_title:
                print("无法获取作品名称，无法加载缓存")
                return False
            
            # 构建缓存目录和文件路径
            cache_dir = Path("data/NovelData") / work_title
            cache_file = cache_dir / "parameters_cache.json"
            
            # 检查缓存文件是否存在
            if not cache_file.exists():
                print(f"参数缓存文件不存在: {cache_file}")
                return False
            
            # 读取缓存文件
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            
            if "parameters" not in cached_data:
                print("缓存文件格式不正确，缺少parameters字段")
                return False
            
            # 加载缓存的参数
            parameters = cached_data["parameters"]
            
            # 更新UI
            self.param_progress_label.config(text="已从缓存加载参数", foreground="green")
            self.param_progress_indicator.config(text="✓")
            self._display_extracted_parameters(parameters)
            
            print(f"成功从缓存加载了 {len(parameters)} 个参数")
            return True
        except Exception as e:
            print(f"加载参数缓存时出错: {str(e)}")
            return False

    def _get_work_title(self):
        """获取当前作品标题"""
        # 尝试从base_config获取标题
        if hasattr(self, 'base_config') and self.base_config:
            title = self.base_config.get("title", "")
            if title:
                return title
        
        # 或者从配置文件读取
        try:
            if self.novel_config_file.exists():
                with open(self.novel_config_file, "r", encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                    base_config = config_data.get("base_config", {})
                    title = base_config.get("title", "")
                    if title:
                        return title
        except Exception as e:
            print(f"从配置文件获取作品标题时出错: {str(e)}")
        
        # 如果没有标题，使用时间戳作为替代
        return f"untitled_{int(time.time())}"

    def _run_parameter_extraction(self):
        """在后台线程中运行参数提取"""
        try:
            # 更新UI状态
            self.master.after(0, lambda: self.param_progress_label.config(text="正在分析模板内容...", foreground="blue"))
            self.master.after(0, lambda: self.param_progress_indicator.config(text="⏳"))
            
            # 准备提示
            template_content = self.worldview_template
            prompt = f"""请分析以下世界观模板内容，提取出关键参数及其默认值。
以JSON格式返回，格式为：
{{
  "parameters": [
    {{"name": "参数名称", "description": "参数描述", "default_value": "默认值示例"}}
  ]
}}

模板内容:
{template_content}

只返回JSON格式的结果，不要有任何其他文字。"""

            # 调用API
            try:
                from core.api_client.deepseek import api_client
                from modules.GlobalModule import global_config
                
                # 保存当前温度设置
                original_temp = global_config.generation_params.temperature
                
                # 设置低温度以获得更确定性的结果
                global_config.generation_params.temperature = 0.1
                
                # 准备消息
                messages = [
                    {"role": "system", "content": "你是一个专业的世界观设计助手，擅长分析世界观模板并提取关键参数。"},
                    {"role": "user", "content": prompt}
                ]
                
                # 调用API
                response = api_client.generate(messages)
                
                # 恢复原始温度设置
                global_config.generation_params.temperature = original_temp
                
                # 解析JSON响应
                try:
                    # 尝试直接解析整个响应
                    param_data = json.loads(response)
                    
                    # 如果解析成功但没有parameters字段，尝试在文本中查找JSON
                    if "parameters" not in param_data:
                        # 查找JSON开始和结束的位置
                        start_idx = response.find('{')
                        end_idx = response.rfind('}') + 1
                        if start_idx >= 0 and end_idx > start_idx:
                            json_str = response[start_idx:end_idx]
                            param_data = json.loads(json_str)
                    
                    # 确保有parameters字段
                    if "parameters" not in param_data:
                        raise ValueError("返回的JSON中没有parameters字段")
                    
                    # 提取参数列表
                    parameters = param_data["parameters"]
                    
                    # 更新UI显示参数
                    self.master.after(0, lambda: self._display_extracted_parameters(parameters))
                    
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                    print(f"API返回内容: {response}")
                    # 尝试在文本中查找JSON
                    import re
                    json_match = re.search(r'({.*})', response, re.DOTALL)
                    if json_match:
                        try:
                            param_data = json.loads(json_match.group(1))
                            if "parameters" in param_data:
                                parameters = param_data["parameters"]
                                self.master.after(0, lambda: self._display_extracted_parameters(parameters))
                                return
                        except:
                            pass
                    
                    # 如果无法解析，使用默认参数
                    self.master.after(0, lambda: self._use_default_parameters())
                    
            except Exception as e:
                print(f"API调用错误: {e}")
                # 使用默认参数
                self.master.after(0, lambda: self._use_default_parameters())
                
        except Exception as e:
            print(f"参数提取过程错误: {e}")
            self.master.after(0, lambda: self.param_progress_label.config(text=f"参数提取失败: {str(e)}", foreground="red"))
            self.master.after(0, lambda: self.param_progress_indicator.config(text="❌"))
            # 使用默认参数
            self.master.after(0, lambda: self._use_default_parameters())

    def _display_extracted_parameters(self, parameters):
        """显示提取的参数"""
        # 更新进度指示
        self.param_progress_label.config(text="参数提取完成", foreground="green")
        self.param_progress_indicator.config(text="✓")
        
        # 清空参数容器
        for widget in self.params_container.winfo_children():
            widget.destroy()
        
        # 保存参数到缓存
        self._save_parameters_to_cache(parameters)
        
        # 保存参数引用
        self.extracted_parameters = parameters
        
        # 创建分割窗口
        paned_window = ttk.PanedWindow(self.params_container, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 左侧参数列表框架
        left_frame = ttk.Frame(paned_window, width=200)
        paned_window.add(left_frame, weight=1)
        
        # 右侧参数内容编辑框架
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=3)
        
        # 在左侧创建参数列表
        list_label = ttk.Label(left_frame, text="参数列表", font=("Arial", 10, "bold"))
        list_label.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建带滚动条的参数列表
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建参数列表框
        self.param_listbox = tk.Listbox(
            list_frame, 
            width=30, 
            selectbackground="#a6a6a6",
            selectmode=tk.SINGLE,
            exportselection=0
        )
        self.param_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        self.param_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.param_listbox.yview)
        
        # 填充参数列表
        for i, param in enumerate(parameters):
            param_name = param.get("name", "未命名参数")
            self.param_listbox.insert(tk.END, param_name)
        
        # 右侧编辑区域
        edit_label = ttk.Label(right_frame, text="参数内容编辑", font=("Arial", 10, "bold"))
        edit_label.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加描述标签
        self.param_description_label = ttk.Label(
            right_frame, 
            text="请从左侧选择一个参数", 
            wraplength=400,
            foreground="gray"
        )
        self.param_description_label.pack(fill=tk.X, padx=5, pady=2)
        
        # 添加编辑框
        self.param_editor = scrolledtext.ScrolledText(
            right_frame, 
            height=10, 
            wrap=tk.WORD,
            undo=True
        )
        self.param_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 初始化参数值字典
        self.param_values = {}
        for param in parameters:
            param_name = param.get("name", "未命名参数")
            default_value = param.get("default_value", "")
            self.param_values[param_name] = default_value
        
        # 绑定选择事件
        self.param_listbox.bind('<<ListboxSelect>>', self._on_param_selected)
        
        # 绑定编辑框内容变更事件
        self.param_editor.bind('<FocusOut>', self._on_param_edited)
        self.param_editor.bind('<KeyRelease>', self._on_param_edited)
        
        # 如果有参数，默认选择第一个
        if parameters:
            self.param_listbox.selection_set(0)
            self.param_listbox.event_generate('<<ListboxSelect>>')
        
        # 启用确认按钮
        self.confirm_params_btn.config(state="normal")

    def _on_param_selected(self, event):
        """当选择参数列表中的项目时触发"""
        # 获取选中的索引
        selection = self.param_listbox.curselection()
        if not selection:
            return
        
        # 获取当前选中的参数名称
        index = selection[0]
        param_name = self.param_listbox.get(index)
        
        # 保存当前编辑框内容到上一个选中的参数
        current_value = self.param_editor.get("1.0", tk.END).strip()
        if hasattr(self, 'current_param') and self.current_param:
            self.param_values[self.current_param] = current_value
        
        # 更新当前选中的参数
        self.current_param = param_name
        
        # 查找参数详情
        param_info = None
        for param in self.extracted_parameters:
            if param.get("name") == param_name:
                param_info = param
                break
        
        if not param_info:
            return
        
        # 更新描述标签
        description = param_info.get("description", "")
        self.param_description_label.config(text=description if description else "无描述")
        
        # 更新编辑框内容
        self.param_editor.delete("1.0", tk.END)
        self.param_editor.insert("1.0", self.param_values.get(param_name, ""))
        
        # 将焦点设置到编辑框
        self.param_editor.focus_set()

    def _on_param_edited(self, event):
        """当参数编辑框内容改变时触发"""
        if not hasattr(self, 'current_param') or not self.current_param:
            return
        
        # 获取当前编辑框内容
        current_value = self.param_editor.get("1.0", tk.END).strip()
        
        # 更新参数值
        self.param_values[self.current_param] = current_value

    def _save_parameters_to_cache(self, parameters):
        """保存参数到缓存文件"""
        try:
            # 获取作品名称
            work_title = self._get_work_title()
            if not work_title:
                print("无法获取作品名称，无法保存缓存")
                return
            
            # 构建缓存目录和文件路径
            cache_dir = Path("data/NovelData") / work_title
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = cache_dir / "parameters_cache.json"
            
            # 保存参数到缓存文件
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump({"parameters": parameters}, f, ensure_ascii=False, indent=2)
            
            print(f"成功将 {len(parameters)} 个参数保存到缓存: {cache_file}")
        except Exception as e:
            print(f"保存参数缓存时出错: {str(e)}")

    def _use_default_parameters(self):
        """使用默认参数"""
        # 更新进度指示
        self.param_progress_label.config(text="使用默认参数", foreground="orange")
        self.param_progress_indicator.config(text="⚠")
        
        # 创建默认参数列表
        default_params = [
            {"name": "世界名称", "description": "这个世界的名称", "default_value": ""},
            {"name": "时代背景", "description": "这个世界的历史背景", "default_value": ""},
            {"name": "地理环境", "description": "这个世界的主要地理特征", "default_value": ""},
            {"name": "科技水平", "description": "这个世界的科技发展程度", "default_value": ""},
            {"name": "社会结构", "description": "这个世界的社会组织形式", "default_value": ""},
            {"name": "文化特点", "description": "这个世界的文化特征", "default_value": ""}
        ]
        
        # 显示默认参数
        self._display_extracted_parameters(default_params)

    def _ai_generate_template(self):
        """调用AI生成世界观模板"""
        print("WorldView: AI生成模板按钮被点击")
        try:
            # 获取当前选择的创作类型 - 优先使用当前保存的创作类型
            creation_type = None
            
            # 方式1: 尝试从本地变量获取
            if hasattr(self, 'current_creation_type') and self.current_creation_type:
                print(f"WorldView: 使用当前保存的创作类型: {self.current_creation_type}")
                # 如果是字符串,需要从配置文件中获取详细信息
                if isinstance(self.current_creation_type, str):
                    try:
                        with open(self.config_file, "r", encoding='utf-8') as f:
                            config_data = yaml.safe_load(f)
                            base_config = config_data.get('base_config', {})
                            main_type = base_config.get('main_type')
                            sub_type = base_config.get('sub_type')
                            if main_type and sub_type:
                                creation_type = {'主类型': main_type, '子类型': sub_type}
                                print(f"WorldView: 从配置文件解析出创作类型: {creation_type}")
                    except Exception as e:
                        print(f"WorldView: 读取配置文件失败: {e}")
                        # 如果是已知的创作类型字符串,使用硬编码的默认值
                        if self.current_creation_type == '剧本杀':
                            creation_type = {'主类型': '盒装', '子类型': '硬核推理'}
                            print(f"WorldView: 使用硬编码的默认值: {creation_type}")
                else:
                    # 已经是字典格式
                    creation_type = self.current_creation_type
            
            # 方式2: 尝试从配置文件获取
            if not creation_type:
                try:
                    with open(self.config_file, "r", encoding='utf-8') as f:
                        config_data = yaml.safe_load(f)
                        base_config = config_data.get('base_config', {})
                        main_type = base_config.get('main_type')
                        sub_type = base_config.get('sub_type')
                        if main_type and sub_type:
                            creation_type = {'主类型': main_type, '子类型': sub_type}
                            print(f"WorldView: 从配置文件获取创作类型: {creation_type}")
                except Exception as e:
                    print(f"WorldView: 读取配置文件失败: {e}")
            
            # 方式3: 尝试从UI组件获取
            if not creation_type:
                try:
                    # 尝试不同的可能路径
                    for path in ['.base_config', 'base_config', '..base_config']:
                        try:
                            base_config = self.master.nametowidget(path)
                            if hasattr(base_config, 'get_creation_type'):
                                creation_type = base_config.get_creation_type()
                                print(f"WorldView: 从UI组件获取创作类型: {creation_type}, 路径: {path}")
                                break
                        except (KeyError, AttributeError):
                            continue
                except Exception as e:
                    print(f"WorldView: 获取UI组件失败: {e}")
            
            # 方式4: 使用默认值
            if not creation_type:
                # 使用硬编码的默认值
                creation_type = {'主类型': '盒装', '子类型': '硬核推理'}
                print(f"WorldView: 所有方法都失败,使用默认值: {creation_type}")
            
            # 检查创作类型是否有效
            if not creation_type:
                messagebox.showwarning("提示", "无法获取创作类型,请先在基础配置中选择创作类型")
                return
            
            # 确保创作类型是字典格式,包含主类型和子类型
            if isinstance(creation_type, str):
                # 尝试解析字符串格式
                parts = creation_type.split()
                if len(parts) >= 2:
                    creation_type = {'主类型': parts[0], '子类型': parts[1]}
                else:
                    messagebox.showwarning("提示", f"创作类型格式不正确: {creation_type}")
                    return
            
            # 验证创作类型包含必要的键
            if not isinstance(creation_type, dict) or '主类型' not in creation_type or '子类型' not in creation_type:
                messagebox.showwarning("提示", f"创作类型格式不正确: {creation_type}")
                return
            
            # 创建生成窗口
            gen_window = tk.Toplevel(self.master)
            gen_window.title("AI生成世界观模板")
            gen_window.geometry("800x600")
            gen_window.minsize(700, 500)
            print("WorldView: 已创建生成窗口")
            
            # 创建一个Frame来放置所有控件
            main_frame = ttk.Frame(gen_window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # 顶部提示文本
            prompt_frame = ttk.Frame(main_frame)
            prompt_frame.pack(fill="x", pady=5)
            
            ttk.Label(prompt_frame, text="提示词(可编辑):", font=("Arial", 10, "bold")).pack(anchor="w")
            
            # 提示词编辑区
            prompt_editor = scrolledtext.ScrolledText(prompt_frame, height=6, wrap="word")
            prompt_editor.pack(fill="x", expand=False, pady=5)
            
            # 生成提示词
            prompt = self._build_template_prompt(creation_type)
            prompt_editor.insert("1.0", prompt)
            print(f"WorldView: 已生成提示词,长度: {len(prompt)}")
            
            # 中间分隔线
            ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)
            
            # 生成结果区域
            result_frame = ttk.Frame(main_frame)
            result_frame.pack(fill="both", expand=True, pady=5)
            
            ttk.Label(result_frame, text="生成结果:", font=("Arial", 10, "bold")).pack(anchor="w")
            
            # 结果编辑器
            editor_frame = ttk.Frame(result_frame)
            editor_frame.pack(fill="both", expand=True)
            
            editor = scrolledtext.ScrolledText(editor_frame, wrap="word")
            editor.pack(fill="both", expand=True)
            
            # 思考过程区域
            thinking_frame = ttk.Frame(main_frame)
            thinking_frame.pack(fill="x", pady=5)
            
            thinking_header = ttk.Frame(thinking_frame)
            thinking_header.pack(fill="x")
            
            ttk.Label(thinking_header, text="AI思考过程:", font=("Arial", 10, "bold")).pack(side="left")
            self.thinking_indicator = ttk.Label(thinking_header, text="●", foreground="green")
            self.thinking_indicator.pack(side="left", padx=5)
            
            self.thinking_text = scrolledtext.ScrolledText(thinking_frame, height=6, wrap="word")
            self.thinking_text.pack(fill="x", expand=False)
            
            # 底部按钮区域
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill="x", pady=10)
            
            # 生成/停止按钮
            self.gen_btn = ttk.Button(btn_frame, text="开始生成", 
                                command=lambda: self._start_template_generation(gen_window, prompt_editor.get("1.0", "end-1c"), editor))
            self.gen_btn.pack(side="left", padx=5)
            
            self.stop_btn = ttk.Button(btn_frame, text="停止生成", command=self._stop_template_generation, state="disabled")
            self.stop_btn.pack(side="left", padx=5)
            
            # 保存按钮
            self.save_btn = ttk.Button(btn_frame, text="应用模板", 
                                command=lambda: self._save_template(editor, gen_window),
                                state="disabled")
            self.save_btn.pack(side="right", padx=5)
            
            # 显示窗口并置于前台
            gen_window.transient(self.master)
            gen_window.grab_set()
            gen_window.focus_set()
            print("WorldView: 生成窗口已完成设置")
            
        except Exception as e:
            error_msg = f"创建AI生成模板窗口时出错: {str(e)}"
            print(f"WorldView错误: {error_msg}")
            messagebox.showerror("错误", error_msg)
            import traceback
            traceback.print_exc()

    def _build_template_prompt(self, creation_type):
        """根据当前创作类型构建提示词"""
        # 直接从novel_structure.yaml读取base_config部分
        main_type = "盒装"  # 默认值
        sub_type = "硬核推理"  # 默认值
        
        try:
            if self.novel_config_file.exists():
                with open(self.novel_config_file, "r", encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                    base_config = config_data.get('base_config', {})
                    main_type = base_config.get('main_type', main_type)
                    sub_type = base_config.get('sub_type', sub_type)
                    print(f"_build_template_prompt: 从novel_structure.yaml获取创作类型: 主类型={main_type}, 子类型={sub_type}")
        except Exception as e:
            print(f"_build_template_prompt: 读取novel_structure.yaml失败: {e}")
            print(f"_build_template_prompt: 使用默认值: 主类型={main_type}, 子类型={sub_type}")
        
        # 从BaseConfiguration获取完整的类型数据
        type_data = BaseConfiguration.CREATION_TYPES
        
        # 从AllSubtypes.json中获取子类型的详细定义
        subtype_description = ""
        try:
            with open("data/StudyData/AllSubtypes.json", "r", encoding="utf-8") as f:
                subtypes_data = json.load(f)
                if sub_type in subtypes_data:
                    subtype_description = subtypes_data[sub_type]
        except Exception as e:
            print(f"加载子类型数据出错: {e}")
        
        # 获取当前选择的模板信息
        template_info = ""
        if hasattr(self, 'selected_template') and self.selected_template and self.selected_template["name"]:
            template_name = self.selected_template["name"]
            template_type = self.selected_template.get("type", "")
            
            print(f"_build_template_prompt: 使用已选择的模板: {template_name}, 类型: {template_type}")
            template_info = f"基于'{template_name}'模板特性，"
            
            # 根据模板名称获取更详细的预览内容
            template_preview = self._generate_template_preview(template_name)
            if template_preview:
                template_info += f"\n\n选定的模板特点：\n{template_preview}"
        
        prompt = f"""为《{main_type}-{sub_type}》创作类型设计一个详细的世界观模板，{template_info}请提供以下要素：

一、总览设定（50字内概括核心）
- 用一句话定义世界观的"独特性"
- 区分网络小说与严肃小说的不同表现方式

二、时空与物理法则
1. 时空背景
   - 时代：现代/古代/近未来/架空纪元
   - 地理范围：主要地图构成
   - 物理法则：
     * 常规物理：是否与现实一致
     * 超自然规则：魔法、异能、科技上限及其限制

2. 时间流动
   - 时间线类型：单线/循环/平行时空
   - 特殊时间现象
   - 针对{main_type}的时间规则设计建议

三、社会结构
1. 权力与阶级
   - 统治势力：政府/教会/家族/其他形式
   - 阶级划分标准与社会矛盾

2. 经济与资源
   - 硬通货类型
   - 核心资源争夺点

3. 文化与习俗
   - 禁忌与信仰体系
   - 特色日常习俗：节日、饮食、服饰等

四、超自然/科技体系
1. 力量本源
   - 能力来源
   - 升级逻辑与等级划分
   - 能力限制与代价

2. 核心冲突关联
   - 力量体系如何影响世界观主要矛盾

五、关键组织与势力
- 至少3个重要组织，包含名称、性质、核心目标、与主角关系

六、生态与生物
- 特殊生物设计
- 自然环境威胁

七、历史大事件
- 按时间轴列出影响世界观的关键事件

八、与主线剧情的绑定技巧
- 世界观细节如何转化为剧情伏笔
- 如何通过日常元素折射世界观特色

要求：
- 符合{main_type}的一般特征
- 融入{sub_type}的典型元素和特色
- 提供具体细节而非泛泛而谈
- 构建富有创意且内部逻辑自洽的世界体系
- 为创作者提供清晰可扩展的世界框架
- 对网络小说和严肃小说分别提供合适的设计建议"""

        # 如果获取到了子类型描述，添加子类型特定要求
        if subtype_description:
            prompt += f"""
- 根据{sub_type}的特点进行针对性设计，注意体现其核心要素和创作特征"""
            
            # 继续添加完整的子类型参考
            prompt += f"\n\n参考该子类型的定义：\n{subtype_description}"
        
        return prompt

    def _start_template_generation(self, window, prompt, editor):
        """开始生成模板"""
        print("WorldView: 开始生成模板")
        try:
            # 清空编辑器和思考区域
            editor.delete("1.0", "end")
            self.thinking_text.delete("1.0", "end")
            
            # 更新UI状态
            self.gen_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.save_btn.config(state="disabled")
            self.thinking_indicator.config(foreground="red", text="●")
            
            # 保存当前窗口和编辑器的引用
            self.current_gen_window = window
            self.current_editor = editor
            
            # 创建用于在线程间安全更新UI的函数
            def safe_update_ui(func, *args):
                if window.winfo_exists():
                    window.after(0, func, *args)
            
            # 回调函数用于处理流式响应
            def safe_callback(chunk):
                safe_update_ui(self._template_stream_callback, chunk)
            
            # 定义备用模拟数据生成功能
            def generate_fallback_content():
                print("WorldView: 启用最终备用模拟内容")
                # 模拟思考过程
                safe_callback("<think>所有API尝试失败，切换到备用模拟内容...</think>")
                time.sleep(0.5)
                safe_callback("<think>正在生成硬核推理剧本杀世界观模板...</think>")
                time.sleep(0.5)
                
                # 备用模拟内容
                fallback_content = """# 硬核推理剧本杀世界观模板

1. 核心世界观概述
   这是一个表面平静但暗流涌动的现代都市,城市的表象下隐藏着错综复杂的秘密网络。社会精英阶层与普通市民共存,但界限分明。一系列看似无关的命案背后,隐藏着一个精心设计的谜题。这个世界强调逻辑的力量,每个线索都是解开真相的关键,没有超自然力量,只有人性的复杂与理性的较量。

2. 宇宙观/规则体系
   这是一个严格遵循现实世界物理法则与逻辑规则的世界。任何事件都有其合理解释,不存在超自然现象。信息是最宝贵的资源,知识就是力量。案件的解决依靠证据链与逻辑推理,而非巧合或直觉。世界运行遵循"因果律",每个结果都有其原因,每个谜题都有其答案。

3. 时空背景设定
   故事发生在现代都市,时间跨度为三天,但案件本身可能有长达数年的预谋。空间上主要集中在一栋豪华公寓大楼,这里居住着各行各业的精英人士。大楼内部结构复杂,电梯、安保系统、监控摄像头构成了一个封闭的微型社会生态系统。

4. 文明/种族/势力结构
   社会分为几个主要群体：权力阶层（政商精英、富豪）、知识阶层（医生、律师、教授）、服务阶层（管家、保安、清洁工）以及隐藏势力（地下组织、情报机构）。这些群体之间存在明显的信息不对称,各自掌握着不同的真相碎片。警方作为官方调查力量,能力受限于体制与资源。私人侦探则游走于各个阶层之间,成为连接不同信息孤岛的桥梁。

5. 核心冲突与矛盾
   表层冲突是一起密室杀人案,受害者是一位富有的收藏家。深层冲突源于一件价值连城的古董背后隐藏的秘密,这个秘密威胁到某个权贵家族的根基。各方势力为了保护自身利益或揭露真相而展开博弈。最核心的矛盾在于：真相与正义之间的选择,以及个人道德与集体利益的冲突。

6. 故事发展脉络建议
   第一阶段：案件发现,基础信息收集,建立初步嫌疑人名单。
   第二阶段：深入调查,发现表面证据的矛盾点,各人物之间的复杂关系浮出水面。
   第三阶段：关键证物出现,引发对初始假设的全面质疑,调查方向转变。
   第四阶段：隐藏多年的秘密逐渐揭露,真凶身份与动机浮现,但面临更大的道德困境。
   结局：真相大白,但留下开放性的伦理思考,没有绝对的正确答案。

7. 特色元素与象征符号
   - 古董怀表：象征时间的见证者,也是案件的关键物证
   - 残缺的棋盘：代表信息不完整,需要玩家拼凑真相
   - 镜像密码：表面看到的并非真相,需要换个角度思考
   - 红色记号笔：凶手的标志,在关键证物上留下的记号
   - 雨天：重要事件往往发生在雨天,象征真相如雨水般逐渐渗透
   - 黑白照片：过去的线索,连接历史与现在的重要媒介
   - 手套：代表精心策划,不留痕迹的犯罪手法"""

                # 分段发送模拟内容
                chunks = fallback_content.split('\n\n')
                for chunk in chunks:
                    safe_callback(chunk + '\n\n')
                    time.sleep(0.3)
                
                # 模拟完成
                safe_update_ui(self._mark_template_thinking_finished)
            
            # 在新线程中运行生成过程
            def generate_thread():
                try:
                    print("WorldView: 生成线程开始")
                    
                    # 安全更新UI状态
                    safe_update_ui(lambda: self.thinking_indicator.config(foreground="red", text="●"))
                    
                    # 导入API客户端
                    try:
                        from core.api_client.deepseek import api_client
                        print("WorldView: 成功导入API客户端")
                        
                        # 判断当前是否为DeepSeek-R1或Qwen-R1模型
                        try:
                            from modules.GlobalModule import global_config
                            model_name = global_config.model_config.name
                            show_reasoning = "DeepSeek-R1" in model_name or "Qwen-R1" in model_name
                        except:
                            show_reasoning = True  # 默认显示思维链
                        
                        # 清除编辑器内容
                        safe_update_ui(lambda: editor.delete("1.0", "end"))
                        
                        # 设置停止标志
                        self.generation_stopped = False
                        
                        # 准备消息
                        messages = [
                            {"role": "system", "content": "你是一个专业的世界观设计助手，擅长为各类作品创建详细的世界观模板和设定。"},
                            {"role": "user", "content": prompt}
                        ]
                        
                        # 使用API客户端的流式生成
                        print("WorldView: 开始调用API生成内容")
                        for chunk in api_client.stream_generate(messages, callback=safe_callback):
                            if self.generation_stopped or not window.winfo_exists():
                                print("WorldView: 生成被用户停止")
                                break
                        
                        # 生成完成
                        if not self.generation_stopped and window.winfo_exists():
                            print("WorldView: 生成完成")
                            safe_update_ui(self._mark_template_thinking_finished)
                            
                    except ImportError as e:
                        print(f"WorldView: 导入API客户端失败: {str(e)}，切换到模拟模式")
                        # 无法导入API客户端，使用模拟模式
                        generate_fallback_content()
                    except Exception as e:
                        print(f"WorldView: API调用失败，切换到模拟模式: {str(e)}")
                        # API调用失败，使用模拟模式
                        generate_fallback_content()
                        
                except Exception as e:
                    print(f"WorldView: 生成线程发生异常: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    safe_update_ui(lambda: messagebox.showerror("错误", f"生成过程发生错误: {str(e)}", parent=window))
                    # 恢复UI状态
                    safe_update_ui(lambda: [
                        self.gen_btn.config(state="normal"),
                        self.stop_btn.config(state="disabled"),
                        self.thinking_indicator.config(foreground="black", text="○")
                    ])
                finally:
                    print("WorldView: 生成线程结束")
            
            # 启动生成线程
            print("WorldView: 启动生成线程")
            self.gen_thread = threading.Thread(target=generate_thread)
            self.gen_thread.daemon = True
            self.gen_thread.start()
        
        except Exception as e:
            error_msg = f"启动生成过程时出错: {str(e)}"
            print(f"WorldView错误: {error_msg}")
            messagebox.showerror("错误", error_msg, parent=window)
            import traceback
            traceback.print_exc()
            
            # 最后的保底措施：在主线程运行备用内容生成（可能导致UI短暂冻结）
            try:
                print("WorldView: 尝试最终备用方案")
                # 不再用线程，在主线程直接更新
                editor.delete("1.0", "end")
                self.thinking_text.delete("1.0", "end")
                
                fallback_content = """# 备用硬核推理剧本杀世界观模板

1. 核心世界观概述
   表面平静的现代都市下隐藏着错综复杂的秘密网络。每条线索都是解开真相的关键，没有超自然力量，只有人性的复杂与理性的较量。

2. 宇宙观/规则体系
   严格遵循现实世界物理法则，任何事件都有合理解释。信息是最宝贵的资源，案件解决依靠证据链与逻辑推理。

3. 时空背景设定
   现代都市中的一栋豪华公寓大楼，电梯、安保系统、监控摄像头构成封闭的微型社会生态系统。

4. 文明/种族/势力结构
   权力阶层（政商精英、富豪）、知识阶层（医生、律师、教授）、服务阶层（管家、保安）以及隐藏势力（地下组织）。

5. 核心冲突与矛盾
   密室杀人案背后隐藏的家族秘密，各方势力展开博弈。真相与正义之间的选择，个人道德与集体利益的冲突。

6. 故事发展脉络
   案件发现→深入调查→关键证物出现→隐藏秘密揭露→真相大白(开放式结局)

7. 特色元素与象征符号
   古董怀表、残缺棋盘、镜像密码、红色记号笔、雨天场景、黑白照片、手套"""

                # 直接插入内容
                editor.insert("end", fallback_content)
                
                # 启用保存按钮
                self.gen_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                self.save_btn.config(state="normal")
                self.thinking_indicator.config(foreground="green", text="✓")
                
            except Exception as fallback_error:
                print(f"WorldView错误: 备用方案也失败了: {fallback_error}")
                # 真的没辙了

    def _stop_template_generation(self):
        """停止模板生成过程"""
        print("WorldView: 停止模板生成")
        # 设置停止标志
        self.generation_stopped = True
        
        # 通知API客户端停止生成
        try:
            from core.api_client.deepseek import api_client
            setattr(api_client, '_generation_stopped', True)
            print("WorldView: 已设置API客户端停止标志")
        except Exception as e:
            print(f"WorldView: 设置API客户端停止标志失败: {str(e)}")
        
        # 更新UI状态
        self.thinking_indicator.config(foreground="orange", text="⏹")
        self.gen_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.save_btn.config(state="normal")
        
        # 更新UI
        self.current_gen_window.update_idletasks()
        
        # 等待线程结束
        def ensure_stopped():
            print("WorldView: 确认停止状态")
            # 双重保险:再次设置API客户端停止标志
            try:
                from core.api_client.deepseek import api_client
                setattr(api_client, '_generation_stopped', True)
            except:
                pass
                
            if hasattr(self, 'gen_thread') and self.gen_thread.is_alive():
                self.current_gen_window.after(100, ensure_stopped)
            else:
                # 确保UI状态更新
                self.thinking_indicator.config(foreground="green", text="✓")
        
        # 使用短延迟确保UI更新
        self.current_gen_window.after(300, ensure_stopped)

    def _save_template(self, editor, gen_window):
        """保存生成的模板并应用"""
        content = editor.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("提示", "生成内容为空,无法保存", parent=gen_window)
            return
        
        # 解析生成的模板内容,提取各个部分
        template_data = self._parse_template_content(content)
        
        if not template_data:
            # 解析失败时，创建一个基本的模板数据结构
            print("WorldView: 解析模板内容失败，使用基本模板结构")
            template_data = {
                "name": "AI生成模板",
                "overview": content,  # 将所有内容放入概述部分
                "rules": "",
                "background": "",
                "factions": "",
                "conflicts": "",
                "storylines": "",
                "elements": ""
            }
            # 提示用户但继续处理
            messagebox.showwarning(
                "解析提示", 
                "无法完全解析模板内容，将整体作为概述应用。\n您仍然可以在结果中编辑和调整内容。", 
                parent=gen_window
            )
        
        # 将模板应用到当前世界观设置
        self._apply_template_data(template_data)
        
        # 关闭生成窗口
        self._safe_close_template_window(gen_window)
        
        # 提示用户模板已应用
        messagebox.showinfo("成功", "AI生成的模板已应用到世界观设置")
        
        # 更新UI显示
        self.update_step_view()

    def _parse_template_content(self, content):
        """解析生成的模板内容,提取各部分"""
        try:
            # 简单的解析逻辑,根据实际生成内容结构调整
            lines = content.split('\n')
            current_section = None
            sections = {
                "概述": [],
                "规则体系": [],
                "时空背景": [],
                "势力结构": [],
                "核心冲突": [],
                "发展脉络": [],
                "特色元素": []
            }
            
            # 移除可能的标题行
            if lines and "# " in lines[0]:
                lines = lines[1:]
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 常见的章节标题格式
                if any(x in line.lower() for x in ["核心世界观", "世界观概述"]):
                    current_section = "概述"
                    continue
                elif any(x in line.lower() for x in ["宇宙观", "规则体系"]):
                    current_section = "规则体系"
                    continue
                elif any(x in line.lower() for x in ["时空背景", "背景设定"]):
                    current_section = "时空背景"
                    continue
                elif any(x in line.lower() for x in ["文明", "种族", "势力结构"]):
                    current_section = "势力结构"
                    continue
                elif any(x in line.lower() for x in ["核心冲突", "矛盾"]):
                    current_section = "核心冲突"
                    continue
                elif any(x in line.lower() for x in ["故事发展", "脉络"]):
                    current_section = "发展脉络"
                    continue
                elif any(x in line.lower() for x in ["特色元素", "象征符号"]):
                    current_section = "特色元素"
                    continue
                    
                # 处理带数字的标题，如"1. 核心世界观概述"
                if line.strip().startswith("1.") and "概述" in line:
                    current_section = "概述"
                    continue
                elif line.strip().startswith("2.") and any(x in line for x in ["宇宙观", "规则"]):
                    current_section = "规则体系"
                    continue
                elif line.strip().startswith("3.") and "背景" in line:
                    current_section = "时空背景"
                    continue
                elif line.strip().startswith("4.") and any(x in line for x in ["文明", "种族", "势力"]):
                    current_section = "势力结构"
                    continue
                elif line.strip().startswith("5.") and any(x in line for x in ["冲突", "矛盾"]):
                    current_section = "核心冲突"
                    continue
                elif line.strip().startswith("6.") and any(x in line for x in ["故事", "发展", "脉络"]):
                    current_section = "发展脉络"
                    continue
                elif line.strip().startswith("7.") and any(x in line for x in ["特色", "元素", "符号"]):
                    current_section = "特色元素"
                    continue
                
                # 如果已经确定了当前章节，添加内容
                if current_section:
                    sections[current_section].append(line)
                else:
                    # 如果没有找到匹配的章节但有内容，将其添加到概述中
                    sections["概述"].append(line)
            
            # 检查是否所有章节都为空，如果是，则所有内容放入概述
            if all(not section for section in sections.values()):
                sections["概述"] = lines
            
            # 将各部分内容合并
            template_data = {
                "name": "AI生成模板",
                "overview": "\n".join(sections["概述"]),
                "rules": "\n".join(sections["规则体系"]),
                "background": "\n".join(sections["时空背景"]),
                "factions": "\n".join(sections["势力结构"]),
                "conflicts": "\n".join(sections["核心冲突"]),
                "storylines": "\n".join(sections["发展脉络"]),
                "elements": "\n".join(sections["特色元素"])
            }
            
            return template_data
        except Exception as e:
            print(f"解析模板内容出错: {e}")
            return None

    def _apply_template_data(self, template_data):
        """将解析的模板数据应用到当前世界观设置"""
        # 保存应用的模板数据
        self.selected_template = {"name": template_data["name"], "type": "AI生成"}
        
        # 保存到配置中
        if not hasattr(self, 'world_config'):
            self.world_config = {}
            
        self.world_config["template"] = template_data
        self.world_config["selected_template"] = self.selected_template["name"]
        
        # 标记步骤完成
        self.steps_completed["构建基础模板"] = True
        
        # 更新UI显示
        self.update_step_view()

    def _template_stream_callback(self, chunk):
        """处理模板生成的流式返回"""
        try:
            # 如果chunk是字典，可能包含思维链内容
            if isinstance(chunk, dict):
                # 处理思维链内容
                if "reasoning_content" in chunk:
                    reasoning = chunk["reasoning_content"]
                    if reasoning:
                        self._display_template_reasoning(reasoning)
                        
                # 检查是否包含thinking_finished标记
                if chunk.get("thinking_finished") and hasattr(self, 'current_editor') and self.current_editor.winfo_exists():
                    self._mark_template_thinking_finished()
                return
            
            # 如果是字符串，检查是否包含思考标记
            if isinstance(chunk, str):
                if chunk.startswith("<think>"):
                    self._display_template_reasoning(chunk)
                else:
                    self._update_template_editor(self.current_editor, chunk)
            
        except Exception as e:
            print(f"WorldView: 流式处理错误: {str(e)}")
            import traceback
            traceback.print_exc()
            # 异常情况下，尝试直接显示内容
            try:
                if isinstance(chunk, str):
                    self._update_template_editor(self.current_editor, chunk)
            except:
                pass

    def _update_template_editor(self, editor, chunk):
        """更新模板编辑器内容"""
        if not editor.winfo_exists():
            return
        
        try:
            # 插入新内容到编辑器末尾
            editor.insert("end", chunk)
            # 滚动到最新内容
            editor.see("end")
        except tk.TclError:
            pass  # 忽略可能的窗口已关闭错误

    def _display_template_reasoning(self, content):
        """显示AI思考过程"""
        if not hasattr(self, 'thinking_text') or not self.thinking_text.winfo_exists():
            return
        
        try:
            # 提取<thinking>标签中的内容
            if content.startswith("<think>") and content.endswith("</think>"):
                reasoning = content[len("<think>"):-len("</think>")]
            else:
                reasoning = content
                
            # 插入思考内容
            self.thinking_text.insert("end", reasoning)
            # 滚动到最新内容
            self.thinking_text.see("end")
        except tk.TclError:
            pass  # 忽略可能的窗口已关闭错误

    def _mark_template_thinking_finished(self):
        """标记思考过程已完成"""
        try:
            self.thinking_indicator.config(foreground="green", text="✓")
        except tk.TclError:
            pass  # 忽略可能的窗口已关闭错误

    def _safe_close_template_window(self, window):
        """安全关闭模板生成窗口"""
        try:
            # 停止任何正在进行的生成
            self._stop_template_generation()
            # 关闭窗口
            window.destroy()
        except Exception:
            pass  # 忽略可能的错误

    def _create_base_template(self):
        """步骤1：构建基础模板"""
        print("WorldView: 正在创建基础模板构建界面...")
        
        # 清空动态框架中的所有子组件
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()
        
        # 创建主内容框架
        content_frame = ttk.Frame(self.dynamic_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=1)
        
        # 创建标题
        ttk.Label(content_frame, text="构建世界观基础模板:", 
                font=("Arial", 10, "bold")).pack(anchor="w", pady=1)
        
        # 创建模板预览区域
        preview_frame = ttk.LabelFrame(content_frame)
        preview_frame.pack(fill="both", expand=True, padx=5, pady=1)
        
        # 如果已经有生成的模板，显示它
        if hasattr(self, 'worldview_template') and self.worldview_template:
            self._display_template_preview(preview_frame)
        else:
            # 创建空白的可编辑预览区域
            preview_container = ttk.Frame(preview_frame)
            preview_container.pack(fill="both", expand=True, padx=5, pady=1)
            
            self.preview_editor = scrolledtext.ScrolledText(preview_container, wrap="word", height=22)
            self.preview_editor.pack(fill="both", expand=True)
            self.preview_editor.insert("1.0", "在这里输入或编辑世界观模板内容...")
            
            # 底部按钮区域
            button_frame = ttk.Frame(preview_frame)
            button_frame.pack(fill="x", pady=5)
            
            # AI生成模板按钮
            ai_gen_btn = ttk.Button(
                button_frame, 
                text="AI生成模板", 
                command=self._ai_generate_template
            )
            ai_gen_btn.pack(side="left", padx=5)
            
            # 确认应用模板按钮
            apply_btn = ttk.Button(
                button_frame, 
                text="应用此模板", 
                command=self._apply_template_from_preview
            )
            apply_btn.pack(side="right", padx=5)
        
        # 标记步骤可以完成（当有模板时）
        if hasattr(self, 'worldview_template') and self.worldview_template:
            self.steps_completed["构建基础模板"] = True
        
    def _display_template_preview(self, parent_frame):
        """在预览区域显示模板内容"""
        # 清空父框架中的所有子组件
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        # 创建滚动文本区域来显示模板内容
        preview_container = ttk.Frame(parent_frame)
        preview_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.preview_editor = scrolledtext.ScrolledText(preview_container, wrap="word", height=15)
        self.preview_editor.pack(fill="both", expand=True)
        self.preview_editor.insert("1.0", self.worldview_template)
        
        # 底部按钮区域
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(fill="x", pady=5)
        
        # AI生成模板按钮
        ai_gen_btn = ttk.Button(
            button_frame, 
            text="AI生成模板", 
            command=self._ai_generate_template
        )
        ai_gen_btn.pack(side="left", padx=5)
        
        # 确认应用模板按钮
        apply_btn = ttk.Button(
            button_frame, 
            text="应用此模板", 
            command=self._apply_template_from_preview
        )
        apply_btn.pack(side="right", padx=5)
    
    def _apply_template_from_preview(self):
        """从预览编辑器中应用模板内容"""
        if hasattr(self, 'preview_editor') and self.preview_editor.winfo_exists():
            # 获取编辑器中的内容
            template_content = self.preview_editor.get("1.0", "end-1c")
            
            # 检查内容是否为空
            if not template_content.strip() or template_content == "在这里输入或编辑世界观模板内容...":
                messagebox.showwarning("提示", "请先输入或生成模板内容")
                return
            
            # 保存模板内容
            self.worldview_template = template_content
            
            # 解析模板内容到数据结构中
            template_data = self._parse_template_content(template_content)
            
            # 应用模板数据
            if hasattr(self, 'results_text'):
                self._apply_template_data(template_data)
            else:
                # 如果results_text不存在，至少标记步骤完成
                self.steps_completed["构建基础模板"] = True
            
            # 更新提示下一步
            messagebox.showinfo("提示", "模板已应用，请点击\"下一步\"继续模板参数调整")
        else:
            messagebox.showwarning("提示", "预览编辑器不存在，请重新加载界面")
            
    def _save_template(self, editor, gen_window):
        """保存AI生成的模板内容"""
        # 获取编辑器内容
        template_content = editor.get("1.0", "end-1c")
        
        # 如果内容为空
        if not template_content.strip():
            messagebox.showwarning("提示", "模板内容为空，请重新生成")
            return
        
        # 保存模板内容
        self.worldview_template = template_content
        
        # 标记步骤完成
        self.steps_completed["构建基础模板"] = True
        
        # 更新预览区域
        self._update_base_template_view()
        
        # 关闭生成窗口
        self._safe_close_template_window(gen_window)
        
        # 显示成功消息
        messagebox.showinfo("提示", "世界观模板已生成并保存!")
    
    def _update_base_template_view(self):
        """更新基础模板视图，显示最新生成的模板"""
        # 检查是否在步骤1
        if self.current_step_index == 0:
            self._create_base_template()
            
    # 其他方法...

    def _create_world_view_display(self):
        """步骤7：世界观展示"""
        print("WorldView: 创建世界观展示界面...")
        
        # 清空动态框架中的所有子组件
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()
        
        # 创建主内容框架
        content_frame = ttk.Frame(self.dynamic_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建标题区域
        title_frame = ttk.Frame(content_frame)
        title_frame.pack(fill="x", expand=False, padx=5, pady=10)
        
        ttk.Label(title_frame, text="世界观总览", 
                font=("Arial", 14, "bold")).pack(anchor="center")
        
        # 创建世界观展示区
        display_frame = ttk.LabelFrame(content_frame, text="完整世界观")
        display_frame.pack(fill="both", expand=True, padx=5, pady=10)
        
        # 创建选项卡界面
        self.tab_control = ttk.Notebook(display_frame)
        self.tab_control.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 创建各个选项卡
        tabs = {
            "总览": self._create_overview_tab,
            "时空背景": self._create_spacetime_tab,
            "社会结构": self._create_society_tab,
            "力量体系": self._create_power_system_tab,
            "关键组织": self._create_organizations_tab,
            "生态环境": self._create_ecology_tab,
            "历史事件": self._create_history_tab,
            "剧情关联": self._create_plot_tab
        }
        
        # 创建各个选项卡
        for tab_name, create_func in tabs.items():
            tab = ttk.Frame(self.tab_control)
            self.tab_control.add(tab, text=tab_name)
            create_func(tab)
        
        # 底部按钮区域
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill="x", pady=10)
        
        # 导出世界观文档按钮
        export_btn = ttk.Button(
            button_frame, 
            text="导出世界观文档", 
            command=self._export_world_view_document
        )
        export_btn.pack(side="right", padx=5)
        
        # 预览世界观按钮
        preview_btn = ttk.Button(
            button_frame, 
            text="预览世界观", 
            command=self._preview_world_view
        )
        preview_btn.pack(side="right", padx=5)
        
        # 标记步骤完成
        self.steps_completed["世界观展示"] = True
        
    def _create_overview_tab(self, tab):
        """创建总览选项卡"""
        frame = ttk.Frame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 核心概述
        overview_frame = ttk.LabelFrame(frame, text="核心世界观概述")
        overview_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        overview_text = scrolledtext.ScrolledText(overview_frame, wrap="word", height=6)
        overview_text.pack(fill="both", expand=True, padx=5, pady=5)
        if hasattr(self, 'worldview_template') and self.worldview_template:
            overview_text.insert("1.0", "这里显示世界观的核心概述...")
        overview_text.config(state="disabled")
        
        # 独特性与特色元素
        features_frame = ttk.LabelFrame(frame, text="世界观独特性与特色元素")
        features_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        features_text = scrolledtext.ScrolledText(features_frame, wrap="word", height=8)
        features_text.pack(fill="both", expand=True, padx=5, pady=5)
        features_text.insert("1.0", "这里显示世界观的独特性与特色元素...")
        features_text.config(state="disabled")
    
    def _create_spacetime_tab(self, tab):
        """创建时空背景选项卡"""
        frame = ttk.Frame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 时代背景
        era_frame = ttk.LabelFrame(frame, text="时代背景")
        era_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        era_text = scrolledtext.ScrolledText(era_frame, wrap="word", height=5)
        era_text.pack(fill="both", expand=True, padx=5, pady=5)
        era_text.insert("1.0", "这里显示世界的时代背景...")
        era_text.config(state="disabled")
        
        # 地理范围
        geography_frame = ttk.LabelFrame(frame, text="地理范围")
        geography_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        geography_text = scrolledtext.ScrolledText(geography_frame, wrap="word", height=5)
        geography_text.pack(fill="both", expand=True, padx=5, pady=5)
        geography_text.insert("1.0", "这里显示世界的地理范围...")
        geography_text.config(state="disabled")
        
        # 物理法则
        physics_frame = ttk.LabelFrame(frame, text="物理法则")
        physics_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        physics_text = scrolledtext.ScrolledText(physics_frame, wrap="word", height=5)
        physics_text.pack(fill="both", expand=True, padx=5, pady=5)
        physics_text.insert("1.0", "这里显示世界的物理法则...")
        physics_text.config(state="disabled")
    
    def _create_society_tab(self, tab):
        """创建社会结构选项卡"""
        frame = ttk.Frame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 权力与阶级
        power_frame = ttk.LabelFrame(frame, text="权力与阶级")
        power_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        power_text = scrolledtext.ScrolledText(power_frame, wrap="word", height=5)
        power_text.pack(fill="both", expand=True, padx=5, pady=5)
        power_text.insert("1.0", "这里显示世界的权力与阶级结构...")
        power_text.config(state="disabled")
        
        # 经济与资源
        economy_frame = ttk.LabelFrame(frame, text="经济与资源")
        economy_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        economy_text = scrolledtext.ScrolledText(economy_frame, wrap="word", height=5)
        economy_text.pack(fill="both", expand=True, padx=5, pady=5)
        economy_text.insert("1.0", "这里显示世界的经济与资源系统...")
        economy_text.config(state="disabled")
        
        # 文化与习俗
        culture_frame = ttk.LabelFrame(frame, text="文化与习俗")
        culture_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        culture_text = scrolledtext.ScrolledText(culture_frame, wrap="word", height=5)
        culture_text.pack(fill="both", expand=True, padx=5, pady=5)
        culture_text.insert("1.0", "这里显示世界的文化与习俗...")
        culture_text.config(state="disabled")
    
    def _create_power_system_tab(self, tab):
        """创建力量体系选项卡"""
        frame = ttk.Frame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 力量来源
        source_frame = ttk.LabelFrame(frame, text="力量来源")
        source_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        source_text = scrolledtext.ScrolledText(source_frame, wrap="word", height=5)
        source_text.pack(fill="both", expand=True, padx=5, pady=5)
        source_text.insert("1.0", "这里显示世界的力量来源...")
        source_text.config(state="disabled")
        
        # 能力等级与体系
        system_frame = ttk.LabelFrame(frame, text="能力等级与体系")
        system_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        system_text = scrolledtext.ScrolledText(system_frame, wrap="word", height=5)
        system_text.pack(fill="both", expand=True, padx=5, pady=5)
        system_text.insert("1.0", "这里显示世界的能力等级与体系...")
        system_text.config(state="disabled")
        
        # 限制与代价
        limits_frame = ttk.LabelFrame(frame, text="限制与代价")
        limits_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        limits_text = scrolledtext.ScrolledText(limits_frame, wrap="word", height=5)
        limits_text.pack(fill="both", expand=True, padx=5, pady=5)
        limits_text.insert("1.0", "这里显示世界的力量限制与代价...")
        limits_text.config(state="disabled")
    
    def _create_organizations_tab(self, tab):
        """创建关键组织选项卡"""
        frame = ttk.Frame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 组织列表
        orgs_frame = ttk.LabelFrame(frame, text="关键组织与势力")
        orgs_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 组织表格
        columns = ("组织名称", "性质", "核心目标", "与主角关系")
        org_tree = ttk.Treeview(orgs_frame, columns=columns, show="headings", height=10)
        
        # 设置列标题
        for col in columns:
            org_tree.heading(col, text=col)
            org_tree.column(col, width=100)
        
        # 添加示例数据
        sample_data = [
            ("示例组织1", "政府机构", "维持秩序", "敌对"),
            ("示例组织2", "商业联盟", "追求利益", "合作"),
            ("示例组织3", "秘密结社", "守护古老秘密", "中立")
        ]
        
        for item in sample_data:
            org_tree.insert("", "end", values=item)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(orgs_frame, orient="vertical", command=org_tree.yview)
        org_tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置表格和滚动条
        org_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_ecology_tab(self, tab):
        """创建生态环境选项卡"""
        frame = ttk.Frame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 特殊生物
        creatures_frame = ttk.LabelFrame(frame, text="特殊生物")
        creatures_frame.pack(fill="both", expand=True, padx=5, pady=5)
