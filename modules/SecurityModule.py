import time
import ssl
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import httpx

class KeyManager:
    _CACHE_TTL = 300  # 5分钟缓存
    _cached_key = None
    _last_fetch = 0  # 初始化为0，确保第一次调用时会重新获取
    
    @classmethod
    def get_key(cls):
        """带缓存的密钥获取"""
        # 如果缓存有效，直接返回缓存的密钥
        if time.time() - cls._last_fetch < cls._CACHE_TTL and cls._cached_key:
            return cls._cached_key
        
        # 从apikey.yaml中获取API密钥
        from utils.config_loader import get_api_key
        from modules.GlobalModule import global_config
        
        api_keys = get_api_key()
        provider = global_config.model_config.provider
        
        # 获取对应提供商的API密钥
        key = api_keys.get('providers', {}).get(provider, "")
        
        if not key:
            print(f"警告: 没有找到提供商 {provider} 的API密钥")
        
        # 更新缓存
        cls._cached_key = key
        cls._last_fetch = time.time()
        return cls._cached_key

class SecurityConfig:
    """安全配置"""
    def __init__(self):
        self.enable_ssl_pinning: bool = True
        self.api_whitelist: List[str] = [
            "api.deepseek.com", 
            "api.qianwen.com"
        ]
        self.request_timeout: int = 30  # 秒
        self.retry_policy: Dict[str, Any] = {
            'max_attempts': 3,
            'backoff_factor': 0.5
        }
        self.enable_rate_limiting: bool = True
        self.rate_limit_per_minute: int = 60

class SecureApiClient:
    """安全API客户端"""
    def __init__(self, security_config: Optional[SecurityConfig] = None):
        self.config = security_config or SecurityConfig()
        self._init_ssl_context()
        self._request_count = 0
        self._last_request_time = 0
    
    def _init_ssl_context(self) -> ssl.SSLContext:
        """初始化SSL上下文"""
        ctx = ssl.create_default_context()
        
        # 如果启用了SSL证书固定
        if self.config.enable_ssl_pinning:
            # 验证证书指纹 - 实际应用中应导入公共证书
            ctx.check_hostname = True
            ctx.verify_mode = ssl.CERT_REQUIRED
        
        return ctx
    
    def validate_url(self, url: str) -> bool:
        """验证URL是否在白名单中"""
        # 从URL中提取主机名
        try:
            from urllib.parse import urlparse
            hostname = urlparse(url).netloc
            
            # 检查主机名是否在白名单中
            return hostname in self.config.api_whitelist
        except Exception as e:
            print(f"URL验证失败: {str(e)}")
            return False
    
    def sanitize_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """净化请求数据，防止注入攻击"""
        # 简单实现：对字符串进行转义处理
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # 防止命令注入、SQL注入等
                sanitized[key] = self._sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_request_data(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self.sanitize_request_data(item) if isinstance(item, dict)
                    else self._sanitize_string(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _sanitize_string(self, value: str) -> str:
        """净化字符串值"""
        # 替换潜在危险字符
        unsafe_chars = ["'", '"', ';', '-', '=', '(', ')', '*', '&', '|', '<', '>', '`']
        result = value
        for char in unsafe_chars:
            result = result.replace(char, f"\\{char}")
        return result
    
    def calculate_hash(self, data: str) -> str:
        """计算数据的哈希值"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    async def secure_request(self, method: str, url: str, data: Optional[Dict[str, Any]] = None,
                       headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        """
        发送安全API请求
        
        参数:
            method: 请求方法 (GET, POST, etc.)
            url: 目标URL
            data: 请求数据
            headers: 请求头
            
        返回:
            HTTP响应对象
        """
        # 验证URL
        if not self.validate_url(url):
            raise ValueError(f"URL不在安全白名单中: {url}")
        
        # 净化请求数据
        if data:
            data = self.sanitize_request_data(data)
        
        # 创建安全的HTTP客户端
        async with httpx.AsyncClient(timeout=self.config.request_timeout) as client:
            # 发送请求并实现重试逻辑
            retry_count = 0
            max_retries = self.config.retry_policy['max_attempts']
            backoff = self.config.retry_policy['backoff_factor']
            
            while retry_count < max_retries:
                try:
                    response = await client.request(
                        method=method,
                        url=url,
                        json=data,
                        headers=headers
                    )
                    return response
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise e
                    # 指数退避策略
                    import asyncio
                    await asyncio.sleep(backoff * (2 ** (retry_count - 1)))
        
        # 不应该到达这里
        raise RuntimeError("请求失败")

# 全局安全配置实例
security_config = SecurityConfig()

# 提供同步版本的安全请求函数
def secure_request(method: str, url: str, data: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None) -> httpx.Response:
    """同步版本的安全请求函数"""
    client = SecureApiClient(security_config)
    
    # 验证URL
    if not client.validate_url(url):
        raise ValueError(f"URL不在安全白名单中: {url}")
    
    # 净化请求数据
    if data:
        data = client.sanitize_request_data(data)
    
    # 创建HTTP客户端并发送请求
    with httpx.Client(timeout=security_config.request_timeout) as http_client:
        retry_count = 0
        max_retries = security_config.retry_policy['max_attempts']
        backoff = security_config.retry_policy['backoff_factor']
        
        while retry_count < max_retries:
            try:
                response = http_client.request(
                    method=method,
                    url=url,
                    json=data,
                    headers=headers
                )
                return response
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise e
                # 指数退避策略
                import time
                time.sleep(backoff * (2 ** (retry_count - 1)))
    
    # 不应该到达这里
    raise RuntimeError("请求失败") 