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
import re

class WorldViewPanel:
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
        self.steps = ["构建基础模板", "模板参数调整", "生成扩展建议", "检测核心冲突", "完善世界完整度", "优化风格一致性", "世界观展示"]
        
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
        self.step_indicators_frame.pack(padx=10, pady=0)
        
        self.step_indicators = []
        
        # 将所有步骤显示在一行
        for i, step in enumerate(self.steps):
            col = i * 2  # 每个步骤占两列(步骤+箭头)
            
            # 步骤标签 - 移除数字前缀
            step_label = ttk.Label(self.step_indicators_frame, text=f"{step}", font=("Arial", 9))
            step_label.grid(row=0, column=col, padx=5, pady=1)
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
        min_height = 480  # 设置最小高度（可以根据实际需求调整）
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
        
        # 添加鼠标滚轮滚动支持
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
        self.content_frame = ttk.LabelFrame(content_container)
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
        
    def update_by_creation_type(self, creation_type):
        """根据创作类型更新界面,仅保存当前创作类型,不读取配置文件"""
        # 保存创作类型 - 可能是字符串或字典
        self.current_creation_type = creation_type
        
        # 如果是字符串,尝试从配置文件获取更详细的信息
        if isinstance(creation_type, str):
            print(f"更新当前创作类型为字符串: {creation_type}")
            try:
                with open(self.config_file, "r", encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    base_config = config_data.get('base_config', {})
                    main_type = base_config.get('main_type')
                    sub_type = base_config.get('sub_type')
                    
                    if main_type and sub_type:
                        # 也保存字典格式的创作类型,以备后用
                        self.current_creation_type_dict = {'主类型': main_type, '子类型': sub_type}
                        print(f"从配置文件获取到详细创作类型: {self.current_creation_type_dict}")
            except Exception as e:
                print(f"读取配置文件获取创作类型详情失败: {e}")
        else:
            print(f"更新当前创作类型为字典: {creation_type}")
            # 已经是字典格式
            self.current_creation_type_dict = creation_type
    
    def update_step_view(self):
        """更新步骤视图,根据当前步骤显示不同内容"""
        print(f"WorldView: 更新步骤视图，当前步骤索引: {self.current_step_index}")
        
        # 清空动态框架
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()
        
        # 保存固定容器的当前高度
        current_height = self.fixed_container.winfo_height()
        
        # 重置滚动位置
        self.content_canvas.yview_moveto(0)
        
        # 更新步骤指示器
        for i, step in enumerate(self.steps):
            if i < self.current_step_index:
                self.step_indicators[i].configure(
                    text=f"✓ {step}", 
                    foreground="#006600", 
                    font=self.completed_step_font
                )
            elif i == self.current_step_index:
                self.step_indicators[i].configure(
                    text=f"► {step}", 
                    foreground="#000066", 
                    font=self.current_step_font
                )
            else:
                self.step_indicators[i].configure(
                    text=f"{step}", 
                    foreground="black", 
                    font=self.step_font
                )
            
        # 根据当前步骤创建相应内容
        if self.current_step_index == 0:
            self._create_base_template()
        elif self.current_step_index == 1:
            self._create_parameter_input_view()
        elif self.current_step_index == 2:
            self._create_suggestion_generation()
        elif self.current_step_index == 3:
            self._create_conflict_detection()
        elif self.current_step_index == 4:
            self._create_completion_validation()
        elif self.current_step_index == 5:
            self._create_style_polishing()
        elif self.current_step_index == 6:
            self._create_world_view_display()
            
        # 更新按钮状态
        self.prev_button.configure(state=tk.NORMAL if self.current_step_index > 0 else tk.DISABLED)
        
        # 确保固定容器保持相同高度
        min_height = max(480, current_height)  # 使用保存的高度或最小高度
        self.fixed_container.configure(height=min_height)
        self.fixed_container.update()  # 强制更新容器大小
        
        # 更新滚动区域
        self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))
        
        self.next_button.configure(text="完成" if self.current_step_index == len(self.steps) - 1 else "下一步")
    
    def next_step(self):
        """进入下一步"""
        # 检查当前步骤是否已完成
        current_step_name = self.steps[self.current_step_index]
        if not self.steps_completed.get(current_step_name, False):
            messagebox.showwarning("提示", f"请先完成「{current_step_name}」步骤再继续")
            return
                
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            self.update_step_view()
        else:
            # 已经是最后一步,执行完成操作
            self.finalize_outline()
            
    def prev_step(self):
        """返回上一步"""
        # 取消任何进行中的进度条动画
        if hasattr(self, 'progress_timer_id'):
            self.master.after_cancel(self.progress_timer_id)
            
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.update_step_view()
            
    def finalize_outline(self):
        """完成大纲生成"""
        messagebox.showinfo("完成", "世界观构建完成！请在结果区查看完整世界观。")
    
    def _check_config_changes(self):
        """定期检查配置文件变化,更新界面"""
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
                    
                    # 如果当前正在模板载入步骤,需要刷新界面以显示最新的基础配置信息
                    if self.current_step_index == 0:
                        self.update_step_view()
                        
                    print(f"检测到配置文件变化,已更新基础配置信息: {self.base_config}")
        except Exception as e:
            # 静默处理异常,不打断用户体验
            print(f"配置文件检查错误: {str(e)}")
            
        # 继续下一轮检查
        self.after(2000, self._check_config_changes)
    
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
            
            # 标记步骤完成
            self.steps_completed["构建基础模板"] = True
            
            # 更新提示下一步
            messagebox.showinfo("提示", "模板已应用，请点击\"下一步\"继续模板参数调整")
        else:
            messagebox.showwarning("提示", "预览编辑器不存在，请重新加载界面")
            
    def _update_base_template_view(self):
        """更新基础模板视图，显示最新生成的模板"""
        # 检查是否在步骤1
        if self.current_step_index == 0:
            self._create_base_template()
    
    def _ai_generate_template(self):
        """调用AI生成世界观模板"""
        print("WorldView: AI生成模板按钮被点击")
        try:
            # 创建生成窗口
            gen_window = tk.Toplevel(self.master)
            gen_window.title("AI生成世界观模板")
            gen_window.geometry("900x800")
            gen_window.minsize(800, 700)
            
            # 设置窗口居中显示
            self._center_window(gen_window, 900, 800)
            
            # 创建一个Frame来放置所有控件
            main_frame = ttk.Frame(gen_window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # 创建一个可调节大小的框架，使用PanedWindow
            paned_window = ttk.PanedWindow(main_frame, orient="vertical")
            paned_window.pack(fill="both", expand=True)
            
            # ===== 顶部提示词区域 =====
            prompt_frame = ttk.Frame(paned_window)
            
            # 创建作品信息区域
            info_frame = ttk.Frame(prompt_frame)
            info_frame.pack(fill="x", pady=5)
            
            # 从基础配置中获取信息
            work_title = "未命名作品"
            work_type = "未指定类型"
            main_type = "通用"
            sub_type = "通用"
            
            if hasattr(self, 'base_config') and self.base_config:
                # 获取作品名称、作品类型、主类型和子类型
                work_title = self.base_config.get('title', work_title)
                work_type = self.base_config.get('creation_type', work_type)
                main_type = self.base_config.get('main_type', main_type)
                sub_type = self.base_config.get('sub_type', sub_type)
                
                # 创建作品信息标签
                work_info = f"作品名称: 《{work_title}》  作品类型: {work_type}  创作类型: {main_type}-{sub_type}"
                work_info_label = ttk.Label(info_frame, text=work_info, font=("Arial", 9))
                work_info_label.pack(anchor="w", padx=5)
            
            ttk.Label(prompt_frame, text="提示词(可编辑):", font=("Arial", 10, "bold")).pack(anchor="w")
            
            # 提示词编辑区
            prompt_editor = scrolledtext.ScrolledText(prompt_frame, height=6, wrap="word")
            prompt_editor.pack(fill="both", expand=True, pady=5)
            
            # 添加到PanedWindow
            paned_window.add(prompt_frame, weight=1)
            
            # 初始使用默认提示词
            initial_prompt = self._build_template_prompt()
            if initial_prompt:
                prompt_editor.insert("1.0", initial_prompt)
            
            # ===== 中间结果区域 =====
            result_frame = ttk.Frame(paned_window)
            
            ttk.Label(result_frame, text="生成结果:", font=("Arial", 10, "bold")).pack(anchor="w")
            
            # 结果编辑器
            editor = scrolledtext.ScrolledText(result_frame, wrap="word")
            editor.pack(fill="both", expand=True, pady=5)
            
            # 添加到PanedWindow
            paned_window.add(result_frame, weight=2)
            
            # ===== 底部思考过程区域 =====
            thinking_frame = ttk.Frame(paned_window)
            
            thinking_header = ttk.Frame(thinking_frame)
            thinking_header.pack(fill="x")
            
            ttk.Label(thinking_header, text="AI思考过程:", font=("Arial", 10, "bold")).pack(side="left")
            self.thinking_indicator = ttk.Label(thinking_header, text="●", foreground="green")
            self.thinking_indicator.pack(side="left", padx=5)
            
            # 思考过程区域（现在在可调整的pane中）
            self.thinking_text = scrolledtext.ScrolledText(thinking_frame, height=6, wrap="word")
            self.thinking_text.pack(fill="both", expand=True, pady=5)
            
            # 添加到PanedWindow
            paned_window.add(thinking_frame, weight=1)
            
            # 底部按钮区域
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill="x", pady=10)
            
            # 按钮区域布局
            left_btn_frame = ttk.Frame(btn_frame)
            left_btn_frame.pack(side="left", fill="x", expand=True)
            
            right_btn_frame = ttk.Frame(btn_frame)
            right_btn_frame.pack(side="right", fill="x")
            
            # 开始生成模板按钮
            self.gen_btn = ttk.Button(left_btn_frame, text="生成模板", 
                                command=lambda: self._start_template_generation(gen_window, prompt_editor.get("1.0", "end-1c"), editor))
            self.gen_btn.pack(side="left", padx=5)
            
            # 生成提示词按钮
            gen_prompt_btn = ttk.Button(left_btn_frame, text="生成提示词",
                                 command=lambda: self._generate_prompt_via_api(gen_window, prompt_editor))
            gen_prompt_btn.pack(side="left", padx=5)
            
            # 停止生成按钮
            self.stop_btn = ttk.Button(left_btn_frame, text="停止生成", 
                                command=self._stop_template_generation,
                                state="disabled")
            self.stop_btn.pack(side="left", padx=5)
            
            # 保存按钮
            self.save_btn = ttk.Button(right_btn_frame, text="应用模板", 
                                command=lambda: self._save_template(editor, gen_window),
                                state="disabled")
            self.save_btn.pack(side="right", padx=5)
            
            # 初始化生成状态标记
            self.generation_stopped = False
            self.prompt_generation_active = False
            
            # 显示窗口并置于前台
            gen_window.transient(self.master)
            gen_window.grab_set()
            gen_window.focus_set()
            
        except Exception as e:
            messagebox.showerror("错误", f"创建AI生成模板窗口时出错: {str(e)}")
            print(f"WorldView错误: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _generate_prompt_via_api(self, window, prompt_editor):
        """通过API生成提示词"""
        print("WorldView: 通过API生成提示词")
        try:
            # 获取基础信息
            main_type = "通用"
            sub_type = "通用"
            work_title = "未命名作品"
            work_type = "未指定类型"
            
            if hasattr(self, 'base_config') and self.base_config:
                main_type = self.base_config.get('main_type', main_type)
                sub_type = self.base_config.get('sub_type', sub_type)
                work_title = self.base_config.get('title', work_title)
                work_type = self.base_config.get('creation_type', work_type)
            
            # 清空编辑器
            prompt_editor.delete("1.0", "end")
            prompt_editor.insert("1.0", "正在生成提示词...")
            prompt_editor.config(state="disabled")
            
            # 更新思考区域
            self.thinking_text.delete("1.0", "end")
            self.thinking_text.insert("end", f"正在为《{work_title}》({work_type} | {main_type}-{sub_type})生成提示词...\n\n")
            self.thinking_indicator.config(foreground="red", text="●")
            
            # 设置生成状态和按钮
            self.generation_stopped = False
            self.prompt_generation_active = True
            self.gen_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            
            # 临时存储当前编辑器，用于后续更新
            self.prompt_editor = prompt_editor
            self.current_gen_window = window
            
            def safe_update_ui(func, *args):
                if window.winfo_exists():
                    window.after(0, func, *args)
            
            # 回调函数处理流式响应
            def prompt_callback(chunk):
                if not window.winfo_exists() or self.generation_stopped:
                    return
                
                if isinstance(chunk, dict):
                    # 思维链内容通过模板回调处理
                    safe_update_ui(lambda: self._template_stream_callback(chunk))
                else:
                    # 文本内容直接更新到编辑器
                    safe_update_ui(lambda: self._update_prompt_editor(prompt_editor, chunk))
            
            def generate_thread():
                try:
                    # 尝试导入API客户端并生成内容
                    try:
                        from core.api_client.deepseek import api_client
                        
                        # 准备消息
                        meta_prompt = f"""我需要你帮我创建一个提示词，这个提示词将用于生成《{work_title}》这部{work_type}类型的{main_type}-{sub_type}作品的世界观模板。

请根据作品特点，创建一个详细的提示词，包含：
1. {work_type}类型的{main_type}-{sub_type}作品的世界观应该包含哪些核心要素
2. 每个要素应该包含哪些具体细节
3. 需要考虑的特殊设定或限制条件
4. 与《{work_title}》作为{work_type}类型的{main_type}-{sub_type}作品相关的典型元素和特色

提示词应该结构清晰，层次分明，便于AI理解和生成。请直接给出提示词内容，无需额外解释。"""
                        
                        messages = [
                            {"role": "system", "content": "你是一个专业的提示词工程师，擅长创建用于生成世界观设定的高质量提示词。在生成提示词前，请思考并解释你的决策过程。"},
                            {"role": "user", "content": meta_prompt}
                        ]
                        
                        # 启用编辑器用于流式更新
                        safe_update_ui(lambda: prompt_editor.config(state="normal"))
                        safe_update_ui(lambda: prompt_editor.delete("1.0", "end"))
                        
                        # 使用API客户端的流式生成，使用相同的回调处理机制
                        for chunk in api_client.stream_generate(messages, callback=prompt_callback):
                            if self.generation_stopped or not window.winfo_exists():
                                print("提示词生成被停止")
                                break
                        
                        # 生成完成
                        if window.winfo_exists():
                            if not self.generation_stopped:
                                safe_update_ui(lambda: self.thinking_text.insert("end", "\n\n提示词生成完成！\n"))
                            safe_update_ui(lambda: self.thinking_indicator.config(foreground="green", text="●"))
                            safe_update_ui(lambda: self.gen_btn.config(state="normal"))
                            safe_update_ui(lambda: self.stop_btn.config(state="disabled"))
                            self.prompt_generation_active = False
                        
                    except Exception as e:
                        print(f"生成提示词API调用失败: {str(e)}")
                        if window.winfo_exists():
                            # 生成失败，回退到默认提示词
                            default_prompt = self._build_template_prompt()
                            safe_update_ui(lambda: self.thinking_text.insert("end", f"\nAPI调用失败: {str(e)}，使用默认提示词\n"))
                            safe_update_ui(lambda: prompt_editor.config(state="normal"))
                            safe_update_ui(lambda: prompt_editor.delete("1.0", "end"))
                            safe_update_ui(lambda: prompt_editor.insert("1.0", default_prompt))
                            safe_update_ui(lambda: self.thinking_indicator.config(foreground="green", text="●"))
                            safe_update_ui(lambda: self.gen_btn.config(state="normal"))
                            safe_update_ui(lambda: self.stop_btn.config(state="disabled"))
                            self.prompt_generation_active = False
                
                except Exception as e:
                    print(f"生成提示词线程异常: {str(e)}")
                    if window.winfo_exists():
                        safe_update_ui(lambda: messagebox.showerror("错误", f"生成提示词出错: {str(e)}", parent=window))
                        safe_update_ui(lambda: prompt_editor.config(state="normal"))
                        safe_update_ui(lambda: prompt_editor.delete("1.0", "end"))
                        safe_update_ui(lambda: prompt_editor.insert("1.0", self._build_template_prompt()))
                        safe_update_ui(lambda: self.gen_btn.config(state="normal"))
                        safe_update_ui(lambda: self.stop_btn.config(state="disabled"))
                        self.prompt_generation_active = False
            
            # 启动生成线程
            prompt_thread = threading.Thread(target=generate_thread)
            prompt_thread.daemon = True
            prompt_thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"生成提示词时出错: {str(e)}", parent=window)
            prompt_editor.config(state="normal")
            prompt_editor.delete("1.0", "end")
            prompt_editor.insert("1.0", self._build_template_prompt())
            self.gen_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.prompt_generation_active = False
    
    def _update_prompt_editor(self, editor, chunk):
        """更新提示词编辑器内容（流式更新）"""
        if not editor or not editor.winfo_exists():
            return
        
        try:
            # 过滤特殊符号
            filtered_chunk = self._filter_special_symbols(chunk)
            
            # 插入新内容到编辑器末尾
            editor.insert("end", filtered_chunk)
            # 滚动到最新内容
            editor.see("end")
        except tk.TclError:
            pass  # 忽略可能的窗口已关闭错误
    
    def _filter_special_symbols(self, text):
        """过滤文本中的特殊符号，保留有用内容"""
        if not text:
            return text
            
        # 如果文本中只包含特殊符号或非常短，直接返回
        if len(text.strip()) <= 2 or text.strip() in ['#', '*', '`', '-', '=', '_']:
            return text
            
        # 定义需要特殊处理的模式
        patterns_to_handle = [
            # 移除Markdown标题标记，但保留文字内容和数字编号
            (r'#+ +([\d\.]+\s*)?(.+)', r'\1\2'),  # 例如 "# 1. 标题" -> "1. 标题"
            
            # 移除Markdown列表标记，但保留文字内容和编号
            (r'^\* +([\d\.]+\s*)?(.+)', r'\1\2'),  # 例如 "* 1. 列表项" -> "1. 列表项"
            (r'^\- +([\d\.]+\s*)?(.+)', r'\1\2'),  # 例如 "- 1. 列表项" -> "1. 列表项"
            (r'^\+ +([\d\.]+\s*)?(.+)', r'\1\2'),  # 例如 "+ 1. 列表项" -> "1. 列表项"
            
            # 移除Markdown强调标记，但保留文字内容
            (r'\*\*(.+?)\*\*', r'\1'),  # 例如 "**加粗**" -> "加粗"
            (r'\*(.+?)\*', r'\1'),      # 例如 "*斜体*" -> "斜体"
            (r'__(.+?)__', r'\1'),      # 例如 "__加粗__" -> "加粗"
            (r'_(.+?)_', r'\1'),        # 例如 "_斜体_" -> "斜体"
            
            # 移除Markdown代码标记，但保留文字内容
            (r'`(.+?)`', r'\1'),        # 例如 "`代码`" -> "代码"
            
            # 移除Markdown分隔线
            (r'^-{3,}$', ''),           # 例如 "---" -> ""
            (r'^={3,}$', ''),           # 例如 "===" -> ""
            (r'^_{3,}$', ''),           # 例如 "___" -> ""
        ]
        
        # 分行处理，保持原有结构
        lines = text.split('\n')
        for i in range(len(lines)):
            line = lines[i]
            for pattern, replacement in patterns_to_handle:
                line = re.sub(pattern, replacement, line)
            lines[i] = line
        
        # 重新组合处理后的文本
        return '\n'.join(lines)
    
    def _build_template_prompt(self):
        """根据当前创作类型构建提示词"""
        # 设置默认值
        main_type = "通用"  # 默认主类型
        sub_type = "通用"   # 默认子类型
        work_title = "未命名作品"  # 默认作品名称
        work_type = "未指定类型"   # 默认作品类型
        
        # 使用内存中的base_config信息
        if hasattr(self, 'base_config') and self.base_config:
            # 获取作品名称、作品类型、主类型和子类型
            work_title = self.base_config.get('title', work_title)
            work_type = self.base_config.get('creation_type', work_type)
            main_type = self.base_config.get('main_type', main_type)
            sub_type = self.base_config.get('sub_type', sub_type)
            print(f"_build_template_prompt: 使用当前基础配置信息: 作品名称={work_title}, 作品类型={work_type}, 主类型={main_type}, 子类型={sub_type}")
        else:
            print("_build_template_prompt: 未找到当前基础配置信息，使用默认值")
        
        # 构建提示词
        prompt = f"""为《{work_title}》这部{work_type}类型的{main_type}-{sub_type}作品设计一个详细的世界观模板，请提供以下要素：

一、总览设定（50字内概括核心）
- 用一句话定义世界观的"独特性"

二、时空与物理法则
1. 时空背景
   - 时代：现代/古代/近未来/架空纪元
   - 地理范围：主要地图构成
   - 物理法则：常规物理是否与现实一致，超自然规则特点

2. 时间流动
   - 时间线类型：单线/循环/平行时空
   - 特殊时间现象

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

五、关键组织与势力
- 至少3个重要组织，包含名称、性质、核心目标、与主角关系

六、生态与生物
- 特殊生物设计
- 自然环境威胁

七、历史大事件
- 按时间轴列出影响世界观的关键事件

要求：
- 契合《{work_title}》这部{work_type}作品的核心主题
- 符合{main_type}的一般特征
- 融入{sub_type}的典型元素和特色
- 提供具体细节而非泛泛而谈
- 构建富有创意且内部逻辑自洽的世界体系"""
        
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
            self.generation_stopped = False
            
            # 创建用于在线程间安全更新UI的函数
            def safe_update_ui(func, *args):
                if window.winfo_exists():
                    window.after(0, func, *args)
            
            # 回调函数用于处理流式响应
            def safe_callback(chunk):
                safe_update_ui(self._template_stream_callback, chunk)
            
            # 备用内容，当API调用失败时使用
            fallback_content = """# 世界观模板（备用内容）

一、总览设定
   这是一个表面平静但暗流涌动的现代都市，城市表象下隐藏着错综复杂的秘密网络。每个线索都是解开真相的关键，没有超自然力量，只有人性的复杂与理性的较量。

二、时空与物理法则
   - 时代：现代社会
   - 地理范围：虚构都市"映月市"
   - 物理法则：与现实世界一致

三、社会结构
   - 权力阶级：市政府、警方与商业巨头
   - 经济资源：房地产、信息与古董收藏品
   - 文化习俗：老城区保守传统，新城区现代开放

四、超自然/科技体系
   - 无超自然能力，但有高科技监控与分析系统

五、关键组织
   1. 映月警局：官方执法机构，内部派系林立
   2. 蓝天集团：城市最大地产开发商
   3. 古董收藏协会：表面合法，暗中交易非法文物

六、生态与生物
   - 城市生态系统，无特殊生物

七、历史大事件
   - 映月市重建计划（5年前）
   - 市长选举舞弊案（2年前）
   - 博物馆失窃案（3个月前）"""
            
            # 在新线程中运行生成过程
            def generate_thread():
                try:
                    # 尝试导入API客户端并生成内容
                    try:
                        from core.api_client.deepseek import api_client
                        
                        # 准备消息
                        messages = [
                            {"role": "system", "content": "你是一个专业的世界观设计助手，擅长为各类作品创建详细的世界观模板和设定。在创建世界观模板前，请思考并解释你的设计理念和构思过程。"},
                            {"role": "user", "content": prompt}
                        ]
                        
                        # 使用API客户端的流式生成
                        for chunk in api_client.stream_generate(messages, callback=safe_callback):
                            if self.generation_stopped or not window.winfo_exists():
                                print("生成被停止")
                                break
                        
                        # 生成完成
                        if not self.generation_stopped and window.winfo_exists():
                            safe_update_ui(self._mark_template_thinking_finished)
                            
                    except Exception as e:
                        print(f"API调用失败: {str(e)}，使用备用内容")
                        
                        # 使用备用内容
                        if window.winfo_exists():
                            safe_update_ui(lambda: self.thinking_text.insert("end", "API调用失败，使用备用内容...\n"))
                            
                            # 分段显示备用内容以模拟生成效果
                            chunks = fallback_content.split('\n\n')
                            for chunk in chunks:
                                if self.generation_stopped:
                                    break
                                safe_callback(chunk + '\n\n')
                                time.sleep(0.3)
                            
                            safe_update_ui(self._mark_template_thinking_finished)
                        
                except Exception as e:
                    print(f"生成线程发生异常: {str(e)}")
                    if window.winfo_exists():
                        safe_update_ui(lambda: messagebox.showerror("错误", f"生成过程发生错误: {str(e)}", parent=window))
                        safe_update_ui(lambda: self.gen_btn.config(state="normal"))
                        safe_update_ui(lambda: self.stop_btn.config(state="disabled"))
            
            # 启动生成线程
            self.gen_thread = threading.Thread(target=generate_thread)
            self.gen_thread.daemon = True
            self.gen_thread.start()
        
        except Exception as e:
            messagebox.showerror("错误", f"启动生成过程时出错: {str(e)}", parent=window)
            print(f"启动生成错误: {str(e)}")
            
            # 恢复UI状态
            self.gen_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
    
    def _stop_template_generation(self):
        """停止模板或提示词生成"""
        print("WorldView: 停止生成被触发")
        
        # 设置停止标记
        self.generation_stopped = True
        
        # 调用API客户端的停止方法
        try:
            from core.api_client.deepseek import api_client
            setattr(api_client, '_generation_stopped', True)
        except Exception as e:
            print(f"设置API客户端停止标志失败: {str(e)}")
        
        # 更新UI状态
        self.thinking_indicator.config(foreground="orange", text="⏹")
        self.gen_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        # 根据当前生成类型更新UI
        if hasattr(self, 'prompt_generation_active') and self.prompt_generation_active:
            # 提示词生成停止
            print("WorldView: 提示词生成被停止")
            if hasattr(self, 'prompt_editor') and self.prompt_editor and self.prompt_editor.winfo_exists():
                self.prompt_editor.config(state="normal")
            self.prompt_generation_active = False
            
            # 在思考区域添加停止信息
            if hasattr(self, 'thinking_text') and self.thinking_text.winfo_exists():
                self.thinking_text.insert("end", "\n\n提示词生成已停止。\n")
        else:
            # 模板生成停止
            print("WorldView: 模板生成被停止")
            self.save_btn.config(state="normal")
            
            # 在思考区域添加停止信息
            if hasattr(self, 'thinking_text') and self.thinking_text.winfo_exists():
                self.thinking_text.insert("end", "\n\n模板生成已停止。\n")
    
    def _template_stream_callback(self, chunk):
        """处理流式响应的回调函数"""
        try:
            # 处理不同类型的响应
            if isinstance(chunk, dict):
                # 处理思维过程内容
                if "reasoning_content" in chunk:
                    content = chunk["reasoning_content"]
                    # 直接传递给处理函数，无需额外处理
                    self._display_template_reasoning(content)
                    return
                # 处理思维结束标志
                elif "thinking_finished" in chunk:
                    if hasattr(self, 'thinking_text') and self.thinking_text.winfo_exists():
                        self.thinking_text.insert("end", "\n\n思考完成，开始生成...\n\n")
                    self._mark_template_thinking_finished()
                    return
            
            # 文本内容更新到编辑器，仅当有编辑器引用时
            if hasattr(self, 'current_editor') and self.current_editor and self.current_editor.winfo_exists():
                self._update_template_editor(self.current_editor, chunk)
        except Exception as e:
            print(f"处理流回调时发生异常: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _update_template_editor(self, editor, chunk):
        """更新模板编辑器内容"""
        if not editor or not editor.winfo_exists():
            return
        
        try:
            # 过滤特殊符号
            filtered_chunk = self._filter_special_symbols(chunk)
            
            # 插入新内容到编辑器末尾
            editor.insert("end", filtered_chunk)
            # 滚动到最新内容
            editor.see("end")
        except tk.TclError:
            pass  # 忽略可能的窗口已关闭错误
    
    def _display_template_reasoning(self, content):
        """显示AI思考过程"""
        if not hasattr(self, 'thinking_text') or not self.thinking_text.winfo_exists():
            return
        
        try:
            # 检查内容类型
            if not content or content.isspace():
                return  # 忽略空内容
                
            # 获取当前内容结尾字符，用于判断是否需要添加空格或换行
            is_beginning = self.thinking_text.index("end-1c") == "1.0"
            last_char = "" if is_beginning else self.thinking_text.get("end-2c", "end-1c")
            
            # 处理不同类型的内容
            if len(content) < 5 and content.strip() in [".", ",", "!", "?", "...", "。", "，", "！", "？"]:
                # 对于单个标点符号，直接添加无需额外处理
                self.thinking_text.insert("end", content)
            elif "\n" in content:
                # 如果内容本身包含换行，保持原始格式
                # 确保段落前后有适当的换行
                if not content.endswith("\n"):
                    content += "\n"
                # 如果前面没有换行且不是开始位置，添加换行
                if not is_beginning and not last_char.endswith("\n") and not content.startswith("\n"):
                    content = "\n" + content
                self.thinking_text.insert("end", content)
            else:
                # 普通文本内容
                # 判断是否需要在前面添加空格（避免多余空格）
                needs_space = False
                
                if not is_beginning and last_char and last_char not in ["\n", " ", ""]:
                    # 检查当前内容和上一个字符的组合是否需要空格
                    # 中文与中文之间、中文与英文之间、英文单词内部不需要空格
                    last_is_chinese = '\u4e00' <= last_char <= '\u9fff'
                    first_is_chinese = content and '\u4e00' <= content[0] <= '\u9fff'
                    last_is_letter = 'a' <= last_char.lower() <= 'z'
                    first_is_letter = content and 'a' <= content[0].lower() <= 'z'
                    
                    # 当两个英文字母相邻，且不是标点符号时，需要添加空格
                    if (last_is_letter and first_is_letter) and not content.startswith((",", ".", "!", "?", ":", ";", "-", "_")):
                        needs_space = True
                    # 中英文之间一般不需要空格，除非特殊情况
                    elif (last_is_chinese and first_is_letter) or (last_is_letter and first_is_chinese):
                        needs_space = False
                
                # 根据判断结果插入内容
                if needs_space and not content.startswith(" "):
                    self.thinking_text.insert("end", " " + content)
                else:
                    self.thinking_text.insert("end", content)
            
            # 滚动到最新内容
            self.thinking_text.see("end")
        except tk.TclError:
            pass  # 忽略可能的窗口已关闭错误
        except Exception as e:
            print(f"显示思考过程时出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _mark_template_thinking_finished(self):
        """标记思考过程已完成"""
        try:
            if hasattr(self, 'thinking_indicator') and self.thinking_indicator.winfo_exists():
                self.thinking_indicator.config(foreground="green", text="●")
                
            # 不再添加文本提示，因为在回调中已经添加了
            if hasattr(self, 'save_btn') and self.save_btn.winfo_exists():
                self.save_btn.config(state="normal")
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

    def _parse_template_content(self, content):
        """解析模板内容到数据结构中"""
        # 简化的解析逻辑，只提取大标题及其内容
        template_data = {
            "full_content": content,
            "sections": {}
        }
        
        try:
            lines = content.split('\n')
            current_section = None
            current_text = []
            
            # 识别主要标题和内容
            for line in lines:
                line_lower = line.lower()
                
                # 检查是否为新章节标题
                if (line.startswith('#') or 
                    any(line.startswith(prefix) for prefix in ['一、', '二、', '三、', '四、', '五、', '六、', '七、', '八、']) or
                    any(keyword in line_lower for keyword in ['总览', '时空', '社会', '力量', '组织', '生态', '历史'])):
                    
                    # 保存之前的章节内容
                    if current_section and current_text:
                        template_data["sections"][current_section] = '\n'.join(current_text)
                    
                    # 确定新章节名称
                    if '总览' in line_lower or '概述' in line_lower:
                        current_section = "overview"
                    elif '时空' in line_lower or '背景' in line_lower:
                        current_section = "time_space"
                    elif '社会' in line_lower or '文化' in line_lower:
                        current_section = "society"
                    elif '力量' in line_lower or '体系' in line_lower or '科技' in line_lower:
                        current_section = "power_system"
                    elif '组织' in line_lower or '势力' in line_lower:
                        current_section = "organizations"
                    elif '生态' in line_lower or '生物' in line_lower or '环境' in line_lower:
                        current_section = "ecology"
                    elif '历史' in line_lower or '事件' in line_lower:
                        current_section = "history"
                    else:
                        current_section = "other"
                    
                    # 重置当前文本收集
                    current_text = [line]
                else:
                    # 继续收集当前章节文本
                    if current_section:
                        current_text.append(line)
            
            # 保存最后一个章节
            if current_section and current_text:
                template_data["sections"][current_section] = '\n'.join(current_text)
                
        except Exception as e:
            print(f"解析模板内容时出错: {str(e)}")
        
        return template_data
    
    def _apply_template_data(self, template_data):
        """应用解析后的模板数据"""
        # 简化版本，只保存数据以供后续使用
        self.worldview_data = template_data
    
    
    def _create_parameter_input_view(self):
        """步骤2：模板参数调整"""
        # 此处实现参数调整的界面
        pass
    
    def _create_suggestion_generation(self):
        """步骤3：生成扩展建议"""
        # 此处实现扩展建议生成的逻辑
        pass
    
    def _create_conflict_detection(self):
        """步骤4：检测核心冲突"""
        # 此处实现冲突检测的逻辑
        pass
    
    def _create_completion_validation(self):
        """步骤5：完善世界完整度"""
        # 此处实现完整度验证的逻辑
        pass
    
    def _create_style_polishing(self):
        """步骤6：优化风格一致性"""
        # 此处实现风格优化的逻辑
        pass
        
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
            "生态环境": self._create_ecology_tab
        }
        
        # 创建各个选项卡
        for tab_name, create_func in tabs.items():
            tab = ttk.Frame(self.tab_control)
            self.tab_control.add(tab, text=tab_name)
            create_func(tab)
        
        # 底部按钮区域
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill="x", pady=5)
        
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
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        
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
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        
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
        
        # 生物表格
        columns = ("生物名称", "类型", "特殊能力", "生态位置")
        creatures_tree = ttk.Treeview(creatures_frame, columns=columns, show="headings", height=6)
        
        # 设置列标题
        for col in columns:
            creatures_tree.heading(col, text=col)
            creatures_tree.column(col, width=100)
        
        # 添加示例数据
        sample_data = [
            ("示例生物1", "智慧种族", "元素控制", "森林"),
            ("示例生物2", "魔法生物", "隐形", "山脉"),
            ("示例生物3", "机械生命", "数据分析", "城市")
        ]
        
        for item in sample_data:
            creatures_tree.insert("", "end", values=item)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(creatures_frame, orient="vertical", command=creatures_tree.yview)
        creatures_tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置表格和滚动条
        creatures_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 环境特性
        env_frame = ttk.LabelFrame(frame, text="环境特性")
        env_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        env_text = scrolledtext.ScrolledText(env_frame, wrap="word", height=5)
        env_text.pack(fill="both", expand=True, padx=5, pady=5)
        env_text.insert("1.0", "这里显示世界的环境特性与自然规律...")
        env_text.config(state="disabled")
    
    def _save_to_file(self):
        """保存世界观到文件"""
        try:
            # 创建保存目录
            save_dir = Path("data/worldviews")
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # 默认文件名
            default_filename = f"世界观_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # 打开文件对话框
            file_path = filedialog.asksaveasfilename(
                initialdir=save_dir,
                initialfile=default_filename,
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            
            if not file_path:
                return
                
            # 收集世界观数据
            worldview_content = "==== 世界观总览 ====\n\n"
            
            # TODO: 收集实际的世界观数据
            
            # 写入文件
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(worldview_content)
                
            messagebox.showinfo("成功", f"世界观已保存到: {file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存文件时出错: {str(e)}")
    
    def _export_world_view_document(self):
        """导出世界观文档"""
        self._save_to_file()
    
    def _preview_world_view(self):
        """预览世界观"""
        # 创建预览窗口
        preview_window = tk.Toplevel(self.master)
        preview_window.title("世界观预览")
        preview_window.geometry("800x600")
        
        # 设置窗口居中显示
        self._center_window(preview_window, 800, 600)
        
        # 创建文本区域
        preview_text = scrolledtext.ScrolledText(preview_window, wrap="word")
        preview_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 插入世界观内容
        preview_text.insert("1.0", "==== 世界观总览 ====\n\n")
        # TODO: 插入实际的世界观内容
        
        preview_text.config(state="disabled")

    def _center_window(self, window, width, height):
        """设置窗口居中显示"""
        # 获取屏幕尺寸
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # 计算居中位置的坐标
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 设置窗口位置
        window.geometry(f"{width}x{height}+{x}+{y}")

