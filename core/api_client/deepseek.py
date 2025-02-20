from openai import OpenAI
from typing import Iterator
from modules.GlobalModule import global_config
import os
import httpx
from modules.AuthModule import validate_token
import logging
from utils.config_loader import get_version_info, get_api_key
from cryptography.fernet import Fernet

class DeepSeekAPIClient:
    def __init__(self):
        self.key_cache = {}  # 简单缓存机制

    # def _fetch_encrypted_key(self) -> str:
    #     """从代理服务器获取加密密钥"""
    #     try:
    #         resp = httpx.post(
    #             "https://your-proxy.com/api/get-key",
    #             headers={"Authorization": f"Bearer {self._get_user_token()}"},
    #             timeout=5
    #         )
    #         resp.raise_for_status()
    #         return resp.json()["encrypted_key"]
    #     except httpx.HTTPError as e:
    #         self._handle_error(e)
            
    # def _get_api_key(self) -> str:
    #     """获取解密后的API密钥"""
    #     if cached := self.key_cache.get('api_key'):
    #         return cached
        
    #     encrypted = self._fetch_encrypted_key()
    #     decrypted = decrypt_key(encrypted)
    #     self.key_cache['api_key'] = decrypted
    #     return decrypted
    
    # def decrypt_key(encrypted: str) -> str:
    #     """解密临时密钥"""
    #     f = Fernet(os.getenv('APP_JWT_SECRET').encode())
    #     return f.decrypt(encrypted.encode()).decode()

    def _get_api_key(self) -> str:
        """根据模型配置获取对应密钥"""
        from utils.config_loader import get_api_key
        provider = global_config.model_config.provider  # 从模型配置获取提供商
        return get_api_key()["providers"].get(provider, "")

    def generate(self, messages: list) -> str:
        """直接调用第三方API生成内容"""
        api_key = self._get_api_key()
        
        response = httpx.post(
            f"{global_config.model_config.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": global_config.model_config.model,
                "messages": messages,
                "temperature": global_config.generation_param.temperature,
                "max_tokens": self._calculate_max_tokens(messages)
            },
            timeout=global_config.security.request_timeout
        )
        return self._parse_response(response)

    def stream_generate(self, messages: list) -> Iterator[str]:
        """流式生成（直接调用API）"""
        api_key = self._get_api_key()
        
        try:
            with httpx.Client(timeout=None) as client:
                response = client.stream(
                    "POST",
                    f"{global_config.model_config.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": global_config.model_config.model,
                        "messages": messages,
                        "temperature": global_config.generation_param.temperature,
                        "max_tokens": self._calculate_max_tokens(messages),
                        "stream": True  # 启用流式
                    }
                )
                for chunk in response.iter_lines():
                    yield chunk
                
        except httpx.HTTPError as e:
            self._handle_api_error(e)

    def _build_headers(self, token: str) -> dict:
        return {
            "Authorization": f"Bearer {token}",
            "X-Client-Version": get_version_info(),
            "User-Agent": f"NovelWriter/{get_version_info()['version']}"
        }

    # def _get_user_token(self) -> str:
    #     """从界面获取用户令牌"""
    #     from ui.panels import ParameterPanel
    #     return ParameterPanel.instance.user_token_entry.get()

    def _build_params(self, messages: list) -> dict:
        """构建请求参数"""
        return {
            'temperature': global_config.generation_param.temperature,
            'frequency_penalty': global_config.generation_param.frequency_penalty,
            'presence_penalty': global_config.generation_param.presence_penalty,
            'top_p': global_config.generation_param.top_p,
            'stream': global_config.generation_param.stream,
            'response_format': global_config.generation_param.response_format
        }

    def _calculate_max_tokens(self, messages: list) -> int:
        """计算安全的最大token数"""
        content = " ".join([msg["content"] for msg in messages])
        content_tokens = len(content) // 4  # 简单估算
        max_available = int(global_config.model_config.context_window * 0.8)
        return min(
            global_config.generation_param.max_tokens,
            max_available - content_tokens
        )

    @staticmethod
    def _handle_api_error(error: httpx.HTTPError):
        from tkinter import messagebox
        error_map = {
            401: "认证失效，请刷新令牌",
            429: "请求过于频繁，请稍后再试",
            500: "服务器内部错误",
            503: "服务暂时不可用"
        }
        msg = error_map.get(error.response.status_code, 
                           f"API请求失败: {str(error)}")
        messagebox.showerror("请求错误", msg)
        logging.error(f"API Error: {error}")

# 单例实例
api_client = DeepSeekAPIClient()

# 测试请求头构建
headers = api_client._build_headers("test_token")
assert headers["Authorization"] == "Bearer test_token"
assert "X-Client-Version" in headers 