from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from utils.config_loader import load_config
import os
import threading
import httpx
from datetime import datetime


# 全局API配置变量（运行时动态修改）
class APIModelConfig:
    """模型基础配置"""
    def __init__(self):
        self.provider: str = "DeepSeek"  # 服务商名称
        self.base_url: str = "https://api.deepseek.com/v1"
        self.model: str = "deepseek-reasoner"  # 官方模型标识
        self.context_window: int = 128000  # 最新支持128k上下文
        self.name: str = "DeepSeek-R1"  # 默认模型名称

class GenerationParameter:
    """生成参数配置"""
    def __init__(self, **kwargs):
        self.temperature: float = kwargs.get('temperature', 1.0)  # 0.0-2.0
        self.top_p: float = kwargs.get('top_p', 1.0)           # 0.0-1.0
        self.max_tokens: int = kwargs.get('max_tokens', 2000)  # 根据context_window自动限制
        self.response_format: dict = kwargs.get('response_format', {"type": "text"})
        self.frequency_penalty: float = kwargs.get('frequency_penalty', 0.0)  # [-2.0, 2.0]
        self.presence_penalty: float = kwargs.get('presence_penalty', 0.0)   # [-2.0, 2.0]

class GlobalAPIConfig:
    """统一配置入口"""
    def __init__(self):
        self.model_config = APIModelConfig()
        self.generation_params = GenerationParameter()  # 修正变量名
        self.model_mapping = self._load_model_config()
        self.connection_monitor = ConnectionMonitor()

    def _load_model_config(self) -> dict:
        """从配置文件加载模型映射"""
        try:
            # 仅加载系统级模型配置
            system_config = load_config('model_config.yaml') or {}
            return system_config.get('models', {})
        except Exception as e:
            print(f"模型配置加载失败: {e}")
            return {}

    def load_user_config(self):
        """加载用户配置"""
        user_config = load_config('user_config.yaml') or {}
        # 应用用户选择的模型
        selected = user_config.get('selected_model', 'DeepSeek-R1')
        self.update_model(selected)

    def update_model(self, model_name: str):
        """更新模型配置"""
        config = self.model_mapping.get(model_name)
        if config:
            # 更新模型基础配置
            self.model_config.__dict__.update({
                'name': model_name,
                'provider': config['provider'],
                'base_url': config['base_url'],
                'model': config['model'],
                'context_window': config['context_window']
            })
            # 自动调整参数
            self._adjust_parameters(config)
    
    def _adjust_parameters(self, config: dict):
        """自动调整生成参数"""
        safe_max_tokens = int(config["context_window"] * 0.8)
        if self.generation_params.max_tokens > safe_max_tokens:
            self.generation_params.max_tokens = safe_max_tokens

    def save_config(self):
        """保存当前配置"""
        config_to_save = {
            "selected_model": self.model_config.name  # 仅保存模型名称
        }
        # 确保不保存其他内容

    def load_config(self, config: dict):
        """加载配置"""
        model_name = config.get("selected_model", "DeepSeek-R1")
        self.update_model(model_name)
        # 加载其他参数...

    def validate_configs(self):
        """配置验证"""
        errors = []
        
        # 验证模型配置
        if not self.model_mapping:
            errors.append("未找到有效的模型配置")
        
        # 验证用户选择是否存在
        if self.model_config.name not in self.model_mapping:
            errors.append(f"选择的模型 {self.model_config.name} 不存在")
        
        if errors:
            raise ValueError("配置错误: " + "; ".join(errors))

class ConnectionMonitor:
    def __init__(self):
        self._status = False
        self._timer = None
        self.last_check = "尚未检查"
        
    def start_monitoring(self, interval=60):
        """启动定时状态检查"""
        self._check_status()
        self._timer = threading.Timer(interval, self.start_monitoring, [interval])
        self._timer.daemon = True
        self._timer.start()
        
    def _check_status(self):
        """实际执行状态检查"""
        try:
            from utils.config_loader import get_api_key
            api_key = get_api_key()["providers"].get(global_config.model_config.provider, "")
            
            response = httpx.get(
                f"{global_config.model_config.base_url}/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5
            )
            self._status = response.status_code == 200
            self.last_check = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            self._status = False
            self.last_check = f"检查失败: {str(e)}"
            
    @property
    def status(self):
        return self._status

global_config = GlobalAPIConfig()

# class SecurityConfig:
#     def __init__(self):
#         self.enable_ssl_pinning = True
#         self.api_whitelist = ["your-proxy-server.com"]
#         self.request_timeout = 30  # 秒
#         self.retry_policy = {
#             'max_attempts': 3,
#             'backoff_factor': 0.5
#         }


# global_config.security = SecurityConfig()

# # 验证安全配置加载
# print(global_config.security.enable_ssl_pinning)  # True
# print(global_config.security.api_whitelist)  # ["your-proxy-server.com"]

# def initialize_security():
#     if global_config.security.enable_ssl_pinning:
#         # 实现SSL证书固定逻辑
#         import ssl
#         ctx = ssl.create_default_context()
#         ctx.load_verify_locations(cafile="proxy_server.pem") 


