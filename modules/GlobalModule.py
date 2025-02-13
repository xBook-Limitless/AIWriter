from typing import Optional  # 添加类型提示导入

# 全局API配置变量（运行时动态修改）
class APIProvider:
    """API服务商基础配置"""
    def __init__(self):
        self.name: str = "deepseek"          # 默认服务商
        self.base_url: str = "https://api.deepseek.com/v1"  # 确保版本正确
        self.auth_endpoint: str = "/auth/v1"  # 更新认证路径
        self.rate_limit: int = 60            # 默认每分钟60次

class APIModel:
    """模型基础配置"""
    def __init__(self):
        self.base_model: str = "deepseek-chat"  # 官方模型标识
        self.context_window: int = 4096        # 默认上下文长度

class APICredential:
    """API密钥管理"""
    def __init__(self):
        self.api_key: str = "sk-994f41664cef4351a2b04442ff09ee13"
        self.valid_until: float = 0            # 默认永不过期

class GenerationParameter:
    """生成温度配置"""
    def __init__(self):
        self._temperature = 1.0  # 默认值从0.7改为1.0
        self.top_p: float = 1.0    # 新增官方参数
        self.max_tokens: int = 2048 # 默认值从2000改为2048
        self.frequency_penalty: float = 0
        self.presence_penalty: float = 0
        self.response_format: dict = {"type": "text"}  # 新增官方参数

    @property
    def temperature(self) -> float:
        return self._temperature

    @temperature.setter
    def temperature(self, value: float):
        """设置温度值并验证范围"""
        if not (0.0 <= value <= 1.5):
            raise ValueError(f"温度值 {value} 超出允许范围 (0.0-1.5)")
        self._temperature = value

    def validate_all(self):
        """验证所有参数"""
        errors = []
        if not (0.0 <= self.temperature <= 1.5):
            errors.append(f"温度值 {self.temperature} 超出范围")
        if self.max_tokens < 1:
            errors.append("最大token数必须大于0")
        if errors:
            raise ValueError("参数验证失败: " + "; ".join(errors))

class AdvancedGenerationParameter:
    """高级生成参数配置"""
    def __init__(self):
        self.stream_options = None
        self.tools = None
        self.tool_choice = "none"
        self.logprobs = False
        self.top_logprobs = None
        self.stop = None
        self.stream = False
        self.presence_penalty = 0.0
        self.frequency_penalty = 0.0

    def to_dict(self):
        """将高级参数转换为字典"""
        return {
            'stream': self.stream,
            'stop': self.stop,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'stream_options': self.stream_options,
            'tools': self.tools,
            'tool_choice': self.tool_choice,
            'logprobs': self.logprobs,
            'top_logprobs': self.top_logprobs,
            'top_p': self.top_p  # 移动到此处
        }

    def validate(self):
        """参数验证"""
        errors = []
        if not -2.0 <= self.presence_penalty <= 2.0:
            errors.append(f"存在惩罚值 {self.presence_penalty} 超出范围(-2.0~2.0)")
        if not -2.0 <= self.frequency_penalty <= 2.0:
            errors.append(f"频率惩罚值 {self.frequency_penalty} 超出范围(-2.0~2.0)")
        if self.stream_interval < 0.05:
            errors.append("流式间隔不能小于0.05秒")
        if errors:
            raise ValueError("高级参数错误: " + "; ".join(errors))
    
class PromptTemplate:
    """统一提示词模板管理"""
    def __init__(self):
        self.unified_template: str = """
        [SYSTEM_ROLE]
        你是一个AI助手，根据以下规则处理输入：
        {system_rules}
        
        [USER_FORMAT]
        输入内容：{user_input}
        附加要求：{requirements}
        """

class GlobalAPIConfig:
    """单一实例全局配置"""
    def __init__(self):
        # 直接初始化唯一实例
        self.provider = APIProvider()
        self.model = APIModel()
        self.credential = APICredential()
        
        # 参数配置
        self.parameters = GenerationParameter()
        self.advanced = AdvancedGenerationParameter()

    def validate(self):
        """简化验证逻辑"""
        if not hasattr(self.provider, 'base_url'):
            raise ValueError("必须配置服务商base_url")
        if not self.credential.api_key:
            raise ValueError("必须配置API密钥")

# 全局单例访问点
global_api_config = GlobalAPIConfig()

