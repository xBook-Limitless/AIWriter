import tkinter as tk
from tkinter import ttk
import yaml
from pathlib import Path
from tkinter import messagebox
import time
import os
import traceback
import json
import threading
import logging
import random  # 新增随机模块

class RoleConfiguration(ttk.Frame):
    """角色配置面板"""
    
    ROLE_TYPES = {
        "严肃小说": ["主角", "对抗者", "叙事推动者", "情感联结体", 
                  "集体象征体", "超现实存在", "角色发展轨迹"],
        "网络小说": ["主角", "反派", "导师", "盟友", "恋人", 
                  "喜剧角色", "成长型角色"],
        "剧本": ["主角", "对手", "帮手", "催化剂角色", 
               "象征性角色", "功能性角色"],
        "剧本杀": ["侦探", "凶手", "帮凶", "目击者", 
                "关联人物", "背景人物"],
        "游戏剧情": ["可操作角色", "NPC", "Boss", "商人", 
                 "任务发布者", "阵营领袖"]
    }

    def __init__(self, master):
        super().__init__(master)
        self.role_map = {}  # 新增初始化
        self.config_file = Path("data/configs/novel_structure.yaml")
        self.entries = {}
        self.current_role_id = None
        self.roles = {}
        self.operation_history = []  # 统一操作历史记录
        self.reasoning_window = None
        self.reasoning_text = None
        self._create_widgets()  # 确保先创建组件
        self._load_config()     # 后加载配置
        self._update_preview()  # 最后初始化预览

    def _create_widgets(self):
        """创建角色配置界面"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左侧输入区域 (40%宽度)
        input_frame = ttk.Frame(main_frame, width=200)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 右侧预览区域 (60%宽度)
        preview_frame = ttk.Frame(main_frame, width=300)
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # --- 左侧输入组件 ---
        # 核心信息行
        top_frame = ttk.Frame(input_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        # 角色定位
        ttk.Label(top_frame, text="角色定位：").pack(side=tk.LEFT)
        self.role_type = ttk.Combobox(top_frame, state="readonly", width=10)
        self.role_type.pack(side=tk.LEFT, padx=5)
        
        # 姓名
        ttk.Label(top_frame, text="姓名：").pack(side=tk.LEFT, padx=3)
        self.entries['name'] = ttk.Entry(top_frame, width=10)
        self.entries['name'].pack(side=tk.LEFT, padx=0)
        
        # 性别
        ttk.Label(top_frame, text="性别：").pack(side=tk.LEFT, padx=2)
        self.entries['gender'] = ttk.Combobox(top_frame, values=["男", "女", "其他"], 
                                           state="readonly", width=4)
        self.entries['gender'].pack(side=tk.LEFT, padx=2)
        
        # 年龄
        ttk.Label(top_frame, text="年龄：").pack(side=tk.LEFT, padx=2)
        self.entries['age'] = ttk.Entry(top_frame, width=7)
        self.entries['age'].pack(side=tk.LEFT, padx=2)

        # 其他字段调整
        fields = [
            ("身份地位：", "identity", None),
            ("外貌特征：", "appearance", None),
            ("随身物品：", "belongings", None),
            ("显性目标：", "goal", None),
            ("隐性动机：", "motive", None),
            ("人设金句：", "tagline", None)
        ]

        for i, (label, key, options) in enumerate(fields, start=1):
            row_frame = ttk.Frame(input_frame)
            row_frame.pack(fill=tk.X, pady=3)
            
            ttk.Label(row_frame, text=label).pack(side=tk.LEFT, padx=3)
            if options:
                entry = ttk.Combobox(row_frame, values=options, state="readonly", width=45)
            else:
                entry = ttk.Entry(row_frame, width=48)
            entry.pack(side=tk.LEFT, padx=0, fill=tk.X, expand=True)
            self.entries[key] = entry

        # 替换角色列表为下拉框
        self.role_selector_frame = ttk.Frame(input_frame)
        self.role_selector_frame.pack(fill=tk.X, pady=5)

        # 角色选择器
        ttk.Label(self.role_selector_frame, text="当前角色：").pack(side=tk.LEFT)
        self.role_selector = ttk.Combobox(
            self.role_selector_frame, 
            state="readonly",
            width=10  # 宽度调整为10字符
        )
        self.role_selector.pack(side=tk.LEFT, padx=5)
        self.role_selector.bind("<<ComboboxSelected>>", self._select_role)

        # 操作按钮容器
        btn_frame = ttk.Frame(self.role_selector_frame)
        btn_frame.pack(side=tk.LEFT, padx=5)
        
        # 调整按钮宽度和间距
        ttk.Button(btn_frame, text="新建", width=5, command=self._add_role).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_frame, text="删除", width=5, command=self._delete_role).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_frame, text="撤销", width=5, command=self._undo_last).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_frame, text="保存", width=5, command=self._save_config).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_frame, text="AI生成", width=5, command=self._ai_generate_role).pack(side=tk.LEFT, padx=1)  # 新增AI生成按钮

        # 初始化角色类型
        self._update_role_types()

        # --- 右侧预览与编辑 ---
        # 预览标题
        ttk.Label(preview_frame, text="角色档案预览", font=('微软雅黑', 10, 'bold')).pack(pady=3)
        
        # 预览框容器设置
        scroll_container = ttk.Frame(preview_frame)  # 固定容器高度
        scroll_container.pack(fill=tk.X)  # 仅水平填充

        # 预览文本框
        self.preview_text = tk.Text(
            scroll_container,
            width=30,
            height=11,  # 固定显示12行
            wrap=tk.WORD,
            font=('Consolas', 10),
            padx=5,
            pady=5,
            bg='#F8F8F8'
        )
        self.preview_text.pack(side=tk.LEFT)  # 仅水平填充
        
        # 编辑按钮
        ttk.Button(
            preview_frame, 
            text="编辑完整档案", 
            command=self._open_full_edit
        ).pack(pady=5)

        # 最后绑定事件
        self._setup_preview_bindings()

    def _update_role_types(self, creation_type=None):
        """根据创作类型更新角色定位选项"""
        try:
            # 如果未传入类型，从配置文件获取
            if not creation_type:
                with open(self.config_file, "r", encoding='utf-8') as f:
                    config = yaml.safe_load(f).get("base_config", {})
                creation_type = config.get("creation_type", "严肃小说")
            
            types = self.ROLE_TYPES.get(creation_type, [])
            current_value = self.role_type.get()
            
            self.role_type["values"] = types
            # 保持当前选择（如果新类型中包含原值）
            if current_value in types:
                self.role_type.set(current_value)
            elif types:
                self.role_type.set(types[0])
            else:
                self.role_type.set('')
            # 新增：更新后立即刷新预览
            self._update_preview()
        except Exception as e:
            messagebox.showerror("错误", f"更新角色类型失败：{str(e)}")

    def _add_role(self, silent=False):
        """生成唯一连续ID（新增静默模式参数）"""
        new_index = len(self.roles) + 1
        while f"role_{new_index}" in self.roles:
            new_index += 1
        new_id = f"role_{new_index}"
        
        # 创建新角色数据
        new_role = {
            "role_type": "",
            "name": "新角色" if silent else "",  # 静默模式自动命名
            "gender": "",
            "age": "",
            "identity": "",
            "appearance": "",
            "belongings": "",
            "goal": "",
            "motive": "",
            "tagline": ""
        }
        self.roles[new_id] = new_role
        
        # 非静默模式立即更新界面
        if not silent:
            self.current_role_id = new_id
            self._update_role_list()
            self._show_role_data(new_role)
            self._record_operation('create', new_id, None)
        
        return new_id  # 始终返回新角色ID

    def _load_config(self):
        """修复旧版配置兼容性问题"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding='utf-8') as f:
                    all_config = yaml.safe_load(f) or {}

                # 兼容旧版本列表格式
                role_config = all_config.get("role_config", {})
                raw_roles = role_config.get("roles", [])
                
                # 转换旧数据格式
                if isinstance(raw_roles, list):
                    # 旧版列表格式转换
                    self.roles = {
                        item.get("id", f"role_{idx+1}"): {
                            k: v for k, v in item.items() if k != "id"
                        }
                        for idx, item in enumerate(raw_roles)
                    }
                else:
                    # 新版字典格式
                    self.roles = raw_roles.copy()

                # 设置当前角色
                self.current_role_id = role_config.get("current_role")
                if self.roles and not self.current_role_id:
                    self.current_role_id = next(iter(self.roles))

                if self.current_role_id:
                    self._show_role_data(self.roles[self.current_role_id])
                else:
                    self._clear_form()

                self._update_role_list()

        except Exception as e:
            messagebox.showerror("配置错误", f"加载角色配置失败：{str(e)}")
            self.roles = {}

    def _save_config(self):
        """保存时自动记录修改"""
        if self.current_role_id and self.current_role_id in self.roles:
            # 记录修改前的状态
            prev_data = self.roles[self.current_role_id].copy()
            # 获取当前表单数据
            current_data = {
                "role_type": self.role_type.get(),
                **{k: v.get() for k, v in self.entries.items()}
            }
            # 如果数据有变化才记录
            if prev_data != current_data:
                self._record_operation('update', self.current_role_id, prev_data)
            
            # 更新到角色字典
            self.roles[self.current_role_id] = current_data
        
        # 读取现有配置
        all_config = {}
        if self.config_file.exists():
            with open(self.config_file, "r", encoding='utf-8') as f:
                all_config = yaml.safe_load(f) or {}

        # 更新角色配置部分
        all_config["role_config"] = {
            "current_role": self.current_role_id,
            "roles": self.roles
        }

        # 确保配置目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # 写入完整配置
        with open(self.config_file, "w", encoding='utf-8') as f:
            yaml.dump(all_config, f, allow_unicode=True, sort_keys=False)

    def _update_role_list(self, select_id=None):
        """支持指定选中角色"""
        self.role_map = {}  # 每次更新前重置
        display_names = []
        
        for role_id, data in self.roles.items():
            name = data.get('name', '新角色')
            # 处理重名情况：自动添加序号
            base_name = name
            counter = 1
            while name in self.role_map:
                name = f"{base_name}({counter})"
                counter += 1
            
            display_names.append(name)
            self.role_map[name] = role_id
        
        self.role_selector['values'] = display_names
        
        # 自动选择有效角色
        if self.roles:
            target_id = select_id if select_id else self.current_role_id
            if target_id not in self.roles:
                target_id = next(iter(self.roles))
            
            self.current_role_id = target_id  # 确保当前角色ID有效
            current_name = self._get_display_name(target_id)
            self.role_selector.set(current_name)
        else:
            self.role_selector.set('')

    def _get_display_name(self, role_id):
        """根据ID获取显示名称"""
        data = self.roles.get(role_id, {})
        base_name = data.get('name', '新角色')
        
        # 检查是否有重名
        same_names = [k for k, v in self.role_map.items() if v == role_id]
        return same_names[0] if same_names else base_name

    def _select_role(self, event):
        """安全选择角色"""
        selected_name = self.role_selector.get()
        if selected_name in self.role_map:
            target_id = self.role_map[selected_name]
            if target_id in self.roles:  # 添加存在性检查
                self.current_role_id = target_id
                self._show_role_data(self.roles[target_id])
            else:
                messagebox.showwarning("警告", "该角色已不存在")
                self._update_role_list()

    def _show_role_data(self, data, keep_position=False):
        """显示角色数据时保持滚动位置"""
        if keep_position:
            # 记录当前滚动位置
            scroll_position = self.preview_text.yview()
        
        if self.current_role_id and self.current_role_id in self.roles:
            current_name = self._get_display_name(self.current_role_id)
            self.role_selector.set(current_name)
            self.role_type.set(data.get("role_type", ""))
            for key, entry in self.entries.items():
                value = data.get(key, "")
                if isinstance(entry, ttk.Combobox):
                    entry.set(value)
                else:
                    entry.delete(0, tk.END)
                    entry.insert(0, value)
            self._update_preview(force=True)
        else:
            self._clear_form()

        if keep_position:
            # 恢复滚动位置
            self.preview_text.yview_moveto(scroll_position[0])
            self.update_idletasks()

    def _delete_role(self):
        """删除角色后强制更新界面"""
        if self.current_role_id and self.current_role_id in self.roles:
            # 记录删除前的状态
            original_roles = self.roles.copy()
            original_current = self.current_role_id
            
            # 执行删除
            del self.roles[self.current_role_id]
            
            # 重新生成连续ID
            new_roles = {}
            for idx, (_, data) in enumerate(self.roles.items(), 1):
                new_id = f"role_{idx}"
                new_roles[new_id] = data
            self.roles = new_roles
            
            # 自动选择新角色
            self.current_role_id = next(iter(self.roles)) if self.roles else None
            if self.current_role_id:
                self._show_role_data(self.roles[self.current_role_id])
            else:
                self._clear_form()
            
            # 记录操作历史
            self._record_operation('delete', original_current, {
                'original_roles': original_roles,
                'original_current': original_current
            })
            self._save_config()
            
            # 强制更新下拉框
            self._update_role_list()
            
            # 确保当前选中项有效
            if self.roles:
                self.role_selector.set(self._get_display_name(self.current_role_id))
            else:
                self.role_selector.set('')
            
            # 立即刷新界面
            self.update_idletasks()

    # 新增公共方法供外部调用
    def update_by_creation_type(self, creation_type):
        """根据外部传入的创作类型更新"""
        self._update_role_types(creation_type)

    def _setup_preview_bindings(self):
        """为预览框添加事件绑定"""
        # 双击预览框打开完整编辑
        self.preview_text.bind("<Double-Button-1>", self._open_full_edit)
        
        # 新增：为所有输入框添加撤销支持
        for entry in self.entries.values():
            entry.bind("<Control-z>", self._undo_last_entry)
            entry.bind("<Control-Z>", self._undo_last_entry)  # 处理大写锁定情况

    def _track_entry_changes(self, var, entry):
        """增强历史记录跟踪"""
        entry.edit_history = [entry.get()]  # 初始化时包含当前值
        entry.edit_pointer = 0
        
        def on_change(*args):
            current = entry.get()
            last = entry.edit_history[entry.edit_pointer]
            
            # 忽略重复值
            if current == last:
                return
                
            # 添加新记录前截断指针后的历史
            entry.edit_history = entry.edit_history[:entry.edit_pointer+1]
            entry.edit_history.append(current)
            entry.edit_pointer += 1
            
            # 保持最多20步历史
            if len(entry.edit_history) > 20:
                # 移除最旧记录时调整指针
                removed_count = len(entry.edit_history) - 20
                entry.edit_history = entry.edit_history[removed_count:]
                entry.edit_pointer -= removed_count
                
            # 延迟自动保存
            self.after(2000, self._save_config)
        
        var.trace_add("write", on_change)

    def _undo_last_entry(self, event):
        """支持多步撤销"""
        widget = event.widget
        if not widget:
            return
        
        try:
            if not hasattr(widget, 'edit_history') or len(widget.edit_history) < 2:
                return
                
            # 允许逐步回退直到历史记录开头
            if widget.edit_pointer > 0:
                widget.edit_pointer -= 1
                prev_text = widget.edit_history[widget.edit_pointer]
                
                # 静默更新
                widget.config(state=tk.NORMAL)
                widget.delete(0, tk.END)
                widget.insert(0, prev_text)
                widget.config(state=tk.NORMAL)
                
                # 触发预览更新
                self._update_preview()
                
        except Exception as e:
            logging.error(f"撤销失败：{str(e)}")
        return "break"

    def _update_preview(self, event=None, force=False):
        """添加强制刷新逻辑"""
        if force or self.current_role_id:
            data = {
                'role_type': self.role_type.get(),
                **{k: v.get() for k, v in self.entries.items()}
            }
            
            # 严格保持原始字段名称和顺序
            preview_template = (
                "▬ 核心定位 ▬\n"
                "●角色定位：{role_type}\n\n"
                "▬ 基础信息 ▬\n"
                "●姓名：{name}\n"
                "●性别：{gender}\n"
                "●年龄：{age}\n"
                "●身份地位：{identity}\n\n"
                "▬ 人物画像 ▬\n"
                "●外貌特征：{appearance}\n"
                "●随身物品：{belongings}\n\n"
                "▬ 行为动机 ▬\n"
                "●显性目标：{goal}\n"
                "●隐性动机：{motive}\n\n"
                "▬ 标志特征 ▬\n"
                "●人设金句：{tagline}"
            )
            
            # 保持原始空值处理方式
            preview_content = preview_template.format(
                role_type=data['role_type'] or "未指定类型",
                name=data['name'] or "未知",
                gender=data['gender'] or "未知", 
                age=data['age'] or "未知",
                identity=data['identity'] or "未定义",
                appearance=data['appearance'] or "暂无描述",
                belongings=data['belongings'] or "无特殊物品",
                goal=data['goal'] or "目标未明确",
                motive=data['motive'] or "动机待挖掘",
                tagline=data['tagline'] or "暂无特色标签"
            )
            
            # 更新预览内容
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, preview_content)
            self.preview_text.config(state=tk.DISABLED)

    def _open_full_edit(self, event=None):
        """修复文本编辑器撤销检查"""
        edit_win = tk.Toplevel(self)
        edit_win.title("完整角色档案编辑")
        
        # 窗口居中
        edit_win.update_idletasks()
        width = 600
        height = 450
        x = (edit_win.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_win.winfo_screenheight() // 2) - (height // 2)
        edit_win.geometry(f'{width}x{height}+{x}+{y}')

        # 添加文本编辑器的撤销功能
        editor = tk.Text(edit_win, wrap=tk.WORD, font=('宋体', 11), undo=True)
        editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        editor.insert(tk.END, self.preview_text.get(1.0, tk.END))
        
        # 正确配置撤销功能
        editor.configure(
            undo=True, 
            autoseparators=True, 
            maxundo=50
        )
        
        # 绑定快捷键（移除不存在的edit_canundo检查）
        editor.bind("<Control-z>", lambda e: self._safe_undo(editor))
        editor.bind("<Control-y>", lambda e: self._safe_redo(editor))
        editor.bind("<Control-Z>", lambda e: self._safe_redo(editor))

        # 初始化撤销栈
        editor.edit_reset()
        editor.edit_modified(False)

        # 保存按钮
        ttk.Button(
            edit_win, 
            text="保存修改",
            command=lambda: self._save_edit_content(editor.get(1.0, tk.END))
        ).pack(pady=5)

    def _safe_undo(self, editor):
        """增强文本编辑器撤销"""
        try:
            # 检查是否可以撤销
            editor.edit_undo()
            # 自动重置修改标志
            editor.edit_modified(False)
        except tk.TclError as e:
            if "nothing to undo" not in str(e):
                logging.error(f"编辑器撤销失败：{str(e)}")
        return "break"

    def _safe_redo(self, editor):
        """增强的通用重做方法"""
        try:
            editor.edit_redo()
        except tk.TclError as e:
            if "nothing to redo" not in str(e):
                logging.error(f"重做失败：{str(e)}")
        return "break"

    def _save_edit_content(self, content):
        """保存完整档案时进行有效性验证"""
        try:
            parsed_data = self._parse_free_text(content)
            
            # 获取当前创作类型
            with open(self.config_file, "r", encoding='utf-8') as f:
                creation_type = yaml.safe_load(f).get("base_config", {}).get("creation_type", "网络小说")
            
            # 验证角色定位
            valid_role_types = self.ROLE_TYPES.get(creation_type, [])
            if parsed_data.get("role_type") and parsed_data["role_type"] not in valid_role_types:
                raise ValueError(f"角色定位必须为：{', '.join(valid_role_types)}")
            
            # 验证性别
            valid_genders = ["男", "女", "其他"]
            if parsed_data.get("gender") and parsed_data["gender"] not in valid_genders:
                raise ValueError(f"性别必须为：{', '.join(valid_genders)}")
            
            if self.current_role_id:
                # 更新数据并刷新界面
                self.roles[self.current_role_id].update(parsed_data)
                self._show_role_data(self.roles[self.current_role_id])  # 同步表单
                self._update_preview()  # 同步预览
                self._save_config()     # 保存到文件
                messagebox.showinfo("成功", "修改已同步到所有界面")
            else:
                messagebox.showerror("错误", "请先选择要编辑的角色")

        except Exception as e:
            messagebox.showerror("验证失败", str(e))

    def _parse_free_text(self, text):
        logging.debug(f"开始解析文本：\n{text}")
        field_map = {
            "角色定位": "role_type",
            "姓名": "name",
            "性别": "gender",
            "年龄": "age",
            "身份地位": "identity",
            "外貌特征": "appearance",
            "随身物品": "belongings",
            "显性目标": "goal",
            "隐性动机": "motive",
            "人设金句": "tagline"
        }

        valid_roles = set()
        for role_list in self.ROLE_TYPES.values():
            valid_roles.update(role_list)

        lines = [line.strip() for line in text.split('\n') if line.strip()]
        parsed = {}
        
        # 增强核心定位解析
        core_section_found = False
        for i, line in enumerate(lines):
            if '▬ 核心定位 ▬' in line:
                core_section_found = True
                # 查找后续所有以●开头的行
                for j in range(i+1, len(lines)):
                    if lines[j].startswith('●'):
                        role_line = lines[j]
                        # 提取角色定位（兼容带[]和不带的情况）
                        role_type = role_line.split('：')[-1].strip().strip('[]')
                        if role_type in valid_roles:
                            parsed['role_type'] = role_type
                            break
                break  # 找到核心定位段落后立即退出循环
        
        if not core_section_found:
            raise ValueError("必须包含核心定位段落（▬ 核心定位 ▬）")

        # 其他字段解析优化
        current_section = None
        for line in lines:
            if line.startswith('▬'):
                current_section = line.replace('▬', '').strip()
                continue
            
            if line.startswith('●'):
                parts = line[1:].split('：', 1)
                if len(parts) == 2:
                    field_key = parts[0].strip()
                    value = parts[1].strip().strip('[]')  # 去除可能存在的方括号
                    if field_key in field_map:
                        parsed[field_map[field_key]] = value
                    else:
                        logging.warning(f"忽略未知字段：{field_key}")
        
        # 最终验证
        if 'role_type' not in parsed:
            raise ValueError("必须明确指定角色定位")
        if parsed['role_type'] not in valid_roles:
            raise ValueError(f"角色类型必须来自：{', '.join(valid_roles)}")

        logging.debug(f"解析结果：{json.dumps(parsed, ensure_ascii=False)}")
        return parsed

    def _clear_form(self):
        """清空表单"""
        self.role_type.set('')
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set('')
            else:
                entry.delete(0, tk.END)
        self.entries["gender"].set("男")
        self._update_preview()

    def _record_operation(self, op_type, role_id, snapshot=None):
        """增强操作记录逻辑"""
        # 自动记录完整快照
        if op_type in ['create', 'delete']:
            self.operation_history.append({
                'type': op_type,
                'role_id': role_id,
                'data': self.roles.get(role_id) if op_type == 'delete' else None
            })
        elif op_type == 'update' and role_id in self.roles:
            # 自动保存修改前的完整数据
            self.operation_history.append({
                'type': 'update',
                'role_id': role_id,
                'data': snapshot.copy() if snapshot else self.roles[role_id].copy()
            })
        # 限制历史记录长度
        if len(self.operation_history) > 50:
            self.operation_history.pop(0)

    def _undo_last(self):
        """增强撤销功能"""
        if not self.operation_history:
            messagebox.showinfo("提示", "没有可撤销的操作")
            return

        last_op = self.operation_history.pop()
        
        try:
            if last_op['type'] == 'create':
                # 撤销新建：删除角色
                del self.roles[last_op['role_id']]
                if self.current_role_id == last_op['role_id']:
                    self.current_role_id = next(iter(self.roles)) if self.roles else None
                self._update_role_list()
                
            elif last_op['type'] == 'delete':
                # 撤销删除：恢复角色数据
                self.roles[last_op['role_id']] = last_op['data']
                self.current_role_id = last_op['role_id']
                self._update_role_list()
                
            elif last_op['type'] == 'update':
                # 撤销修改：恢复数据
                role_id = last_op['role_id']
                self.roles[role_id] = last_op['data']
                if self.current_role_id == role_id:
                    self._show_role_data(self.roles[role_id])
                
            self._save_config()  # 撤销后自动保存
            
        except Exception as e:
            messagebox.showerror("撤销失败", str(e))

    def _ai_generate_role(self):
        """打开AI生成窗口"""
        from core.api_client.deepseek import api_client
        
        try:
            with open(self.config_file, "r", encoding='utf-8') as f:
                novel_config = yaml.safe_load(f).get("base_config", {})
                novel_name = novel_config.get("novel_name", "当前小说")
                creation_type = novel_config.get("creation_type")  # 直接使用配置项
                
                if not creation_type:
                    raise ValueError("配置文件中缺少创作类型(creation_type)")
                
                # 严格匹配当前类型
                if creation_type not in self.ROLE_TYPES:
                    raise ValueError(f"无效的创作类型：{creation_type}，请使用：{', '.join(self.ROLE_TYPES.keys())}")
                
                available_roles = self.ROLE_TYPES[creation_type]
                existing_roles = [r["role_type"] for r in self.roles.values()]
                candidates = [rt for rt in available_roles if rt not in existing_roles]
                selected_role = random.choice(candidates) if candidates else random.choice(available_roles)

        except Exception as e:
            messagebox.showerror("配置错误", f"加载配置失败：{str(e)}")
            return

        # 更新提示词中的类型引用
        prompt = f"""你是一个专业的{creation_type}作家，请为《{novel_name}》生成一个{selected_role}的详细角色设定。要求包含：
        1. 姓名要符合{creation_type}的{selected_role}定位
        2. 年龄需要与{selected_role}的典型设定匹配
        3. 身份地位要体现{creation_type}中{selected_role}的特点
        4. 显性目标和隐性动机要有戏剧冲突
        5. 人设金句要突出角色性格

        必须严格遵循以下要求：
        1. 角色定位必须从以下列表选择：{", ".join(available_roles)}
        2. 不要自行发明新的角色类型
        3. 所有字段必须完整填写
        
        如：●姓名：夜无殇
        ...（其他字段保持相同格式）
        
        请严格使用以下格式（不要使用方括号）：
        
        ▬ 核心定位 ▬
        ●角色定位：[角色定位]
        ▬ 基础信息 ▬
        ●姓名：[姓名]
        ●性别：[性别]
        ●年龄：[年龄]
        ●身份地位：[身份地位]
        ▬ 人物画像 ▬
        ●外貌特征：[详细描述]
        ●随身物品：[特征物品]
        ▬ 行为动机 ▬
        ●显性目标：[明确目标]
        ●隐性动机：[隐藏动机]
        ▬ 标志特征 ▬
        ●人设金句：[人设金句]"""

        # 创建生成窗口（仅界面，不启动生成）
        gen_win = tk.Toplevel(self)
        gen_win.title("AI角色生成助手")
        
        # 窗口居中显示
        gen_win.update_idletasks()  # 确保获取准确的窗口尺寸
        width = 600
        height = 500
        x = (gen_win.winfo_screenwidth() - width) // 2
        y = (gen_win.winfo_screenheight() - height) // 2
        gen_win.geometry(f"{width}x{height}+{x}+{y}")
        gen_win.resizable(False, False)
        
        # 拦截关闭事件
        gen_win.protocol("WM_DELETE_WINDOW", lambda: self._safe_close(gen_win))

        # 生成窗口组件
        editor = tk.Text(
            gen_win, 
            wrap=tk.WORD, 
            font=('宋体', 11), 
            undo=True,  # 启用内置撤销
            autoseparators=True,
            maxundo=50
        )
        editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 绑定撤销快捷键
        editor.bind("<Control-z>", lambda e: self._safe_undo(editor))
        editor.bind("<Control-y>", lambda e: self._safe_redo(editor))
        editor.bind("<Control-Z>", lambda e: self._safe_redo(editor))
        
        # 初始化撤销栈
        editor.edit_reset()
        editor.edit_modified(False)

        # 按钮容器
        btn_frame = ttk.Frame(gen_win)
        btn_frame.pack(pady=5)
        
        # 新增生成控制变量
        self.generating = False
        self.stop_generation = False
        
        # 操作按钮（调整顺序和功能）
        ttk.Button(btn_frame, text="开始生成", width=12, 
                 command=lambda: self._start_generation(gen_win, prompt, editor)).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="停止生成", width=12, 
                 command=self._stop_generation).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="保存新角色", width=12,
                 command=lambda: self._safe_save(editor, gen_win)).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="清空内容", width=12,
                 command=lambda: editor.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=3)

        # 初始化状态标签
        self.status_label = ttk.Label(gen_win, text="就绪")
        self.status_label.pack(side=tk.BOTTOM, pady=5)

        # 将编辑器保存为实例变量
        self.ai_editor = editor  # 新增

    def _start_generation(self, window, prompt, editor):
        """启动生成线程，安全处理流式输出"""
        if self.generating:
            messagebox.showwarning("提示", "生成正在进行中", parent=window)
            return
        
        from core.api_client.deepseek import api_client
        
        # 确保在生成前创建思维链窗口
        self._create_reasoning_window()
        if self.reasoning_window and self.reasoning_text:
            self.reasoning_text.delete(1.0, tk.END)  # 清空思维链窗口
            
        # 判断当前是否为DeepSeek-R1或Qwen-R1模型
        from modules.GlobalModule import global_config
        model_name = global_config.model_config.name
        show_reasoning = "DeepSeek-R1" in model_name or "Qwen-R1" in model_name
        
        # 如果是支持思维链的模型，显示思维链窗口
        if show_reasoning:
            self.show_reasoning_window()
        
        def safe_update_ui(func, *args):
            """确保UI组件存在时才更新"""
            if window.winfo_exists():
                window.after(0, func, *args)
        
        def safe_callback(chunk):
            """安全处理回调，确保窗口存在"""
            if not window.winfo_exists():
                return
                
            try:
                self._stream_callback(chunk)
            except Exception as e:
                logging.error(f"回调处理异常: {str(e)}")
        
        def generate_thread():
            self.generating = True
            self.stop_generation = False
            
            # 安全更新UI
            safe_update_ui(lambda: self.status_label.config(text="生成中..."))
            safe_update_ui(editor.delete, 1.0, tk.END)  # 清空编辑器内容
            
            try:
                messages = [{"role": "user", "content": prompt}]
                
                # 使用安全回调处理流式输出
                for chunk in api_client.stream_generate(messages, callback=safe_callback):
                    if self.stop_generation or not window.winfo_exists():
                        break
                    
                    # 内容会通过回调处理，这里不需要再次处理
                
                # 安全更新状态
                if window.winfo_exists() and hasattr(self, 'status_label') and self.status_label.winfo_exists():
                    status = "已停止" if self.stop_generation else "生成完成"
                    safe_update_ui(lambda: self.status_label.config(text=status))
            except Exception as e:
                logging.exception(f"生成过程出错: {str(e)}")
                if window.winfo_exists():
                    safe_update_ui(messagebox.showerror, "生成失败", str(e), parent=window)
            finally:
                self.generating = False
                self.stop_generation = False

        threading.Thread(target=generate_thread, daemon=True).start()

    def _stop_generation(self):
        """安全停止生成逻辑"""
        if self.generating:
            self.stop_generation = True
            # 确保状态标签存在
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.config(text="正在停止...")
            
            # 直接更新状态，不使用延迟
            self.generating = False
            
            # 避免使用afterx延迟回调，防止窗口关闭后出错
            # self.after(1000, lambda: [
            #    setattr(self, 'generating', False),
            #    setattr(self, 'stop_generation', False),
            #    self.status_label.config(text="已停止")
            # ])
            
            # 直接设置状态
            self.stop_generation = False
            # 仅当标签仍存在时更新
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.config(text="已停止")

    def _save_as_new_role(self, editor, gen_window):
        """保存角色时保持生成窗口打开"""
        try:
            # 获取编辑器内容前先聚焦窗口
            gen_window.focus_force()
            content = editor.get(1.0, tk.END)
            
            # 解析前强制更新界面
            self.update_idletasks()
            
            parsed = self._parse_free_text(content)
            if not parsed.get('name'):
                raise ValueError("角色必须包含姓名")

            # 创建新角色但不切换焦点
            new_id = self._add_role(silent=True)  # 新增静默模式
            
            # 更新数据但不立即刷新界面
            if new_id in self.roles:
                self.roles[new_id].update(parsed)
                self.current_role_id = new_id  # 设置为当前角色
                
                # 延迟更新界面组件
                self.after(100, lambda: [
                    self._update_role_list(select_id=new_id),
                    self._show_role_data(self.roles[new_id]),
                    self._save_config()
                ])
                
                # 创建新角色时记录完整操作
                self._record_operation('create', new_id)
                self._record_operation('update', new_id, {})  # 记录初始空状态
                
                messagebox.showinfo("保存成功", f"{parsed['name']} 已保存", parent=gen_window)
            else:
                raise ValueError("角色创建失败")

        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}", parent=gen_window)
            logging.error(f"保存错误：{traceback.format_exc()}")

    def _safe_save(self, editor, gen_window):
        """优化后的保存操作"""
        # 保存前记录生成窗口位置
        win_x = gen_window.winfo_x()
        win_y = gen_window.winfo_y()
        
        try:
            self._save_as_new_role(editor, gen_window)
            # 保存后保持窗口位置
            gen_window.geometry(f"+{win_x}+{win_y}")
            gen_window.lift()  # 保持窗口在最前
        finally:
            editor.focus_force()

    def _stream_callback(self, chunk):
        """处理流式返回的回调函数"""
        try:
            # 如果chunk是字典，可能包含思维链内容
            if isinstance(chunk, dict):
                # 处理思维链内容
                if "reasoning_content" in chunk:
                    reasoning = chunk["reasoning_content"]
                    if reasoning:
                        self._safe_update_reasoning(reasoning)
                return
            
            # 如果是普通文本内容，即增量内容，直接更新到编辑器
            if isinstance(chunk, str):
                self._safe_update_editor(self.ai_editor, chunk)
            
        except Exception as e:
            logging.error(f"流式处理错误: {str(e)}", exc_info=True)

    def _update_editor(self, editor, chunk):
        """处理流式增量更新"""
        try:
            # 如果chunk是字典，处理思维链内容
            if isinstance(chunk, dict):
                if "reasoning_content" in chunk:
                    reasoning = chunk["reasoning_content"]
                    if reasoning:
                        self.master.after(0, self._safe_update_reasoning, reasoning)
                return
            
            # 处理纯文本增量（流式输出的字符）
            if isinstance(chunk, str):
                self.master.after(0, self._safe_update_editor, editor, chunk)
                return
                
        except Exception as e:
            logging.error(f"流式处理异常: {str(e)}", exc_info=True)
            # 异常情况下，尝试直接显示内容
            try:
                if isinstance(chunk, str):
                    self.master.after(0, self._safe_update_editor, editor, chunk)
            except:
                pass

    def _safe_update_editor(self, editor, content):
        """安全更新生成助手的编辑框"""
        if editor.winfo_exists():
            editor.insert(tk.END, content)
            editor.see(tk.END)
            editor.update_idletasks()

    def _safe_close(self, window):
        """安全关闭窗口检查"""
        try:
            if self.generating:
                # 先停止生成
                self.stop_generation = True
                self.generating = False
                
                messagebox.showwarning("操作阻止", 
                    "生成正在进行中，请先点击【停止生成】再关闭窗口！", 
                    parent=window)
                return
            
            # 安全清理资源
            self.ai_editor = None  # 移除编辑器引用
            window.destroy()
        except Exception as e:
            logging.error(f"关闭窗口时出错: {str(e)}")
            # 确保窗口被销毁
            try:
                window.destroy()
            except:
                pass

    def _create_reasoning_window(self):
        """安全创建思维链窗口"""
        # 先初始化窗口对象为None
        if not hasattr(self, 'reasoning_window'):
            self.reasoning_window = None
        
        # 检查窗口有效性
        if self.reasoning_window is None or not self.reasoning_window.winfo_exists():
            self.reasoning_window = tk.Toplevel(self.master)
            self.reasoning_window.title("模型思维链")
            self.reasoning_window.protocol("WM_DELETE_WINDOW", self._hide_reasoning_window)
            self.reasoning_text = tk.Text(self.reasoning_window, wrap=tk.WORD, width=80, height=20)
            self.reasoning_text.pack(fill=tk.BOTH, expand=True)
            self.reasoning_window.withdraw()  # 初始隐藏

    def _hide_reasoning_window(self):
        """隐藏窗口代替销毁"""
        if self.reasoning_window.winfo_exists():
            self.reasoning_window.withdraw()

    def show_reasoning_window(self):
        """安全显示窗口"""
        if (hasattr(self, 'reasoning_window') and 
            self.reasoning_window is not None and 
            self.reasoning_window.winfo_exists()):
            self.reasoning_window.deiconify()
            self.reasoning_window.lift()

    def update_reasoning_display(self, content):
        """更新思维链显示"""
        self.master.after(0, lambda: self._safe_update_reasoning(content))
        
    def _safe_update_reasoning(self, content):
        """安全更新思维链显示，保持流式输出效果"""
        try:
            # 确保窗口存在
            self._create_reasoning_window()
            
            # 检查文本框有效性
            if not hasattr(self, 'reasoning_text') or not self.reasoning_text.winfo_exists():
                self.reasoning_text = tk.Text(self.reasoning_window, wrap=tk.WORD)
                self.reasoning_text.pack(fill=tk.BOTH, expand=True)
            
            # 显示窗口
            self.show_reasoning_window()
            
            # 直接在末尾追加内容（不管是否新行）
            self.reasoning_text.insert(tk.END, content)
            
            # 滚动到最底部
            self.reasoning_text.see(tk.END)
            
            # 立即更新窗口，确保内容实时显示
            self.reasoning_window.update_idletasks()
            
        except Exception as e:
            logging.error(f"更新思维链失败: {str(e)}")
            traceback.print_exc()

    def _safe_update_main(self, content):
        """安全更新主界面"""
        if self.preview_text.winfo_exists():
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.insert(tk.END, content)
            self.preview_text.see(tk.END)
            self.preview_text.config(state=tk.DISABLED)
