import tkinter as tk
from tkinter import ttk
import yaml
from pathlib import Path
from tkinter import messagebox
import time
import os
import traceback

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
        ttk.Button(btn_frame, text="保存角色", width=7, command=self._save_config).pack(side=tk.LEFT, padx=1)

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

    def _add_role(self):
        """生成唯一连续ID"""
        new_index = len(self.roles) + 1
        while f"role_{new_index}" in self.roles:
            new_index += 1
        new_id = f"role_{new_index}"
        self.current_role_id = new_id
        new_role = {
            "role_type": "",
            "name": "",
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
        # 记录新建操作
        self._record_operation('create', new_id, None)
        self._update_role_list()
        self._show_role_data(new_role)

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
        """正确收集并保存修改后的数据"""
        try:
            # 确保收集当前表单数据
            if self.current_role_id:
                # 获取所有输入框的当前值
                current_data = {
                    "role_type": self.role_type.get(),
                    **{k: v.get() for k, v in self.entries.items()}
                }
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
            
        except Exception as e:
            error_msg = f"保存失败：{str(e)}\n跟踪信息：{traceback.format_exc()}"
            messagebox.showerror("错误", error_msg)

    def _update_role_list(self):
        """更新下拉框后自动选择有效项"""
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
            if self.current_role_id not in self.roles:
                self.current_role_id = next(iter(self.roles))
            current_name = self._get_display_name(self.current_role_id)
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

    def _show_role_data(self, data):
        """显示前验证当前角色"""
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
            self._update_preview()
        else:
            self._clear_form()

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
        """绑定输入框变更事件"""
        if not hasattr(self, 'preview_text'):
            return

        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.bind("<<ComboboxSelected>>", self._update_preview)
            else:
                entry.bind("<KeyRelease>", self._update_preview)
        self.role_type.bind("<<ComboboxSelected>>", self._update_preview)

    def _update_preview(self, event=None):
        """生成格式优化的预览内容"""
        if not hasattr(self, 'preview_text') or self.preview_text is None:
            return  # 防止组件未初始化时调用
        
        data = {
            'role_type': self.role_type.get(),
            **{k: v.get() for k, v in self.entries.items()}
        }
        
        # 修正后的预览模板
        preview_template = (
            "▬ 核心定位 ▬\n"
            "●{role_type}\n\n"
            "▬ 基础信息 ▬\n"
            "●姓名：{name}\n"
            "●性别：{gender}\n"
            "●年龄：{age}\n"
            "●身份：{identity}\n\n"
            "▬ 人物画像 ▬\n"
            "●外貌：{appearance}\n"
            "●物品：{belongings}\n\n"
            "▬ 行为动机 ▬\n"
            "●显性目标：{goal}\n"
            "●隐性动机：{motive}\n\n"
            "▬ 标志特征 ▬\n"
            "●人物金句：{tagline}"
        )
        
        # 处理空值
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
        
        # 插入文本时应用格式
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, preview_content, 'left')  # 应用左对齐标签
        self.preview_text.config(state=tk.DISABLED)

    def _open_full_edit(self):
        """打开居中显示的完整编辑窗口"""
        edit_win = tk.Toplevel(self)
        edit_win.title("完整角色档案编辑")
        
        # 窗口居中
        edit_win.update_idletasks()
        width = 600
        height = 450
        x = (edit_win.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_win.winfo_screenheight() // 2) - (height // 2)
        edit_win.geometry(f'{width}x{height}+{x}+{y}')

        # 编辑组件
        from tkinter.scrolledtext import ScrolledText
        editor = ScrolledText(edit_win, wrap=tk.WORD, font=('宋体', 11))
        editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 加载当前内容
        editor.insert(tk.END, self.preview_text.get(1.0, tk.END))
        
        # 保存按钮
        ttk.Button(
            edit_win, 
            text="保存修改",
            command=lambda: self._save_edit_content(editor.get(1.0, tk.END))
        ).pack(pady=5)

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
        """增强段落标题处理"""
        field_map = {
            "核心定位": "role_type",
            "姓名": "name",
            "性别": "gender",
            "年龄": "age",
            "身份": "identity",
            "外貌": "appearance",
            "物品": "belongings",
            "目标": "goal",
            "动机": "motive",
            "金句": "tagline"
        }
        
        parsed = {}
        current_field = None
        in_section = False  # 新增状态标记
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue  # 跳过空行
            
            # 识别段落标题行
            if line.startswith('▬') and line.endswith('▬'):
                current_field = None
                in_section = True
                continue
            elif in_section:
                # 段落标题后的首行重置状态
                in_section = False
                current_field = None

            # 处理核心定位特殊格式
            if line.startswith('●') and '：' not in line and current_field is None:
                parsed['role_type'] = line[1:].strip()
                continue
            
            # 仅处理包含冒号的字段行
            if '：' in line:
                field_part, value_part = line.split('：', 1)
                field_key = field_part.strip().lstrip('●│')
                if field_key in field_map:
                    current_field = field_map[field_key]
                    parsed[current_field] = value_part.strip()
            elif current_field:
                # 仅当已有当前字段时追加内容
                parsed[current_field] += '\n' + line.strip()
            
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

    def _record_operation(self, op_type, role_id, data):
        """记录操作历史"""
        self.operation_history.append({
            'type': op_type,
            'role_id': role_id,
            'data': data,
            'timestamp': time.time()
        })
        # 保留最近10条记录
        if len(self.operation_history) > 10:
            self.operation_history.pop(0)

    def _undo_last(self):
        """撤销操作时恢复原始ID"""
        if not self.operation_history:
            return
        
        last_op = self.operation_history.pop()
        
        if last_op['type'] == 'delete':
            # 恢复删除前的状态
            self.roles = last_op['data']['original_roles']
            self.current_role_id = last_op['data']['original_current']
            self._update_role_list()
            self._show_role_data(self.roles[self.current_role_id])
            self._save_config()
        elif last_op['type'] == 'create':
            # 删除新建的角色
            if last_op['role_id'] in self.roles:
                del self.roles[last_op['role_id']]
                if self.current_role_id == last_op['role_id']:
                    if self.roles:
                        self.current_role_id = next(iter(self.roles))
                        self._show_role_data(self.roles[self.current_role_id])
                    else:
                        self.current_role_id = None
                        self._clear_form()
            self._update_role_list()
        
        self._save_config()
