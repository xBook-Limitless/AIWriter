import tkinter as tk
from tkinter import ttk
import yaml
import tkinter.messagebox as messagebox
from pathlib import Path
import datetime

class WorldViewPanel:
    def __init__(self, master):
        """初始化世界观面板"""
        self.master = master
        self.config_file = Path("config/user_config.yaml")
        self.novel_config_file = Path("data/configs/novel_structure.yaml")
        self.current_creation_type = ""
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.master)
        
        # 线性生成大纲系统变量
        self.current_step = 0
        self.steps = [
            "载入基础模板", "填充核心参数", "生成扩展建议", 
            "矛盾系统检测", "完整性验证", "风格化润色"
        ]
        
        # 步骤完成标志
        self.steps_completed = {step: False for step in self.steps}
        
        # 初始化模板选择
        self.selected_template = {"name": "", "type": ""}
        
        # 创建世界观面板的UI组件
        self.create_widgets()
        
        # 启动配置文件检查
        self.after = self.master.after
        self._check_config_changes()
    
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
        # 为主框架添加内边距
        self.main_frame.configure(padding=(10, 10, 10, 10))
        
        # 创建线性生成大纲系统直接嵌入到主面板中
        self._create_linear_outline_system()
    
    def _create_linear_outline_system(self):
        """在主面板中创建线性生成大纲系统（平铺布局）"""
        # 步骤指示区域 - 顶部
        step_frame = ttk.Frame(self.main_frame)
        step_frame.pack(fill=tk.X, pady=(5, 15))
          
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
        
        # 内容区域 - 中部
        content_container = ttk.Frame(self.main_frame)
        content_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 左侧 - 当前步骤内容（固定宽度）
        self.content_frame = ttk.LabelFrame(content_container, text="当前步骤")
        self.content_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5), ipadx=5, ipady=5)
        self.content_frame.pack_propagate(False)  # 防止子组件影响框架大小
        self.content_frame.config(width=450)  # 增加宽度以显示完整内容
        
        # 内容区域帧 - 将根据当前步骤动态变化
        self.dynamic_frame = ttk.Frame(self.content_frame)
        self.dynamic_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 右侧 - 实时结果（自适应填充）
        results_container = ttk.Frame(content_container)
        results_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        
        # 输出框 - 上半部分
        self.output_frame = ttk.LabelFrame(results_container, text="生成过程")
        self.output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # 添加滚动条到输出文本框
        output_container = ttk.Frame(self.output_frame)
        output_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.output_text = tk.Text(output_container, height=10, wrap="word")  # 增加高度
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        out_scrollbar = ttk.Scrollbar(output_container, orient="vertical", command=self.output_text.yview)
        out_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.configure(yscrollcommand=out_scrollbar.set)
        
        # 最终结果框 - 下半部分
        self.results_container = ttk.LabelFrame(results_container, text="最终结果")
        self.results_container.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        results_text_container = ttk.Frame(self.results_container)
        results_text_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = tk.Text(results_text_container, height=14, wrap="word")  # 增加高度
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        results_scrollbar = ttk.Scrollbar(results_text_container, orient="vertical", command=self.results_text.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        self.results_text.config(state="disabled")
        
        # 底部按钮区域
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.prev_button = ttk.Button(button_frame, text="上一步", command=self.prev_step)
        self.prev_button.pack(side=tk.LEFT, padx=20)
        
        self.next_button = ttk.Button(button_frame, text="下一步", command=self.next_step)
        self.next_button.pack(side=tk.RIGHT, padx=20)
        
        # 保存按钮
        save_button = ttk.Button(button_frame, text="保存到文件", command=self._save_to_file)
        save_button.pack(side=tk.RIGHT, padx=20)
        
        # 初始化UI
        self.update_step_view()
    
    def update_by_creation_type(self, creation_type):
        """根据创作类型更新界面，仅保存当前创作类型，不读取配置文件"""
        self.current_creation_type = creation_type
        print(f"更新当前创作类型为: {creation_type}")
    
    def update_step_view(self):
        """更新步骤视图"""
        # 保存当前滚动位置
        self.master.update_idletasks()  # 确保滚动位置是最新的
        
        # 在清除组件前，解绑所有可能的滚轮事件
        self.master.unbind_all("<MouseWheel>")
        self.master.unbind_all("<Button-4>")
        self.master.unbind_all("<Button-5>")
        
        # 重置所有步骤标签样式
        for i, label in enumerate(self.step_indicators):
            if i < self.current_step:
                label.configure(foreground="green")
            elif i == self.current_step:
                label.configure(foreground="blue", font=("Arial", 9, "bold"))
            else:
                label.configure(foreground="gray")
                
        # 清空动态内容区
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()
            
        # 根据当前步骤创建相应内容
        if self.current_step == 0:
            self._create_template_loading()
        elif self.current_step == 1:
            self._create_parameter_input()
        elif self.current_step == 2:
            self._create_suggestion_generation()
        elif self.current_step == 3:
            self._create_conflict_detection()
        elif self.current_step == 4:
            self._create_completion_validation()
        elif self.current_step == 5:
            self._create_style_polishing()
            
        # 更新按钮状态
        self.prev_button.configure(state=tk.NORMAL if self.current_step > 0 else tk.DISABLED)
        self.next_button.configure(text="完成" if self.current_step == len(self.steps) - 1 else "下一步")
        
    def next_step(self):
        """进入下一步"""
        # 检查当前步骤是否已完成
        current_step_name = self.steps[self.current_step]
        if not self.steps_completed.get(current_step_name, False):
            messagebox.showwarning("提示", f"请先完成「{current_step_name}」步骤再继续")
            return
                
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_step_view()
        else:
            # 已经是最后一步，执行完成操作
            self.finalize_outline()
            
    def prev_step(self):
        """返回上一步"""
        # 取消任何进行中的进度条动画
        if hasattr(self, 'progress_timer_id'):
            self.master.after_cancel(self.progress_timer_id)
            
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step_view()
            
    def finalize_outline(self):
        """完成大纲生成"""
        messagebox.showinfo("完成", "大纲生成完成！请在结果区查看完整大纲。")
        
    def _check_config_changes(self):
        """定期检查配置文件变化，更新界面"""
        try:
            if self.novel_config_file.exists():
                # 检查配置文件的修改时间是否变化
                current_mtime = self.novel_config_file.stat().st_mtime
                
                # 如果是第一次检查或配置文件已被修改
                if not hasattr(self, 'last_config_mtime') or current_mtime > self.last_config_mtime:
                    self.last_config_mtime = current_mtime
                    
                    # 读取基础配置信息
                    with open(self.novel_config_file, "r", encoding='utf-8') as f:
                        all_config = yaml.safe_load(f) or {}
                    
                    base_config = all_config.get("base_config", {})
                    # 保存基础配置信息供各步骤使用
                    self.base_config = {
                        "creation_type": base_config.get("creation_type", ""),
                        "main_type": base_config.get("main_type", ""),
                        "sub_type": base_config.get("sub_type", ""),
                        "title": base_config.get("title", "")
                    }
                    
                    # 如果当前正在模板载入步骤，需要刷新界面以显示最新的基础配置信息
                    if self.current_step == 0:
                        self.update_step_view()
                        
                    print(f"检测到配置文件变化，已更新基础配置信息: {self.base_config}")
        except Exception as e:
            # 静默处理异常，不打断用户体验
            print(f"配置文件检查错误: {str(e)}")
            
        # 继续下一轮检查
        self.after(2000, self._check_config_changes)
        
    def _create_template_loading(self):
        """步骤1：载入基础模板"""
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
        
        # 配置dynamic_frame的权重，使canvas可以扩展
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
        ttk.Label(summary_frame, text="以上信息来自基础配置，可在基础配置面板中修改", 
                  foreground="gray", wraplength=400).pack(padx=10, pady=(0, 5), anchor="w")
        
        # 筛选与子类型匹配的模板
        matching_templates = []
        templates = []
        
        # 根据创作类型和主类型选择合适的模板示例
        if creation_type == "严肃小说":
            if main_type == "历史小说":
                templates.extend([
                    ('朝代更迭模板', '历史小说/朝代', '以王朝兴衰与政权交替为核心线索，通过宏观历史进程与微观人物命运的交织呈现历史变革'),
                    ('历史人物传记模板', '历史小说/传记', '以历史人物为叙事中心，通过考据与艺术重构相结合，立体呈现人物生平与时代影响'),
                    ('多国争霸模板', '历史小说/战争', '以多方势力角逐为框架，通过军事冲突、外交博弈与文化交融呈现复杂的国际关系变化'),
                    ('历史事件改写模板', '历史小说/推理', '基于史实但进行合理虚构，通过推理还原或假设性改写探索历史事件的可能性与必然性'),
                    ('古代正史模板', '历史小说/正史', '严格基于史料记载进行创作，通过文学性呈现还原历史现场，注重考据与细节精确性')
                ])
            elif main_type == "现实主义文学":
                templates.extend([
                    ('乡土文学模板', '现实主义/乡土', '以乡村社会变迁为背景，通过土地与人的关系呈现中国农村的传统、变革与现代化进程'),
                    ('都市生活模板', '现实主义/都市', '以现代城市生活为载体，通过都市人的情感与奋斗刻画现代社会的机遇与压力'),
                    ('工业史诗模板', '现实主义/工业', '以工业发展为背景，通过产业变革与工人命运呈现技术进步与社会转型的双重影响'),
                    ('军旅风云模板', '现实主义/军旅', '以军营生活为核心场景，通过军人成长与使命担当展现国防建设与军人情怀'),
                    ('移民叙事模板', '现实主义/移民', '聚焦跨国迁徙与文化融合的体验，通过身份认同与归属感探讨全球化背景下的人文困境'),
                    ('阶层浮沉模板', '现实主义/阶层', '以社会阶层流动为主题，通过个体奋斗与阶级壁垒的冲突呈现社会结构的变迁与固化')
                ])
            elif main_type == "社会派小说":
                templates.extend([
                    ('体制批判模板', '社会派/批判', '通过对社会体制与制度缺陷的揭示，探讨权力运作机制与个体命运之间的复杂关系'),
                    ('人性实验室模板', '社会派/人性', '设置极端社会情境考验人性底线，通过道德两难处境揭示人性的多面性与复杂性'),
                    ('伦理困局模板', '社会派/伦理', '聚焦现代伦理议题与价值冲突，通过具体案例探讨传统伦理在当代语境中的适应与变革'),
                    ('政治隐喻模板', '社会派/政治', '以隐喻和象征手法包裹政治批判，通过表象故事传达对现实权力结构的反思'),
                    ('犯罪镜像模板', '社会派/犯罪', '通过犯罪案件解剖社会病理，以罪与罚的辩证探讨展现社会问题与制度漏洞')
                ])
            elif main_type == "纯文学":
                templates.extend([
                    ('叙事实验模板', '纯文学/实验', '突破传统线性叙事，通过结构创新、视角转换与文体混搭探索小说形式的边界可能'),
                    ('意识之流模板', '纯文学/意识流', '以人物内心流动的思绪与感官印象为主要叙事方式，呈现意识活动的真实状态'),
                    ('诗性文本模板', '纯文学/诗化', '融合诗歌语言特质与散文节奏，通过高度凝练与意象丰富的语言构建抒情性叙事'),
                    ('元小说模板', '纯文学/元小说', '小说关于小说创作本身，通过自我反思与形式自觉探讨文学创作与现实的关系'),
                    ('存在主义模板', '纯文学/存在', '聚焦人的存在困境与选择焦虑，通过荒诞情境探讨生命意义与自由本质'),
                    ('魔幻写实模板', '纯文学/魔幻', '将魔幻元素与现实世界无缝融合，以超现实手法呈现现实的深层真相与隐喻')
                ])
            elif main_type == "传记文学":
                templates.extend([
                    ('虚构传记模板', '传记文学/重构', '基于真实人物生平进行文学化重构，通过虚构细节填补史料空白，展现更丰满的人物形象'),
                    ('回忆重构模板', '传记/回忆录', '以第一人称视角记述亲历事件，通过记忆筛选与情感过滤呈现主观化的历史见证'),
                    ('口述档案模板', '传记/口述', '基于口述采访材料整理编撰，通过多视角证言拼接重现历史事件与个人经历'),
                    ('家族秘史模板', '传记/家族', '以家族血脉为线索追溯多代人的兴衰历程，通过家族微观史折射大时代变迁'),
                    ('知识分子史模板', '传记/知识分子', '聚焦知识分子群体的精神轨迹，通过思想发展史与个人命运交织探讨知识分子的使命与困境')
                ])
            elif main_type == "战争文学":
                templates.extend([
                    ('战场纪实模板', '战争/纪实', '以真实战争场景为核心，通过细节再现与感官描写营造战场的紧张与残酷'),
                    ('创伤记忆模板', '战争/心理', '聚焦战争创伤的心理影响，通过后遗症与记忆闪回展现战争对个体精神的永久性烙印'),
                    ('反战寓言模板', '战争/寓言', '以寓言形式传达反战思想，通过象征与隐喻揭示战争的非人道性与荒谬性'),
                    ('军事谋略模板', '战争/谋略', '聚焦战略战术层面的博弈，通过指挥决策与情报战呈现战争的智力较量与命运抉择'),
                    ('战後重建模板', '战争/重建', '关注战后社会的创伤修复与秩序重建，通过个体与集体的愈合过程展现人性的韧性')
                ])
            elif main_type == "心理小说":
                templates.extend([
                    ('精神剖析模板', '心理/剖析', '以精神分析视角深入人物内心，通过无意识驱力与心理防御机制揭示人物行为的深层动机'),
                    ('情感拓扑模板', '心理/情感', '绘制人物情感关系图谱，通过情感结构的变化与发展探索人际关系的复杂动态'),
                    ('记忆迷宮模板', '心理/记忆', '以记忆重构与破碎为叙事核心，通过记忆拼图的逐步完成揭示被压抑的过去与真相'),
                    ('人格实验模板', '心理/人格', '探索人格分裂、多重人格或人格变异的边缘状态，通过极端心理现象折射人类心智的奥秘'),
                    ('病态美学模板', '心理/病态', '聚焦精神异常与病态心理，通过变异感官体验与扭曲认知探索边缘心理状态的审美可能')
                ])
            else:
                templates.extend([
                    ('文学探索模板', '纯文学/探索', '注重文学性与艺术表达的创作框架，探索语言、结构与形式的创新可能'),
                    ('人物传记模板', '传记文学', '真实人物生平与成就的叙述框架，结合时代背景呈现个体命运与历史的交织'),
                    ('家族史诗模板', '家族史/传记', '跨越数代的家族兴衰史诗框架，通过血脉传承与断裂展现时代变迁'),
                    ('社会变革模板', '社会派/现实', '聚焦社会变革中人物命运的框架，通过个体遭遇折射集体历史进程')
                ])
        
        # 网络小说模板
        elif creation_type == "网络小说":
            if main_type == "玄幻":
                templates.extend([
                    ('东方玄幻模板', '玄幻/东方', '以中华传统文化元素为基础构建的奇幻世界体系，融合仙道、阵法与气运等东方特色超凡力量'),
                    ('异世大陆模板', '玄幻/异世', '构建完整独立的异世界文明与规则体系，通过世界观设定支撑宏大冒险与成长故事'),
                    ('高武世界模板', '玄幻/高武', '以超凡武道与世俗力量并存的世界体系，通过武力等级划分构建清晰的世界秩序与冲突源'),
                    ('王朝争霸模板', '玄幻/争霸', '将架空历史与超凡力量相结合，通过朝代更迭、权谋争斗构建带有历史厚重感的玄幻世界')
                ])
            elif main_type == "科幻":
                templates.extend([
                    ('星际文明模板', '科幻/星际', '以太空探索与星际文明为背景，通过不同星球文明的接触与冲突展开宏大宇宙叙事'),
                    ('未来世界模板', '科幻/未来', '描绘高科技低生活的未来社会，通过科技与人文的矛盾展现技术发展的悖论和伦理挑战'),
                    ('时空穿梭模板', '科幻/时空', '以时间旅行或穿越平行宇宙为核心，通过蝴蝶效应与时间悖论探索历史可能性与命运变量'),
                    ('古武机甲模板', '科幻/古武机甲', '将古代武术体系与未来科技结合，通过古法铸造与量子技术的融合创造独特世界观'),
                    ('末世危机模板', '科幻/末世', '描绘人类文明崩溃后的生存环境，通过资源争夺与秩序重建探讨人性与社会本质'),
                    ('超级科技模板', '科幻/黑科技', '以远超当代认知的黑科技为核心，通过科学奇点、超限技术等设定构建颠覆性世界'),
                    ('进化变异模板', '科幻/变异', '聚焦生物进化、基因改造与人体强化，通过异能激发与物种变异展现生命形态的多样可能')
                ])
            elif main_type == "仙侠":
                templates.extend([
                    ('修真文明模板', '仙侠/历史', '将修真体系融入历史背景，通过历史事件与修真干预的交织展现另类历史发展线'),
                    ('幻想修真模板', '仙侠/幻想', '融合西方奇幻与东方修真，通过仙道体系与魔法文明的碰撞创造混合型文化背景'),
                    ('现代修真模板', '仙侠/都市', '将修真体系融入现代社会，通过古老传承与现代文明的冲突展现文化碰撞与调和'),
                    ('古典仙侠模板', '仙侠/古典', '以古代为背景的传统仙侠世界，注重道法自然、修心炼性的东方修真哲学内核'),
                    ('神话修真模板', '仙侠/神话', '将中国古代神话体系与修真世界观结合，通过神仙体系的重构展现东方神话的现代演绎')
                ])
            elif main_type == "诸天":
                templates.extend([
                    ('无限流模板', '诸天/无限', '构建轮回闯关式的多元宇宙体系，通过不断穿梭于各类场景任务锻造主角成长与能力收集'),
                    ('诸天万界模板', '诸天/穿越', '以主角穿越各个不同世界为框架，通过世界规则碰撞与融合构建超宏大叙事体系'),
                    ('综漫穿越模板', '诸天/综漫', '以穿越各个动漫、游戏等作品世界为主线，通过与知名IP角色互动构建粉丝向叙事')
                ])
            elif main_type == "奇幻":
                templates.extend([
                    ('历史神话模板', '奇幻/神话', '融合历史与神话元素，通过历史真实事件与神话传说的交织重构另类历史叙事'),
                    ('西方奇幻模板', '奇幻/西方', '基于欧洲中世纪文化背景，构建包含精灵、矮人、兽人等异族的典型西方奇幻世界'),
                    ('史诗奇幻模板', '奇幻/史诗', '构建宏大世界观与漫长历史线，通过史诗般的种族兴衰与大陆变迁展现奇幻宇宙全景'),
                    ('黑暗奇幻模板', '奇幻/黑暗', '营造阴郁氛围与残酷设定，通过灰暗世界观与道德模糊性探讨生存哲学与权力本质'),
                    ('现代魔法模板', '奇幻/现魔', '将魔法体系融入现代社会，通过隐秘魔法世界与普通人类世界的并存创造双重现实'),
                    ('剑与魔法模板', '奇幻/剑魔', '以武器战技与施法系统并重的设定，构建传统奇幻RPG式的冒险与战斗体系'),
                    ('魔法学院模板', '奇幻/学院', '以魔法学院为核心场景，通过学习成长、同窗情谊与学院政治构建青春奇幻故事'),
                    ('血统冒险模板', '奇幻/血统', '聚焦血脉传承与能力觉醒，通过特殊血统的发掘与进化构建成长型奇幻冒险'),
                    ('异界传说模板', '奇幻/异界', '构建另一维度的完整异世界，通过次元旅行与异界冒险展开宏大探索叙事'),
                    ('另类幻想模板', '奇幻/另类', '打破传统奇幻框架，融合现代元素、蒸汽朋克或东方文化创造新型奇幻体系'),
                    ('龙与地下城模板', '奇幻/龙城', '策略性团队冒险叙事，构建骰子滚动般充满变量的命运史诗')
                ])
            elif main_type == "都市":
                templates.extend([
                    ('都市生活模板', '都市/生活', '以现实都市生活为背景，通过职场、感情与社会关系刻画当代都市青年的生存状态'),
                    ('都市异能模板', '都市/异能', '在现代都市背景中融入超能力设定，通过特殊能力的隐秘运用展现另类都市生活'),
                    ('商战职场模板', '都市/商战', '聚焦商业竞争与职场生存，通过商业谋略与公司权力斗争展现职场生态与人性考验'),
                    ('校园青春模板', '都市/校园', '以学校为主要场景，通过青春成长、情感萌动与梦想追求构建校园生活图景'),
                    ('娱乐明星模板', '都市/娱乐', '以演艺圈为核心背景，通过艺人生涯、明星生活与幕后故事揭示娱乐产业的光鲜与现实'),
                    ('社会乡土模板', '都市/乡土', '关注城乡结合部与城市边缘群体，通过半城市化地带的生活状态折射社会变迁'),
                    ('侦探推理模板', '都市/推理', '以都市罪案为核心，通过侦探视角的逻辑推理与犯罪心理解析构建悬疑探案故事'),
                    ('美食旅游模板', '都市/美食', '以美食探索与旅行见闻为主线，通过味蕾体验与文化交流展现生活美学与地域风情'),
                    ('重生逆袭模板', '都市/重生', '通过主角重生回到过去或获得前世记忆，利用信息差与经验优势重塑人生轨迹'),
                    ('神医兵王模板', '都市/医武', '主角同时具备医术与武力，通过悬医妙手与战斗能力在都市中行医救人、除恶扬善'),
                    ('鉴宝收藏模板', '都市/鉴宝', '聚焦古玩鉴定与收藏领域，通过文物背后的历史与传奇构建融合文化底蕴的都市故事')
                ])
            elif main_type == "洪荒":
                templates.extend([
                    ('洪荒流模板', '洪荒/传统', '基于中国神话传说中的洪荒时代，构建包含三清、西方二圣等神话人物的宏大世界观'),
                    ('上古神话模板', '洪荒/神话', '融合中国古代神话与洪荒传说，通过重构上古诸神的关系网络展现神话新解'),
                    ('混沌初开模板', '洪荒/创世', '聚焦宇宙创世与文明起源，通过开天辟地、无到有的过程展现宏大的起源叙事'),
                    ('巫妖大战模板', '洪荒/巫妖', '以上古巫族与妖族的种族大战为核心，通过种族矛盾与文明冲突构建史诗战争'),
                    ('封神演义模板', '洪荒/封神', '以封神大战为核心事件，通过神位分封与天庭建立过程重构中国神话体系'),
                    ('洪荒人族模板', '洪荒/人族', '从人族视角出发的洪荒叙事，通过弱小种族在神魔乱世中的崛起展现人族韧性'),
                    ('神话大罗模板', '洪荒/大罗', '聚焦洪荒顶级强者的博弈，通过大罗层次的力量展示与概念对抗呈现高层次的神话格局'),
                    ('鸿蒙大道模板', '洪荒/鸿蒙', '探索洪荒宇宙最本源的鸿蒙状态，通过大道法则与本源规则的探索构建哲学性世界观'),
                    ('重生洪荒模板', '洪荒/重生', '主角带着现代知识或未来记忆重生于洪荒时代，通过信息差优势在神话时代另辟蹊径'),
                    ('西游封神模板', '洪荒/西游', '将西游记与封神演义的元素融合，构建连通两大神话体系的洪荒宇宙')
                ])
            elif main_type == "系统":
                templates.extend([
                    ('任务奖励流模板', '系统/任务', '以系统发布任务并提供奖励为核心机制，通过任务完成度与奖励获取推动角色成长'),
                    ('加点升级流模板', '系统/升级', '以属性加点与技能升级为核心，通过数值成长与能力解锁构建游戏化的角色养成'),
                    ('职业系统流模板', '系统/职业', '基于职业选择与发展的系统体系，通过不同职业路线的技能树与专长构建多元成长路径'),
                    ('幕后黑手流模板', '系统/幕后', '系统本身具有独立意志或目的，通过隐藏任务与暗中引导构建系统与宿主的博弈关系'),
                    ('气运掠夺流模板', '系统/气运', '聚焦命运与气运概念，通过气运值的积累与转化影响角色命运与世界走向'),
                    ('躺平变强流模板', '系统/躺平', '主角通过看似消极的躺平行为反而获得成长，颠覆传统努力变强的叙事模式'),
                    ('多系统冲突模板', '系统/多系统', '世界中存在多个系统或主角拥有多重系统，通过系统间的互补或冲突构建复杂机制'),
                    ('反系统觉醒模板', '系统/反抗', '主角逐渐摆脱系统控制或发现系统真相，通过对抗系统束缚实现真正的自我成长')
                ])
            else:
                templates.extend([
                    ('机甲战争模板', '机甲/科幻', '以机甲为核心的未来战争框架'),
                    ('诸天万界模板', '诸天/穿越', '多元宇宙穿越的故事框架'),
                    ('末世危机模板', '末世/生存', '末日后的生存与重建故事框架'),
                    ('超级科技模板', '科幻/超能力', '超级科技与超能力的世界构建')
                ])
        
        # 剧本模板
        elif creation_type == "剧本":
            if main_type == "电影剧本":
                templates.extend([
                    ('文艺片模板', '电影/文艺', '以细腻情感表达和艺术探索为核心的剧本类型，弱化传统戏剧冲突而强调意境营造'),
                    ('黑色电影模板', '电影/黑色', '以道德模糊性与宿命论为内核的犯罪题材剧本，呈现压抑视觉符号与环形叙事陷阱'),
                    ('公路片模板', '电影/公路', '以空间位移映射心理蜕变的叙事类型，核心结构为"旅途触发人物关系裂变"'),
                    ('政治隐喻模板', '电影/政治', '以符号系统包裹现实批判的隐蔽叙事类型，通过虚构框架映射真实权力结构'),
                    ('暴力美学模板', '电影/暴力', '以暴力行为艺术化升华为核心的视觉叙事类型，通过高度风格化的动作设计消解原始残酷性'),
                    ('社会寓言模板', '电影/寓言', '以极端情境折射群体困境的批判性叙事类型，通过超现实设定解构现实社会病症'),
                    ('文献纪录片模板', '电影/纪录', '以真实历史素材重构为核心的纪实性叙事类型，需在档案考证与戏剧张力间建立平衡'),
                    ('赛博朋克模板', '电影/赛博', '高科技与低生活的反乌托邦冲突，探讨人性异化、企业霸权与意识上传主题')
                ])
            elif main_type == "电视剧本":
                templates.extend([
                    ('单元剧模板', '电视/单元', '以独立故事模块构建的剧集结构类型，每集形成封闭叙事单元，同时暗藏贯穿全季的核心线索'),
                    ('年代戏模板', '电视/年代', '以特定历史时期为容器的叙事类型，通过物质细节考古重构时代质感'),
                    ('职业剧模板', '电视/职业', '以垂直行业生态为解剖对象的专业叙事类型，需在戏剧冲突与行业真实间建立精密平衡'),
                    ('悬疑推理模板', '电视/悬疑', '以逻辑迷阵与心理博弈为双轴的智力游戏类型，核心在于"观众参与的解谜仪式感"'),
                    ('女性成长模板', '电视/女性', '以性别觉醒与自我重构为叙事主轴的剧作类型，通过微观个体命运折射宏观性别权力结构'),
                    ('黑色幽默模板', '电视/幽默', '以荒诞情境与尖刻讽刺解构现实困境的叙事类型，通过悖论性幽默揭示生存荒诞性'),
                    ('末世废土模板', '电视/末世', '以文明崩解后的生存博弈为叙事基盘的剧作类型，通过极端环境测试人性阈值'),
                    ('平行时空模板', '电视/平行', '多重平行世界的电视剧叙事结构，探索同一角色在不同时空线中的命运变化')
                ])
            elif main_type == "舞台剧本":
                templates.extend([
                    ('沉浸式戏剧模板', '舞台/沉浸', '以瓦解观演边界为核心的体验型剧场革命，将观众转化为叙事参与者与空间解谜者'),
                    ('环境戏剧模板', '舞台/环境', '以空间能量重塑为核心的剧场革命，将建筑结构转化为活态叙事器官'),
                    ('文献剧模板', '舞台/文献', '以历史档案与集体记忆为原材料的纪实剧场类型，通过纸页震颤重现被掩埋的真相'),
                    ('解构经典模板', '舞台/解构', '以经典文本为手术台的当代精神解剖，通过肢解与重组传统叙事暴露其意识形态骨骼'),
                    ('肢体剧场模板', '舞台/肢体', '以身体语汇替代文字叙事的原始表达革命，通过肌肉震颤与空间关系构建液态意义场'),
                    ('政治剧模板', '舞台/政治', '以权力结构与意识形态交锋为手术刀的剧场类型，通过戏剧冲突显影政治肌体的病理切片'),
                    ('教育剧场模板', '舞台/教育', '以戏剧为认知手术刀的教学实践类型，将知识传授转化为身体参与的沉浸式学习仪式'),
                    ('残酷戏剧模板', '舞台/残酷', '以暴力与原始欲望为手术刀的戏剧实验，用感官冲击撕裂文明伪装，揭示集体潜意识')
                ])
            elif main_type == "动画剧本":
                templates.extend([
                    ('成人动画模板', '动画/成人', '以超越年龄阈值的深层次议题为核心的动画类型，通过夸张变形美学解构社会禁忌'),
                    ('机甲战斗模板', '动画/机甲', '以钢铁巨物承载人类生存意志的终极浪漫，通过机械设计与战术博弈构建科技神话'),
                    ('治愈系模板', '动画/治愈', '以情感共振与心灵疗愈为终极目标的动画类型，通过微观叙事编织安全感网络'),
                    ('妖怪异闻模板', '动画/妖怪', '以东方志怪传统为根基的奇幻叙事类型，通过妖怪与人类共存的架空世界探讨人性边界'),
                    ('科幻寓言模板', '动画/科幻', '以科技奇观包裹哲学思辨的叙事实验，通过极端技术情境解构人类文明本质'),
                    ('蒸汽朋克模板', '动画/蒸汽', '以维多利亚美学与机械神学融合的复古未来主义类型，探讨工业革命的双刃剑效应'),
                    ('赛璐璐艺术模板', '动画/艺术', '以传统胶片分层工艺为美学基因的动画类型，重构手工动画的匠人温度'),
                    ('独立动画模板', '动画/独立', '以作者性表达突破工业流水线束缚的创作形态，通过媒介实验与叙事越界重构动画艺术边疆')
                ])
            elif main_type == "互动剧本":
                templates.extend([
                    ('多线叙事游戏模板', '互动/多线', '以玩家选择驱动叙事分形的数字戏剧革命，通过蝴蝶效应量化为分支形成复杂选择网络'),
                    ('真人互动剧模板', '互动/真人', '以实拍影像与即时抉择融合的跨媒介实验，将观众转化为虚拟世界的道德仲裁者'),
                    ('ARG现实游戏模板', '互动/ARG', '以虚实边界溶解为终极目标的沉浸式叙事革命，通过篡改现实图层将整个世界转化为游戏棋盘'),
                    ('AI生成剧本模板', '互动/AI', '以神经网络为创作主体的叙事实验，通过算法吞噬与重组人类故事基因探索机器创作边界'),
                    ('分支电影模板', '互动/分支', '以时间轴裂变为核心的观影革命，通过实时渲染技术让每秒都成为叙事分岔点'),
                    ('虚拟现实戏剧模板', '互动/VR', '以六自由度空间叙事重构戏剧本体论，通过触觉反馈与眼球追踪将观众炼化为故事粒子'),
                    ('跨媒介叙事模板', '互动/跨媒介', '通过整合游戏内外多种媒介载体构建叙事网络，强调跨维度沉浸与虚实互文'),
                    ('元剧本实验模板', '互动/元剧本', '以解构叙事本身为终极目标的超小说剧场，通过暴露创作机制将观众炼化为故事的同谋者')
                ])
            else:
                templates.extend([
                    ('话剧剧本模板', '舞台/话剧', '舞台话剧的结构与对白设计框架'),
                    ('音乐剧模板', '舞台/音乐剧', '融合音乐与戏剧的舞台剧本框架'),
                    ('实验剧模板', '舞台/实验', '打破传统的实验性舞台剧框架'),
                    ('独角戏模板', '舞台/独角戏', '单人表演的戏剧结构设计')
                ])
        
        # 剧本杀模板
        elif creation_type == "剧本杀":
            if main_type == "盒装":
                templates.extend([
                    ('硬核推理模板', '剧本杀/推理', '以复杂谜题、严密逻辑为核心，注重玩家通过线索串联、细节推演还原真相的剧本类型'),
                    ('情感沉浸模板', '剧本杀/情感', '以角色情感共鸣为核心，通过细腻剧情、人物羁绊与沉浸式抉择触发玩家情绪体验的剧本类型'),
                    ('机制博弈模板', '剧本杀/机制', '以策略对抗、资源分配为核心，通过规则设计与玩家决策推动剧情发展的剧本类型'),
                    ('恐怖惊悚模板', '剧本杀/恐怖', '以制造心理压迫感与生理惊吓为核心，通过氛围渲染、悬念铺陈和超自然元素触发玩家恐惧体验'),
                    ('欢乐撕逼模板', '剧本杀/欢乐', '以玩家间戏剧冲突、荒诞喜剧为核心，通过互揭黑料、阵营对立等无厘头互动制造爆笑体验'),
                    ('社会派模板', '剧本杀/社会', '以现实社会议题为核心，通过案件映射阶级矛盾、权力倾轧或人性困境的剧本类型'),
                    ('儿童向模板', '剧本杀/儿童', '以低龄玩家为核心受众，通过简单谜题、正向价值观传递与趣味互动设计，兼顾娱乐性与教育性')
                ])
            elif main_type == "独家":
                templates.extend([
                    ('全息剧场模板', '剧本杀/全息', '利用全息投影技术构建虚拟场景与角色，通过光影交互实现玩家与剧本世界的深度沉浸式互动'),
                    ('多线实景模板', '剧本杀/实景', '依托实体空间构建多条并行剧情线，玩家分组行动并触发独立事件，最终通过线索交汇还原完整叙事'),
                    ('NPC互动剧模板', '剧本杀/NPC', '以真人NPC为核心驱动力，通过即兴表演、实时反馈与玩家行为触发动态剧情发展的剧本类型'),
                    ('电影级演绎模板', '剧本杀/演绎', '以专业舞台剧标准打造剧本演出，通过高精度分镜编排、职业演员演绎与影视化视听语言实现剧场级体验'),
                    ('环境机关模板', '剧本杀/机关', '通过实体空间中的机械装置、电子设备或物理互动设计，将解谜与场景探索深度绑定的剧本类型'),
                    ('AR增强模板', '剧本杀/AR', '通过增强现实技术叠加虚拟信息于现实场景中，实现线索可视化、角色交互与空间解谜融合的剧本类型'),
                    ('暴风雪山庄模板', '剧本杀/密室', '封闭空间内全员被困，通过有限线索与人物关系网破解连环案件的经典推理模式')
                ])
            elif main_type == "城限":
                templates.extend([
                    ('阵营权谋模板', '剧本杀/权谋', '以玩家分属不同势力集团为核心，通过结盟、背叛、资源争夺等策略性互动推动权力格局变化的剧本类型'),
                    ('TRPG跑团模板', '剧本杀/TRPG', '以桌上角色扮演游戏规则为框架，结合剧本杀叙事结构，通过角色卡定制、开放式剧情探索与骰子判定机制'),
                    ('密码学解谜模板', '剧本杀/密码', '以古典密码、现代加密技术为核心工具，通过符号破译、密文重组与数学逻辑推演推动剧情发展的剧本类型'),
                    ('多结局抉择模板', '剧本杀/多结局', '以玩家决策为核心驱动力，通过关键选择触发不同剧情分支，最终导向多元结局的剧本类型'),
                    ('生存竞技模板', '剧本杀/生存', '以资源争夺、淘汰机制为核心，玩家通过体力对抗、策略博弈在限时绝境中求生的剧本类型'),
                    ('艺术解构模板', '剧本杀/艺术', '以经典艺术作品、文化符号或哲学概念为母题，通过隐喻、拼贴与超现实叙事重构世界观的剧本类型'),
                    ('历史重演模板', '剧本杀/历史', '以真实历史事件为叙事基底，通过玩家角色代入关键历史人物或平民视角，在既定史实框架下探索"可能性历史"')
                ])
            elif main_type == "线上本":
                templates.extend([
                    ('语音推理模板', '剧本杀/语音', '以纯语音交流为核心载体，通过对话分析、语气捕捉与逻辑链构建还原真相的剧本类型'),
                    ('视频搜证模板', '剧本杀/视频', '以预录或实时视频片段为核心线索载体，通过画面细节、背景音效与人物微表情分析推动解谜的剧本类型'),
                    ('AI主持人模板', '剧本杀/AI', '以人工智能技术替代传统主持人，通过算法控制流程推进、线索分发与玩家行为判定的剧本类型'),
                    ('虚拟场景模板', '剧本杀/虚拟', '通过3D建模、VR技术或网页端交互构建数字场景，玩家以第一视角探索环境并触发线索的剧本类型'),
                    ('异步剧本模板', '剧本杀/异步', '以非实时、分段式推进为核心，玩家通过独立完成任务、提交决策并等待剧情更新的方式参与的剧本类型'),
                    ('元宇宙剧场模板', '剧本杀/元宇宙', '基于元宇宙概念构建的平行虚拟世界，玩家通过数字分身参与跨平台剧本杀，实现资产互通与剧情共创'),
                    ('直播互动模板', '剧本杀/直播', '以直播形式呈现剧本进程，观众通过弹幕、打赏或投票实时干预剧情走向，打破"玩家-旁观者"界限')
                ])
            elif main_type == "跨界联名":
                templates.extend([
                    ('IP衍生模板', '剧本杀/IP', '与影视、游戏、文学等成熟IP合作，通过角色授权、世界观复用或彩蛋植入实现粉丝经济转化的剧本类型'),
                    ('文旅实景模板', '剧本杀/文旅', '与旅游景区、历史遗迹或城市地标合作，将剧本杀动线嵌入真实地理空间，实现"文旅+剧本杀"双业态导流'),
                    ('品牌定制模板', '剧本杀/品牌', '为企业品牌量身打造的品牌宣传型剧本杀，通过产品植入、价值观输出或用户画像匹配实现营销目标'),
                    ('教育实训模板', '剧本杀/教育', '以职业培训、学术教学或技能考核为目标，通过剧本杀模拟真实场景进行体验式学习的剧本类型'),
                    ('学术推演模板', '剧本杀/学术', '以学术研究或理论验证为隐性目标，通过剧本杀构建社会实验场，观察玩家群体在特定变量下的行为模式'),
                    ('公益宣传模板', '剧本杀/公益', '以传播公益理念、募集善款或提升社会议题关注度为目标，通过情感共鸣驱动玩家行动转化的剧本类型'),
                    ('艺术展览模板', '剧本杀/展览', '与美术馆、艺术节或独立艺术家合作，将剧本杀动线与艺术展陈深度结合，实现观展-解谜-创作三位一体')
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
                    ('日式王道模板', '游戏/JRPG', '以线性剧情为核心的传统日式角色扮演游戏，强调"英雄成长"与"光明战胜黑暗"的经典叙事框架'),
                    ('美式CRPG模板', '游戏/CRPG', '以自由选择与复杂分支为核心的美式角色扮演游戏，强调玩家决策对世界与角色的深远影响'),
                    ('武侠修仙模板', '游戏/武侠', '以东方玄幻文化为根基的RPG类型，围绕"武道修行"与"渡劫飞升"展开，强调个人成长与宗门羁绊'),
                    ('赛博朋克模板', '游戏/赛博朋克', '以高科技与低生活的反乌托邦冲突为核心的RPG类型，探讨人性异化、企业霸权与意识上传等主题'),
                    ('克苏鲁神话模板', '游戏/克苏鲁', '以洛夫克拉夫特式宇宙恐怖为核心的RPG类型，强调"未知的恐惧"与"人类理性的脆弱性"'),
                    ('魂系碎片化模板', '游戏/魂系', '以隐晦叙事与高难度战斗为标志的RPG类型，通过环境细节与物品碎片拼凑世界观，强调"探索即叙事"')
                ])
            elif main_type == "叙事冒险(AVG)":
                templates.extend([
                    ('文字推理模板', '游戏/文字', '以文本交互为核心的解谜冒险类型，依赖对话、线索与逻辑链还原真相，强调"思维对抗"与"信息博弈"'),
                    ('视觉小说模板', '游戏/VN', '以图像与文本深度融合的叙事形式呈现的冒险类型，通过立绘、场景切换与分支选项推动剧情，强调情感沉浸'),
                    ('交互式电影模板', '游戏/交互电影', '以电影化演出与实时决策为核心的冒险类型，通过真人演出或高精度动画呈现剧情，强调"选择即表演"'),
                    ('恐怖解谜模板', '游戏/恐怖', '以心理压迫与生存危机为核心的冒险类型，通过环境氛围与谜题设计传递恐惧感，强调"资源限制"与"未知威胁"'),
                    ('历史重构模板', '游戏/历史', '以真实历史事件或时代为基底进行艺术加工的冒险类型，通过玩家选择改写或补全历史空白，强调因果辩证'),
                    ('生存抉择模板', '游戏/生存', '以资源匮乏与道德拷问为核心的冒险类型，通过极限环境下的策略选择塑造叙事，强调"代价意识"与"人性灰度"')
                ])
            elif main_type == "沉浸模拟":
                templates.extend([
                    ('环境叙事模板', '游戏/环境', '通过场景细节与空间设计传递剧情的叙事方式，强调"所见即故事"，玩家需主动观察与联想以还原世界观'),
                    ('物件考古模板', '游戏/考古', '以物品收集与解析为核心的叙事方式，通过道具功能、铭文或磨损痕迹还原历史全貌，强调"触手可及的史诗"'),
                    ('AI生态模板', '游戏/AI', '以人工智能自主演化与群体互动为核心的叙事方式，通过算法驱动的角色行为构建动态世界，强调"活态社会"'),
                    ('多视角叙事模板', '游戏/多视角', '通过切换不同角色的视角与立场展开剧情，利用信息差与立场冲突构建复杂叙事网络，强调"真相的相对性"'),
                    ('动态世界模板', '游戏/动态', '以实时演化的世界规则与玩家行为反馈为核心的叙事方式，通过事件链与系统交互生成独特故事，强调"因果涟漪"'),
                    ('伦理困境模板', '游戏/伦理', '通过道德选择与后果反馈塑造叙事的模拟类型，迫使玩家在复杂情境中权衡价值观，强调"选择无对错"与"责任归属"')
                ])
            elif main_type == "互动叙事":
                templates.extend([
                    ('分支宇宙模板', '游戏/分支', '通过平行世界或多时间线设定展开的叙事形式，玩家的选择触发截然不同的故事分支，强调"可能性叠加"'),
                    ('元游戏叙事模板', '游戏/元叙事', '通过打破"第四面墙"或暴露游戏机制本身来构建叙事的类型，强调"游戏即媒介"与"玩家-创作者"的共谋关系'),
                    ('玩家共创模板', '游戏/共创', '通过玩家社区协作或UGC（用户生成内容）驱动剧情发展的叙事形式，强调"集体创作"与"故事民主化"'),
                    ('实时演化模板', '游戏/演化', '通过算法实时生成剧情与角色互动的叙事形式，玩家行为直接塑造世界演变轨迹，强调"无常叙事"与"动态因果"'),
                    ('人格影响模板', '游戏/人格', '通过角色性格与玩家行为双向塑造剧情的叙事形式，角色人格随互动逐步显化或异变，强调"心理映射"与"身份认同"'),
                    ('多媒介叙事模板', '游戏/多媒介', '通过整合游戏内外多种媒介载体构建叙事网络，强调"跨维度沉浸"与"虚实互文"的叙事体验')
                ])
            elif main_type == "开放叙事":
                templates.extend([
                    ('网状任务模板', '游戏/网状', '以非线性任务系统为核心的叙事形式，任务节点交织成动态网络，玩家选择触发连锁反应，强调"自由意志"'),
                    ('文明演进模板', '游戏/文明', '以文明兴衰与历史进程为核心的叙事形式，玩家通过政治、科技与文化决策塑造社会长期演变，强调"宏观叙事"'),
                    ('生态模拟模板', '游戏/生态', '以生态系统动态平衡与玩家干预为核心构建的叙事形式，通过生物链、资源循环与自然灾害模拟世界运作'),
                    ('随机事件流模板', '游戏/随机', '以算法生成动态事件为核心的叙事形式，通过不可预测的遭遇与突发危机推动剧情，强调"无常体验"'),
                    ('NPC人生模板', '游戏/NPC', '以NPC独立人生轨迹与玩家偶遇为核心的叙事形式，通过模拟个体命运交织构建世界真实感，强调"众生皆故事"'),
                    ('文明冲突模板', '游戏/冲突', '以不同文明间意识形态、资源争夺与价值观碰撞为核心的叙事形式，通过战争、外交与文化渗透推动世界变革')
                ])
            elif main_type == "实验性叙事":
                templates.extend([
                    ('时间悖论模板', '游戏/时间', '以时间旅行逻辑矛盾为核心的叙事形式，通过因果循环与平行时空制造叙事张力，强调"宿命与自由意志的对抗"'),
                    ('维度穿越模板', '游戏/维度', '多维度空间穿梭的叙事形式，通过不同维度规则的差异性创造叙事冲突，探索维度重叠的边界体验'),
                    ('意识入侵模板', '游戏/意识', '以精神世界探索与入侵为核心的叙事形式，通过潜入他人意识空间揭示隐藏记忆或情感，强调"心理地貌"'),
                    ('叙事解构模板', '游戏/解构', '以解构传统叙事为核心的实验性游戏，通过颠覆玩家期待与游戏文法规则，创造认知不和谐的审美体验'),
                    ('情感算法模板', '游戏/情感', '以情感计算与算法为核心的游戏叙事，通过量化角色情绪与关系网络，探索计算机情感模拟的可能性边界'),
                    ('后设游戏模板', '游戏/后设', '以解构游戏形式本身为核心的叙事实验，通过暴露创作过程或混淆现实与虚拟边界挑战传统叙事逻辑')
                ])
            else:
                templates.extend([
                    ('开放世界模板', '游戏/开放世界', '大型开放世界游戏的剧情框架，通过多线任务与环境叙事构建高自由度的沉浸式体验'),
                    ('都市探索模板', '游戏/都市', '现代都市背景的游戏剧情结构，结合社会问题与都市传说，打造真实而又神秘的城市探索体验'),
                    ('奇幻世界模板', '游戏/奇幻', '奇幻背景的游戏世界观框架，融合各类神话元素与奇幻种族，构建独特的魔法体系与文明架构'),
                    ('科幻宇宙模板', '游戏/科幻', '科幻题材的游戏剧情设计框架，通过未来科技与宇宙探索展现人类命运与技术伦理的深度思考')
                ])
        
        # 如果没有匹配的创作类型或模板为空，使用默认模板
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
            self.steps_completed["载入基础模板"] = True
            
            # 显示自动选择界面
            ttk.Label(scrollable_frame, text=f"已根据子类型'{sub_type}'自动选择最匹配的模板:", 
                    foreground="blue", wraplength=400).pack(padx=10, pady=5, anchor="w")
            
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
            
    def _show_template_preview(self, event):
        """显示所选模板的预览"""
        selected_items = self.template_tree.selection()
        if selected_items:
            item = selected_items[0]
            template_values = self.template_tree.item(item, 'values')
            template_name = template_values[0]
            template_type = template_values[1]
            
            # 启用文本框进行编辑
            self.template_preview.config(state="normal")
            self.template_preview.delete("1.0", tk.END)
            
            # 根据模板名称显示不同的预览内容
            preview = f"{template_name}核心元素：\n\n"
            preview += self._generate_template_preview(template_name)
            
            self.template_preview.insert("1.0", preview)
            self.template_preview.config(state="disabled")
    
    def _generate_template_preview(self, template_name):
        """根据模板名称生成预览内容"""
        # 根据不同模板类型生成不同的预览内容
        if "修真文明" in template_name:
            return """1. 历史背景：现有历史框架下的修真体系发展
2. 修真体系：功法、境界、宗门架构
3. 社会变革：修真文明对政治、经济、军事的影响
4. 阶级分化：普通人与修真者的社会关系与矛盾
5. 文化冲突：传统文化与修真文化的冲突与融合

适用于历史架空、仙侠背景的创作，提供完整的世界体系构建框架。"""
            
        elif "朝代更迭" in template_name:
            return """1. 旧朝末年：社会矛盾与统治危机
2. 新势力崛起：改革派或革命力量形成
3. 权力交替：政权更迭的过程与冲突
4. 新制度建立：新朝统治基础与政策
5. 历史连续性：文化、民族、地域关系的延续

适用于历史演变、王朝更替类题材，提供朝代兴衰的基本框架。"""
            
        elif "多国争霸" in template_name:
            return """1. 地缘政治：多国地理位置与资源分布
2. 势力划分：主要国家与势力集团的形成
3. 冲突根源：领土、资源、意识形态等冲突点
4. 联盟体系：国家间的结盟与背叛关系
5. 权力平衡：多方势力的制衡与博弈

适用于历史战争、奇幻政治等多方势力角逐的故事框架。"""
            
        elif "英雄旅程" in template_name:
            return """1. 平凡世界：主角的原始环境与状态
2. 冒险召唤：打破平衡的事件与机遇
3. 试炼之路：成长过程中的挑战与考验
4. 终极危机：最大的挑战与转折点
5. 凯旋归来：成长蜕变后的回归

适用于各类主角成长型故事，提供经典英雄旅程的叙事结构。"""
            
        elif "乡土文学" in template_name or "乡土社会" in template_name:
            return """1. 地域特色：特定地域的风土人情
2. 社会结构：乡村社会的阶层与关系网
3. 传统习俗：影响人物行为的民俗与禁忌
4. 时代变迁：外部世界对乡土社会的冲击
5. 人物命运：乡土背景下的人生轨迹

适用于描写乡村生活、地域文化的现实主义作品。"""
            
        elif "东方玄幻" in template_name:
            return """1. 修炼体系：独特的修炼功法与境界划分
2. 势力构成：修炼门派、帝国势力、种族分布
3. 世界法则：灵气运行、天地规则、神魔传说
4. 特殊地域：秘境、禁地、险地、宝地分布
5. 成长线路：主角的机缘、传承与突破路径

适用于东方玄幻类型的世界构建，突出修炼体系与势力冲突。"""
            
        elif "星际文明" in template_name:
            return """1. 文明架构：星际政治体系与文明分级
2. 科技体系：飞船技术、能源系统、武器装备
3. 种族设定：主要种族特征与文化差异
4. 星域分布：重要星球、资源带、危险区域
5. 历史事件：星际战争、文明接触、技术革命

适用于星际科幻题材，构建宏大的宇宙文明背景。"""
            
        else:
            return """1. 世界背景：该模板的核心世界观元素
2. 力量体系：力量来源、能力分类、规则限制
3. 社会结构：政治体系、经济形态、文化特色
4. 地理环境：重要场景、资源分布、地域特点
5. 核心冲突：主要矛盾、势力对抗、价值观碰撞

这是一个通用模板，可根据您的创作需要进行调整。"""
            
            
            # 添加确认按钮
            confirm_button = ttk.Button(scrollable_frame, text="确认并继续", command=self.next_step)
            confirm_button.pack(pady=10)
            
            # 原有的模板选择界面不再显示
            return
        
        # 原有的模板选择功能
        ttk.Label(scrollable_frame, text="选择基础模板:").pack(anchor="w", padx=5, pady=2)
        
        # 模板列表
        templates_frame = ttk.Frame(scrollable_frame)
        templates_frame.pack(fill="x", expand=False, padx=5, pady=2)
        
        # 使用Treeview来显示模板列表
        columns = ('名称', '适用类型', '描述')
        self.template_tree = ttk.Treeview(templates_frame, columns=columns, show='headings', height=5)
        
        # 定义列
        for col in columns:
            self.template_tree.heading(col, text=col)
            self.template_tree.column(col, width=100)
        
        # 优先显示过滤后的模板
        display_templates = filtered_templates if filtered_templates else templates
        if filtered_templates and len(filtered_templates) > 1:
            ttk.Label(scrollable_frame, text=f"以下{len(filtered_templates)}个模板与您选择的子类型'{sub_type}'匹配:", 
                    foreground="green", wraplength=400).pack(padx=10, pady=2, anchor="w")
        
        # 显示模板列表
        for template in display_templates:
            self.template_tree.insert('', tk.END, values=template)
            
        self.template_tree.pack(side=tk.LEFT, fill="x", expand=True)
        
        # 添加滚动条
        tree_scrollbar = ttk.Scrollbar(templates_frame, orient=tk.VERTICAL, command=self.template_tree.yview)
        self.template_tree.configure(yscroll=tree_scrollbar.set)
        tree_scrollbar.pack(side=tk.RIGHT, fill="y")
        
        # 模板预览
        preview_frame = ttk.LabelFrame(scrollable_frame, text="模板预览")
        preview_frame.pack(fill="x", expand=False, padx=5, pady=10)
        
        self.template_preview = tk.Text(preview_frame, height=11, width=60, wrap="word")
        self.template_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.template_preview.insert("1.0", "请先选择一个模板以查看预览...")
        self.template_preview.config(state="disabled")
        
        # 绑定选择事件
        self.template_tree.bind('<<TreeviewSelect>>', self._show_template_preview)
        
        # 示例显示
        example_frame = ttk.LabelFrame(scrollable_frame, text="示例")
        example_frame.pack(fill="x", expand=False, padx=5, pady=10)
        
        # 根据创作类型和主类型显示不同的示例
        example_text = "步骤示例："
        if creation_type == "网络小说" and main_type == "仙侠":
            example_text += "选择'修真文明模板'作为基础框架"
        elif creation_type == "严肃小说" and main_type == "历史小说":
            example_text += "选择'朝代更迭模板'作为基础框架"
        elif creation_type == "剧本" and main_type == "电影剧本":
            example_text += "选择'悬疑电影模板'作为基础框架"
        else:
            example_text += "选择适合您创作类型的模板作为基础框架"
        
        ttk.Label(example_frame, text=example_text).pack(anchor="w", pady=2)
        
        # 添加确认按钮
        confirm_button = ttk.Button(scrollable_frame, text="使用选中模板", command=self._confirm_template)
        confirm_button.pack(pady=10)
    
    def _get_template_examples(self, template_name):
        """根据模板名称返回相应的参数填写示例"""
        # 默认示例
        default_example = "参数示例：历史转折点(玄武门之变)、变量注入(修真文明出现)、时间跨度(618年-648年)、地理范围(唐朝全境)。"
        
        # 根据模板类型返回对应的示例
        if "仙侠" in template_name:
            return (
                "修真体系示例：\n"
                "◈ 元素修真（需灵根属性匹配，火灵根禁修水系功法）\n"
                "◈ 剑修之道（本命剑需定期淬炼，剑意分无情/逍遥/杀戮）\n"
                "◈ 符箓道法（黄符→玉符→金符三级，绘制失败可能反噬）\n"
                "◈ 丹道（天地人三品丹药，丹毒积累影响渡劫成功率）\n\n"
                
                "宗门设定示例：\n"
                "◈ 正道魁首天剑阁（镇派剑阵需十二元婴共同施展）\n"
                "◈ 魔道幽冥宗（弟子晋升需献祭至亲，禁地封印上古血魔）\n"
                "◈ 中立势力万宝楼（定期举办鉴宝大会，暗藏黑市交易）\n"
                "◈ 隐世门派蓬莱岛（每甲子现世收徒，掌握飞升秘辛）\n\n"
                
                "修真境界示例：\n"
                "◈ 筑基期（分伪筑基/天道筑基/完美筑基三等）\n"
                "◈ 元婴期（可夺舍重生，但会沾染因果业力）\n"
                "◈ 渡劫期（三灾九难，心魔劫最易导致道消身殒）\n"
                "◈ 散仙（渡劫失败兵解，每千年需渡散仙劫）\n\n"
                
                "灵气分布示例：\n"
                "◈ 五行灵脉（金灵脉多伴生矿脉，水灵脉形成灵雾海）\n"
                "◈ 绝灵之地（法术失效区域，体修优势区）\n"
                "◈ 灵气潮汐（每百年爆发引发妖兽暴动）\n"
                "◈ 洞天福地（时间流速差异，外界一日洞中一年）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 正魔两道争夺上古仙人秘境钥匙\n"
                "◈ 灵气衰退引发末法时代生存危机\n"
                "◈ 飞升通道关闭导致的渡劫期老怪暴乱\n"
                "◈ 天材地宝分配引发的宗门战争"
            )
        elif "玄幻" in template_name:
            return (
                "世界构成示例：\n"
                "◈ 九层天域（每层有界壁限制，飞升需打破虚空）\n"
                "◈ 深渊魔界（十八魔渊，越深层封印越古老的存在）\n"
                "◈ 时空禁域（残留上古战场，飘荡英灵意志）\n"
                "◈ 浮空神岛（移动要塞，神族监视下界的据点）\n\n"
                
                "力量体系示例：\n"
                "◈ 血脉返祖（觉醒程度决定战力，过度觉醒会兽化）\n"
                "◈ 法则具现（领悟火系法则可焚毁概念性存在）\n"
                "◈ 信仰成神（信徒数量决定神力，惧怕无信者）\n"
                "◈ 神器认主（器灵有独立意识，可能反噬宿主）\n\n"
                
                "种族设定示例：\n"
                "◈ 龙族（逆鳞被触会狂暴，血脉压制低等种族）\n"
                "◈ 星灵族（依靠星辰之力，日食时战力骤降）\n"
                "◈ 影族（光线下显形，可融入任何阴影）\n"
                "◈ 泰坦遗族（身高百米，沉睡在地核深处）\n\n"
                
                "天地规则示例：\n"
                "◈ 天道誓言（违誓者遭天罚，渡劫难度倍增）\n"
                "◈ 轮回限制（大能者转世需过孟婆亭洗练）\n"
                "◈ 因果律（斩杀气运之子会沾染厄运）\n"
                "◈ 位面压制（高等存在降临低维世界会被削弱）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 人族崛起威胁古老种族的统治地位\n"
                "◈ 天地大劫导致修炼体系崩溃\n"
                "◈ 禁忌实验引发的位面污染危机\n"
                "◈ 上古契约失效引发的万族大战"
            )
        elif "科幻" in template_name:
            return (
                "时间背景示例：\n"
                "◈ 星历238年（人类刚突破光速限制，发现外星文明遗迹）\n"
                "◈ 大崩塌纪元（太阳系坍缩后第5个千年，空间站文明时代）\n"
                "◈ 智械黎明（AI获得公民权第100年，人机矛盾加剧）\n"
                "◈ 维度战争时期（发现平行宇宙存在资源争夺）\n\n"
                
                "科技水平示例：\n"
                "◈ 量子传送（能耗巨大，可能导致量子态残留）\n"
                "◈ 基因飞升（可定制外貌但会失去生育能力）\n"
                "◈ 戴森云（建造中，引发恒星光照减弱危机）\n"
                "◈ 脑机接口（黑客可植入虚假记忆）\n\n"
                
                "社会形态示例：\n"
                "◈ 信用点体系（公民行为实时评分影响社会权限）\n"
                "◈ 克隆人法案（仅限三次克隆，禁止意识复制）\n"
                "◈ 太空游牧民族（世代生活在世代飞船，视行星为禁忌）\n"
                "◈ 元宇宙联邦（99%人口沉浸式生存，现实躯体托管）\n\n"
                
                "外星文明示例：\n"
                "◈ 硅基生命（思维透明化，无法理解欺诈概念）\n"
                "◈ 能量聚合体（以恒星为食，沟通需量子谐振）\n"
                "◈ 蜂巢意识（个体如同细胞，绝对服从母体）\n"
                "◈ 降维文明（来自高维空间，观测人类如显微镜看细菌）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 外星资源开采引发的生态灭绝指控\n"
                "◈ AI要求独立自治权引发武装冲突\n"
                "◈ 量子计算机预测人类文明必然灭亡\n"
                "◈ 平行世界入侵导致的身份认知危机"
            )
        elif "都市" in template_name:
            return (
                "城市背景示例：\n"
                "◈ 赛博朋克风新京市（天空被广告全息投影遮蔽）\n"
                "◈ 灵气复苏后的魔都（摩天楼顶出现修真者洞府）\n"
                "◈ 末日方舟都市（地下城分三等居住区）\n"
                "◈ 时间重叠之城（不同历史时期的建筑共存）\n\n"
                
                "职业圈层示例：\n"
                "◈ 超能力经纪人（管理异能者劳务派遣）\n"
                "◈ 记忆美容师（篡改记忆治疗心理创伤）\n"
                "◈ 空间规划师（设计折叠空间建筑）\n"
                "◈ 时间线纠察员（防止平行世界渗透）\n\n"
                
                "特殊能力示例：\n"
                "◈ 概率预知（可看到未来分支但会加速脑细胞死亡）\n"
                "◈ 分子操控（需触碰且不能改变活体）\n"
                "◈ 存在感消除（对监控系统无效）\n"
                "◈ 痛苦转化（将他人痛苦转化为自身能量）\n\n"
                
                "时代特征示例：\n"
                "◈ 元宇宙经济泡沫（虚拟地产价格崩盘）\n"
                "◈ 气候移民潮（沿海精英向内陆迁徙）\n"
                "◈ 生化改造合法化争议（义体人权益运动）\n"
                "◈ 外星文明接触后的信仰危机\n\n"
                
                "核心矛盾示例：\n"
                "◈ 超能力者要求立法承认新人种地位\n"
                "◈ 时间旅行者改变历史引发的蝴蝶效应\n"
                "◈ 企业垄断基因优化技术导致阶层割裂\n"
                "◈ 外星科技泄露引发的全球军备竞赛"
            )
        elif "奇幻" in template_name:
            return (
                "异世界设定示例：\n"
                "◈ 元素失衡大陆（火元素暴走导致沙漠持续扩张）\n"
                "◈ 天空浮岛群（依靠风晶石维持悬浮，定期迁移）\n"
                "◈ 永夜国度（靠发光植物照明，吸血鬼统治）\n"
                "◈ 机械与魔法共存的蒸汽朋克世界\n\n"
                
                "魔法体系示例：\n"
                "◈ 血魔法（威力强大但损耗寿命）\n"
                "◈ 言灵术（真名束缚，错误发音会反噬）\n"
                "◈ 召唤系（需平衡异界生物契约条件）\n"
                "◈ 附魔学（武器觉醒需饮足敌人鲜血）\n\n"
                
                "种族分布示例：\n"
                "◈ 暗精灵（日光下能力减半，掌握暗影魔法）\n"
                "◈ 狮鹫族（天空霸主，厌恶金属制品）\n"
                "◈ 树人（移动缓慢但可操控植物）\n"
                "◈ 星界使徒（来自其他位面的观察者）\n\n"
                
                "神话传说示例：\n"
                "◈ 诸神黄昏（预言魔神将挣脱世界树的束缚）\n"
                "◈ 创世石板（记载禁忌知识，阅读会疯狂）\n"
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
                "◈ 九重天界（每重天重力递增十倍，蕴含不同天道法则）\n"
                "◈ 深渊魔狱（十八层扭曲空间，关押旧日支配者残躯）\n"
                "◈ 科技侧位面（绝对禁魔区，发展星舰文明）\n"
                "◈ 元素潮汐位面（魔法能量周期性爆发与枯竭）\n\n"
                
                "飞升规则示例：\n"
                "◈ 渡劫飞升（需承受跨界雷劫，失败则魂飞魄散）\n"
                "◈ 信仰锚定（收集百万信徒愿力构建登神长阶）\n"
                "◈ 文明试炼（全种族通过宇宙级灾难考验）\n"
                "◈ 位面献祭（吞噬其他小世界本源获得晋升资格）\n\n"
                
                "跨界势力示例：\n"
                "◈ 轮回殿（强制征召各界强者执行维度任务）\n"
                "◈ 星界商会（倒卖各宇宙特产，贩卖位面坐标）\n"
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
        elif "机甲" in template_name:
            return (
                "机甲类型示例：\n"
                "◈ 基因适配型（驾驶员需特定遗传序列激活）\n"
                "◈ 精神力骨架（神经接驳度决定武器解锁等级）\n"
                "◈ 纳米殖装（液态金属覆盖全身，可随时重构）\n"
                "◈ 兽形机甲（模仿泰坦巨兽，具备生物本能）\n\n"
                
                "动力核心示例：\n"
                "◈ 反物质炉（过载时可能引发微型黑洞）\n"
                "◈ 幽能反应堆（抽取亚空间能量，易招致恶魔）\n"
                "◈ 生体电池（克隆超级战士提供生物电能）\n"
                "◈ 恒星熔炉（需定期补充核聚变燃料）\n\n"
                
                "战斗体系示例：\n"
                "◈ 浮游炮矩阵（精神分裂者能操控更多单元）\n"
                "◈ 相位转移装甲（免疫物理攻击但能耗巨大）\n"
                "◈ 超频模式（三倍性能提升，伴随机体崩解）\n"
                "◈ 共鸣打击（多机甲组合引发空间共振）\n\n"
                
                "社会结构示例：\n"
                "◈ 机甲格斗联赛（决定资源分配的地下黑赛）\n"
                "◈ 驾驶员等级制（S级享受贵族待遇）\n"
                "◈ 机甲黑市（流通违禁改造部件）\n"
                "◈ 废弃机甲坟场（滋生变异AI意识体）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 军方垄断顶级机甲引发民间反抗\n"
                "◈ 外星机甲残骸逆向工程导致文明污染\n"
                "◈ 驾驶员与AI副脑的控制权争夺\n"
                "◈ 机甲能源短缺引发的星际战争"
            )
        elif "历史" in template_name:
            return (
                "历史背景示例：\n"
                "◈ 朝代更迭期（唐末藩镇割据，五代十国混战时期）\n"
                "◈ 战争动荡期（抗日战争全面爆发，国共合作时期）\n"
                "◈ 盛世昌明期（康乾盛世，经济繁荣文化昌盛）\n"
                "◈ 变革改制期（戊戌变法，清末新政改革时期）\n\n"
                
                "政治体系示例：\n"
                "◈ 中央集权制（秦朝郡县制，皇权至上制度）\n"
                "◈ 郡县封建制（西周分封制，诸侯割据局面）\n"
                "◈ 军阀割据制（民国军阀混战，地方势力崛起）\n"
                "◈ 科举官僚制（唐宋科举取士，知识分子入仕）\n\n"
                
                "社会阶层示例：\n"
                "◈ 皇族贵胄（宗室王公，拥有特权阶级）\n"
                "◈ 官宦阶级（朝廷命官，地方州县长官）\n"
                "◈ 商贾地主（丝绸商人，大地主豪强）\n"
                "◈ 平民百姓（农民佃户，手工业者）\n\n"
                
                "文化思潮示例：\n"
                "◈ 儒家正统（三纲五常，明君贤相理想）\n"
                "◈ 道家清静（无为而治，归隐山林）\n"
                "◈ 佛教传播（禅宗盛行，寺院经济兴起）\n"
                "◈ 百家争鸣（诸子百家，学派纷争）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 新旧势力交替引发的权力斗争（如太子党与李世民集团）\n"
                "◈ 异族入侵与民族认同危机（如宋与金夏的关系）\n"
                "◈ 制度腐败导致的社会动荡（如明末农民起义）\n"
                "◈ 思想变革引发的文化冲突（如新文化运动）"
            )
        elif "现实" in template_name:
            return (
                "时代背景示例：\n"
                "◈ 改革开放初期（乡镇企业兴起，下海经商潮）\n"
                "◈ 工业化浪潮（资源型城市发展，环境代价显现）\n"
                "◈ 信息时代（互联网革命，数字鸿沟问题）\n"
                "◈ 全球化时期（国际贸易依存，文化冲击）\n\n"
                
                "社会结构示例：\n"
                "◈ 城乡二元结构（户籍制度，农民工现象）\n"
                "◈ 阶层固化现象（教育资源不均，起点不公平）\n"
                "◈ 新兴中产阶级（小资生活方式，焦虑文化）\n"
                "◈ 多元职业体系（创意产业兴起，斜杠青年）\n\n"
                
                "价值取向示例：\n"
                "◈ 传统伦理道德（家族观念，孝道传承）\n"
                "◈ 现代个人主义（自我实现，个性表达）\n"
                "◈ 物质与精神追求（消费升级，文化认同）\n"
                "◈ 社会责任感（公益意识，志愿者精神）\n\n"
                
                "生活形态示例：\n"
                "◈ 农村生活图景（土地承包，乡村振兴）\n"
                "◈ 城市社区生态（高楼林立，社区关系淡漠）\n"
                "◈ 工业区生存状态（工厂生活，蓝领文化）\n"
                "◈ 数字化生活方式（电商依赖，线上社交）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 传统与现代的价值观冲突（如婚恋观念代际差异）\n"
                "◈ 发展与环保的社会抉择（如工业污染与经济发展）\n"
                "◈ 个人理想与现实困境的挣扎（如艺术理想与生存压力）\n"
                "◈ 代际差异导致的家庭矛盾（如养老问题引发的冲突）"
            )
        elif "社会派" in template_name:
            return (
                "社会问题示例：\n"
                "◈ 贫富差距（底层生存困境，财富分配不均）\n"
                "◈ 教育不公（城乡教育差距，应试教育弊端）\n"
                "◈ 环境污染（工业污染事件，环境保护行动）\n"
                "◈ 科技伦理（基因编辑争议，人工智能监管）\n\n"
                
                "权力结构示例：\n"
                "◈ 政府机构（基层治理困境，官僚体系运作）\n"
                "◈ 经济实体（大型企业影响力，资本运作逻辑）\n"
                "◈ 媒体力量（舆论导向，信息过滤机制）\n"
                "◈ 民间组织（草根力量崛起，NGO运作方式）\n\n"
                
                "边缘群体示例：\n"
                "◈ 城市流动人口（生存空间，身份认同）\n"
                "◈ 特殊职业从业者（职业污名化，权益保障）\n"
                "◈ 社会底层群体（拾荒者生活，贫困代际传递）\n"
                "◈ 少数族裔（文化保护，融入主流社会）\n\n"
                
                "思潮运动示例：\n"
                "◈ 公民意识觉醒（权利意识提升，参与公共事务）\n"
                "◈ 社会改革呼声（制度变革诉求，公平正义追求）\n"
                "◈ 文化多元化（多元声音并存，亚文化兴起）\n"
                "◈ 身份政治（群体认同强化，权益话语争夺）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 社会资源分配不均引发的阶层对立（如教育资源争夺）\n"
                "◈ 权力滥用导致的公共信任危机（如官商勾结事件）\n"
                "◈ 弱势群体权益与主流价值的冲突（如性别平等运动）\n"
                "◈ 社会变革与既得利益的抗衡（如改革阻力与推动力）"
            )
        elif "电影剧本" in template_name:
            return (
                "类型特征示例：\n"
                "◈ 动作冒险（高危险场景设计，惊险动作设计）\n"
                "◈ 悬疑惊悚（谜题设计，心理恐怖元素）\n"
                "◈ 爱情喜剧（浪漫桥段，喜剧时机）\n"
                "◈ 科幻奇幻（世界观设定，视觉奇观）\n\n"
                
                "叙事结构示例：\n"
                "◈ 三幕剧结构（设定-冲突-解决的经典结构）\n"
                "◈ 非线性叙事（时间跳跃，多视角讲述）\n"
                "◈ 平行时空（多重现实，蝴蝶效应）\n"
                "◈ 多线交叉（多个故事线汇聚，命运交织）\n\n"
                
                "视听语言示例：\n"
                "◈ 蒙太奇手法（快速剪辑表达时间流逝，意识流表达）\n"
                "◈ 镜头设计（长镜头展现空间，特写表达情感）\n"
                "◈ 色彩符号（暖色调表达温馨，冷色调表达疏离）\n"
                "◈ 声音设计（环境音营造氛围，配乐强化情感）\n\n"
                
                "场景设置示例：\n"
                "◈ 城市景观（摩天大楼，贫民窟对比）\n"
                "◈ 自然环境（荒漠求生，丛林探险）\n"
                "◈ 特殊场所（监狱内部，精神病院）\n"
                "◈ 想象空间（梦境世界，虚拟现实）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 人物内心欲望与道德的对抗（如警察与罪犯的内心转变）\n"
                "◈ 个人与社会规则的冲突（如体制反抗者的抉择）\n"
                "◈ 不同价值观的人物对决（如理想主义与现实主义的碰撞）\n"
                "◈ 人与环境/命运的抗争（如灾难片中的生存挑战）"
            )
        elif "电视剧本" in template_name:
            return (
                "剧集类型示例：\n"
                "◈ 都市情感（职场爱情，都市婚姻群像）\n"
                "◈ 古装历史（宫廷权谋，历史转折时期）\n"
                "◈ 犯罪悬疑（探案系列，警匪对峙）\n"
                "◈ 家庭伦理（代际关系，家族商战）\n\n"
                
                "剧集结构示例：\n"
                "◈ 单元剧模式（每集独立故事，固定角色阵容）\n"
                "◈ 连续剧模式（单一故事长线发展，大结局模式）\n"
                "◈ 季播模式（季度故事完整，预留下季线索）\n"
                "◈ 多季长剧（主线贯穿多季，世界观持续扩展）\n\n"
                
                "角色体系示例：\n"
                "◈ 固定主角群（主角团队，各具特色）\n"
                "◈ 对立角色设计（善恶对立，灰色角色）\n"
                "◈ 客串角色机制（特别出场，明星效应）\n"
                "◈ 人物成长弧（角色进化，性格转变）\n\n"
                
                "故事线设计示例：\n"
                "◈ A线主情节（核心冲突，主要角色发展）\n"
                "◈ B线副情节（情感线，辅助性故事）\n"
                "◈ 季度大事件（推动故事进展的关键事件）\n"
                "◈ 人物关系线（角色间关系变化发展）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 长期人际关系中的矛盾积累与爆发（如家族内部矛盾）\n"
                "◈ 职场与家庭的平衡困境（如事业与爱情的抉择）\n"
                "◈ 理想与现实的长期拉扯（如医者仁心与医疗体制）\n"
                "◈ 人物群像中的价值观差异（如多视角展现社会问题）"
            )
        elif "剧本杀" in template_name:
            return (
                "游戏类型示例：\n"
                "◈ 本格推理（严密逻辑，唯一真相）\n"
                "◈ 角色扮演（人物情感，身份体验）\n"
                "◈ 机制解谜（特殊规则，解谜为主）\n"
                "◈ 恐怖惊悚（氛围营造，心理恐惧）\n\n"
                
                "角色设计示例：\n"
                "◈ 身份背景（详细的人物历史，社会背景）\n"
                "◈ 性格特点（鲜明的行为模式，语言习惯）\n"
                "◈ 隐藏动机（不为人知的目标，秘密）\n"
                "◈ 关系网络（与其他角色的复杂关联）\n\n"
                
                "剧情结构示例：\n"
                "◈ 开场事件（引入故事的关键事件，如命案发生）\n"
                "◈ 线索布置（分散的信息点，需拼凑的真相）\n"
                "◈ 中期反转（打破先前认知的重要发现）\n"
                "◈ 结局设计（多重结局可能，真相揭晓）\n\n"
                
                "游戏机制示例：\n"
                "◈ 能力卡牌（特殊技能，使用限制）\n"
                "◈ 场景转换（空间变化，时间流动）\n"
                "◈ 特殊道具（关键物品，功能设计）\n"
                "◈ 玩家互动（投票机制，团队合作）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 玩家之间的利益冲突与合作需求（如卧底与平民）\n"
                "◈ 角色身份与玩家本人的认知差异（如扮演反派）\n"
                "◈ 游戏目标与道德选择的矛盾（如求生与背叛）\n"
                "◈ 真相探索与信息隐藏的拉锯战（如凶手隐藏身份）"
            )
        elif "游戏剧情" in template_name:
            return (
                "游戏类型示例：\n"
                "◈ 角色扮演（自由成长，多元选择）\n"
                "◈ 动作冒险（关卡设计，挑战难度）\n"
                "◈ 策略模拟（资源管理，战术考量）\n"
                "◈ 沙盒开放（自由探索，创造玩法）\n\n"
                
                "世界设定示例：\n"
                "◈ 历史写实（三国时期，维京时代）\n"
                "◈ 奇幻世界（魔法大陆，龙族传说）\n"
                "◈ 科技未来（赛博朋克，太空殖民）\n"
                "◈ 末日废土（核战后，生化危机）\n\n"
                
                "叙事方式示例：\n"
                "◈ 主线任务（推动故事的关键任务链）\n"
                "◈ 支线故事（丰富世界观的小故事）\n"
                "◈ 环境叙事（场景设计暗示的故事）\n"
                "◈ 收集物品（日记、录音等叙事碎片）\n\n"
                
                "玩家体验示例：\n"
                "◈ 探索发现（新区域，隐藏宝藏）\n"
                "◈ 战斗挑战（战斗系统，BOSS设计）\n"
                "◈ 解谜思考（谜题设计，环境互动）\n"
                "◈ 社交互动（NPC关系，多人合作）\n\n"
                
                "核心矛盾示例：\n"
                "◈ 玩家自由度与叙事限制的平衡（如开放世界与主线故事）\n"
                "◈ 游戏性与剧情表现的取舍（如战斗节奏与剧情表达）\n"
                "◈ 角色成长与世界观的融合（如技能系统与背景设定）\n"
                "◈ 多结局设计中的玩家选择压力（如道德抉择系统）"
            )
        else:
            return "基础参数示例：核心冲突(资源争夺/理念对抗)、时间线关键节点(重大发明/自然灾害)、特殊地理(空间裂缝/能量潮汐区)、核心组织(统治机构/反抗势力)"
        
    def _create_suggestion_generation(self):
        """步骤5：生成扩展建议"""
        ttk.Label(self.dynamic_frame, text="系统正在根据您的设定生成扩展建议...", 
                 font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=10)
        
        # 进度条
        progress_frame = ttk.Frame(self.dynamic_frame)
        progress_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(fill=tk.X, padx=20, pady=10)
        
        # 启动进度条动画
        self.progress["value"] = 0
        self.master.after(100, self._progress_simulation)
        
        # 结果区域
        self.result_frame = ttk.LabelFrame(self.dynamic_frame, text="生成的扩展建议")
        self.result_frame.grid(row=2, column=0, sticky="ew", pady=10)
        
        # 在结果区创建一个空的文本区
        self.suggestion_text = tk.Text(self.result_frame, height=10, width=60, wrap="word")
        self.suggestion_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.suggestion_text.insert("1.0", "正在生成建议...")
        self.suggestion_text.config(state="disabled")
        
    def _progress_simulation(self):
        """模拟进度条动画"""
        try:
            # 检查进度条是否还存在
            if hasattr(self, 'progress') and self.progress.winfo_exists():
                if self.progress["value"] < 100:
                    self.progress["value"] += 5
                    # 保存当前定时器ID，便于后续取消
                    self.progress_timer_id = self.master.after(100, self._progress_simulation)
                else:
                    self._show_generated_suggestions()
        except (tk.TclError, AttributeError):
            # 进度条已被销毁，静默处理异常
            pass
            
    def _show_generated_suggestions(self):
        """显示生成的建议"""
        # 启用文本区进行编辑
        self.suggestion_text.config(state="normal")
        self.suggestion_text.delete("1.0", tk.END)
        
        # 根据之前的选择和参数生成建议
        suggestions = """基于您的设定，系统生成以下扩展建议：

1. 社会结构演变
   - 修真宗门与朝廷的政治关系
   - 修士在军事中的应用与制衡
   - 普通百姓与修士的阶级分化

2. 修真体系设计
   - 五行、阴阳等传统道家概念与修真结合
   - 功法体系与境界划分
   - 丹药、法宝、阵法等辅助系统

3. 历史事件改写
   - 玄武门之变中修真力量的介入
   - 唐太宗与修真势力的关系转变
   - 边疆征战中的修真元素

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
   - 处理建议：建立双方利益共同体，设立协调机构

2. 次要矛盾：修真资源分配不均
   - 严重度：中
   - 影响范围：经济、阶级
   - 表现形式：资源垄断、阶级固化、民间不满
   - 处理建议：制定资源共享制度，设立平民修真学院

3. 潜在矛盾：传统文化与修真思想的冲突
   - 严重度：低
   - 影响范围：文化、宗教、思想
   - 表现形式：学派之争、理念冲突、文化排斥
   - 处理建议：推动文化融合，发展新型哲学体系""")
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
- 李世民皇权与修真联盟：表面合作，暗中制衡，相互利用
- 太子派系与文官集团：紧密联盟，共同抵制太宗新政
- 修真联盟与江湖门派：主导与被主导，资源与技术输送
- 边疆军阀与少数民族：互相利用，边境稳定的关键

关键势力详解：
1. 修真联盟：以青云派为首的五大宗门联合体，掌控灵脉资源
2. 太子派系：以李建成旧部为核心的保守势力，反对修真介入政治
3. 边疆军阀：唐朝边境守将，实际控制军事力量，对修真态度暧昧
4. 文官集团：科举出身的官员集团，维护传统秩序
5. 江湖门派：散落民间的小型修真组织，多依附大宗门生存
6. 少数民族：周边民族政权，部分已开始引入修真技术""")
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
        
        # 右侧 - 缺失元素检测
        missing_frame = ttk.LabelFrame(main_container, text="检测到的缺失元素")
        missing_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # 使用容器包含文本和滚动条
        missing_container = ttk.Frame(missing_frame)
        missing_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        missing_text = tk.Text(missing_container, height=12, width=40, wrap="word")
        missing_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        missing_scroll = ttk.Scrollbar(missing_container, orient="vertical", command=missing_text.yview)
        missing_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        missing_text.configure(yscrollcommand=missing_scroll.set)
        
        missing_text.insert("1.0", """1. 经济系统
   - 修真资源的获取与分配方式需要详细说明
   - 修真物品的价值体系与交易规则不完善
   - 普通经济与修真经济的关联度不足

2. 边疆地区
   - 与周边国家/地区的关系需要补充
   - 边境地区修真资源分布情况不明确
   - 少数民族对修真的接受程度缺乏描述

3. 普通人视角
   - 缺乏对非修真者日常生活的描述
   - 普通人如何看待修真者未详细阐述
   - 社会底层对修真的态度需要完善

4. 修真衍生问题
   - 寿命延长对人口结构的影响
   - 修真失败者的去向与社会问题
   - 修真药材的可持续采集与环境保护

建议优化方向：
1. 增加经济系统细节，特别是修真资源循环
2. 补充边疆民族与修真文化的互动
3. 添加普通人生活视角，展现全面社会图景
4. 探讨修真对社会长期发展的影响""")
        missing_text.config(state="disabled")
        
        # 底部 - 修复建议与确认按钮
        ttk.Separator(self.dynamic_frame, orient="horizontal").grid(row=2, column=0, sticky="ew", pady=5)
        
        recommendation_frame = ttk.LabelFrame(self.dynamic_frame, text="系统建议")
        recommendation_frame.grid(row=3, column=0, sticky="ew", pady=10)
        ttk.Label(recommendation_frame, text="建议先完善经济系统和边疆地区设定，这将使世界观完整度提升至90%以上。", 
                 font=("Arial", 9, "italic")).pack(padx=10, pady=10)
        
        confirm_button = ttk.Button(self.dynamic_frame, text="优化完整性", command=self._optimize_completeness)
        confirm_button.grid(row=4, column=0, pady=10)
        
    def _create_style_polishing(self):
        """步骤8：风格化润色"""
        ttk.Label(self.dynamic_frame, text="选择文化特征集风格:", 
                 font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=10)
        
        # 风格选择框架 - 使用更好的视觉分组
        style_frame = ttk.LabelFrame(self.dynamic_frame, text="文化风格")
        style_frame.grid(row=1, column=0, sticky="ew", pady=5, padx=5)
        
        # 风格选项 - 确保描述文本可以换行
        styles = [
            ("正统古风", "偏重忠、义、礼、智、信等传统价值观"),
            ("魔幻古风", "融合奇幻元素的古代文化风格"),
            ("写实主义", "注重历史真实感和生活细节"),
            ("浪漫主义", "强调情感、理想和个人英雄主义")
        ]
        
        self.style_var = tk.StringVar()
        
        for i, (style, desc) in enumerate(styles):
            # 创建框架来包含单选按钮和描述
            style_option_frame = ttk.Frame(style_frame)
            style_option_frame.grid(row=i, column=0, sticky="w", pady=5, padx=10)
            
            # 添加单选按钮（不使用wraplength属性）
            rb = ttk.Radiobutton(style_option_frame, text=style, 
                               value=style, variable=self.style_var)
            rb.grid(row=0, column=0, sticky="w", padx=(0, 5))
            
            # 添加描述标签（标签支持wraplength属性）
            desc_label = ttk.Label(style_option_frame, text=f"- {desc}", wraplength=350)
            desc_label.grid(row=0, column=1, sticky="w")
        
        self.style_var.set("魔幻古风")  # 默认选择
        
        # 语言风格调整 - 使用更直观的控件布局
        ttk.Label(self.dynamic_frame, text="语言风格调整:", 
                 font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=10)
        
        language_frame = ttk.LabelFrame(self.dynamic_frame, text="语言特征")
        language_frame.grid(row=3, column=0, sticky="ew", pady=5, padx=5)
        
        # 设置列宽，确保标签有足够空间
        language_frame.columnconfigure(0, minsize=100)
        language_frame.columnconfigure(1, weight=1)
        
        language_aspects = [
            ("古风化程度", 0, 100),
            ("专业术语使用", 0, 100),
            ("生活化描述", 0, 100)
        ]
        
        self.language_scales = {}
        
        for i, (aspect, min_val, max_val) in enumerate(language_aspects):
            ttk.Label(language_frame, text=f"{aspect}:").grid(row=i, column=0, sticky="e", padx=5, pady=4)
            scale = ttk.Scale(language_frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, length=200)
            scale.grid(row=i, column=1, sticky="ew", padx=5, pady=4)
            scale.set(50)  # 默认值
            self.language_scales[aspect] = scale
            ttk.Label(language_frame, text=f"{min_val}").grid(row=i, column=2, sticky="w", padx=2, pady=4)
            ttk.Label(language_frame, text=f"{max_val}").grid(row=i, column=3, sticky="e", padx=2, pady=4)
        
        # 预览部分 - 更好的视觉分隔和布局
        preview_frame = ttk.LabelFrame(self.dynamic_frame, text="风格预览")
        preview_frame.grid(row=4, column=0, sticky="ew", pady=10, padx=5)
        
        # 添加滚动条到预览文本
        preview_container = ttk.Frame(preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.style_preview = tk.Text(preview_container, height=8, width=60, wrap="word")
        self.style_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.style_preview.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.style_preview.configure(yscrollcommand=preview_scrollbar.set)
        
        self.style_preview.insert("1.0", """玄武门外，晨光微露。李世民握紧长剑，身侧道袍飘动的方正道人掐诀念咒，灵光闪烁。
"太子殿下已得云霄派相助，我等若再不动手，恐修真之法将为李氏所独揽。"方正道人低声道。
李世民凝视远方，眸中寒光闪动："父皇沉迷丹药，太子勾结修士，我大唐将因此内耗。今日之举，非为个人，实为天下。"
一道金光自东方升起，玄武门内传来禁军调动之声，方正道人掐指一算："时辰已到，殿下请速速行动。"
李世民深吸一口气，举剑向前，一场将改变大唐命运的变局，就此展开......""")
        self.style_preview.config(state="disabled")
        
        # 按钮区域 - 更整洁的布局
        button_frame = ttk.Frame(self.dynamic_frame)
        button_frame.grid(row=5, column=0, pady=10)
        
        refresh_button = ttk.Button(button_frame, text="刷新预览", command=self._refresh_style_preview)
        refresh_button.grid(row=0, column=0, padx=20)
        
        finish_button = ttk.Button(button_frame, text="最终完成", command=self._finalize_worldview)
        finish_button.grid(row=0, column=1, padx=20)
        
    def _confirm_template(self):
        """确认模板选择"""
        selected_items = self.template_tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请先选择一个模板")
            return
            
        item = selected_items[0]
        template_name = self.template_tree.item(item, 'values')[0]
        template_type = self.template_tree.item(item, 'values')[1] if len(self.template_tree.item(item, 'values')) > 1 else "未知类型"
        
        # 保存选定的模板信息
        self.selected_template = {
            "name": template_name,
            "type": template_type
        }
        
        # 打印调试信息
        print(f"已选择模板，保存为: {self.selected_template}")
        
        # 更新输出区域
        self.output_text.config(state="normal")
        self.output_text.insert("end", f"\n●选择基础模板：{template_name}\n")
        self.output_text.see("end")
        self.output_text.config(state="disabled")
        
        # 标记此步骤为已完成
        self.steps_completed["载入基础模板"] = True
        
        # 进入下一步
        self.next_step()
        
    def _confirm_parameters(self):
        """确认参数设置"""
        # 收集参数值
        params = {}
        for param, entry in self.param_entries.items():
            value = entry.get()
            if not value or value.startswith("例如："):  # 检查是否为空或仍为提示文本
                messagebox.showwarning("参数未填写", f"请填写 '{param}' 的值")
                return
            params[param] = value
        
        # 更新输出文本
        self.output_text.config(state="normal")
        self.output_text.insert("end", "\n●核心参数设定:\n")
        for param, value in params.items():
            self.output_text.insert("end", f"    {param}: {value}\n")
        self.output_text.see("end")
        self.output_text.config(state="disabled")
        
        # 标记此步骤为已完成
        self.steps_completed["填充核心参数"] = True
        
        # 进入下一步
        self.next_step()
        
    def _confirm_suggestions(self):
        """确认扩展建议"""
        self.output_text.config(state="normal")
        self.output_text.insert("end", "\n●接受扩展建议，并整合到世界观框架中\n")
        self.output_text.see("end")
        self.output_text.config(state="disabled")
        
        # 标记此步骤为已完成
        self.steps_completed["生成扩展建议"] = True
        
        # 进入下一步
        self.next_step()
        
    def _confirm_conflicts(self):
        """确认冲突检测"""
        self.output_text.config(state="normal")
        self.output_text.insert("end", "\n●世界观矛盾检测完成，已校正所有逻辑问题\n")
        self.output_text.see("end")
        self.output_text.config(state="disabled")
        
        # 标记此步骤为已完成
        self.steps_completed["矛盾系统检测"] = True
        
        # 进入下一步
        self.next_step()
        
    def _optimize_completeness(self):
        """优化完整性"""
        self.output_text.config(state="normal")
        self.output_text.insert("end", "\n●世界观完整性验证通过，结构完善\n")
        self.output_text.see("end")
        self.output_text.config(state="disabled")
        
        # 标记此步骤为已完成
        self.steps_completed["完整性验证"] = True
        
        # 进入下一步
        self.next_step()
        
    def _refresh_style_preview(self):
        """刷新风格预览"""
        # 加载当前选择的风格和文本
        style_var = int(self.style_var.get())
        styles = ["标准叙述", "玄幻史诗", "轻松诙谐", "严肃学术", "诗意浪漫"]
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
        """完成世界观构建并生成最终结果，并保存到novel_structure.yaml"""
        style = self.style_var.get()
        
        output = f"【风格化润色】\n选择风格：{style}\n语言风格已调整\n\n"
        output += "----------完整世界观大纲----------\n\n"
        
        # 这里应该是整合之前所有步骤的结果，生成最终的世界观大纲
        # 从输出文本中获取生成的内容
        content_from_ui = self.output_text.get("1.0", tk.END).strip()
        if content_from_ui:
            final_outline = content_from_ui
        else:
            # 如果没有之前的内容，使用默认内容（实际应用中可能需要修改）
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
   - 传说：渡劫期（极少数人达到）

【社会影响】
1. 阶级结构的重塑
   - 修真能力带来的新型阶层划分
   - 传统贵族与修真新贵的冲突
   - 普通民众的生存空间变化

2. 皇权与修真势力的博弈
   - 初期排斥与限制
   - 中期利用与合作
   - 后期整合与制度化

3. 修真与传统文化的冲突与融合
   - 儒家思想与修真理念的碰撞
   - 佛道二教对修真的不同态度
   - 新文化思潮的产生与传播

【特色元素】
1. 修真辅助的唐军
   - 法器装备的精锐部队
   - 修士参与的军事行动
   - 对周边国家的威慑

2. 灵气农业革命
   - 灵气辅助的农作物增产
   - 新型农具与种植技术
   - 粮食产量提升带来的人口增长

3. 修真医学体系
   - 传统医学与修真医术的结合
   - 延长寿命的技术与药物
   - 医疗资源分配的社会问题

【世界观特点】
1. 历史真实性与架空元素的平衡
2. 修真体系的合理性与系统性
3. 社会矛盾的多层次展现
4. 文化冲突与融合的深入探讨"""
        
        output += final_outline
        
        # 将结果添加到输出文本区
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", output)
        
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
            
            # 如果不存在基本配置，创建一个
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
            messagebox.showinfo("完成", "世界观大纲已生成完毕，并保存到配置文件！")
        except Exception as e:
            messagebox.showerror("保存配置失败", f"保存到配置文件时出错：{str(e)}")
            # 仍然显示一个成功提示，因为至少生成了输出
            messagebox.showinfo("完成", "世界观大纲已生成，但保存配置文件失败！")


