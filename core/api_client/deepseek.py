from openai import OpenAI
from typing import Iterator, Optional, Dict, Any, List
from modules.GlobalModule import global_config
import os
import httpx
import time
import logging
from modules.AuthModule import validate_token
from modules.SecurityModule import KeyManager
from utils.config_loader import get_version_info, get_api_key
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class DeepSeekAPIClient:
    """DeepSeek API客户端，处理与DeepSeek API的所有交互"""
    
    def __init__(self):
        self.key_cache = {}  # 简单缓存机制
        self.max_retries = 3  # 最大重试次数
        self.retry_delay = 2  # 重试延迟（秒）
        logger.debug("初始化DeepSeek API客户端")
    
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
        """获取API密钥"""
        # 使用KeyManager获取密钥
        return KeyManager.get_key()

    def generate(self, messages: List[Dict[str, Any]]) -> str:
        """生成文本"""
        logger.debug(f"开始生成文本，消息数: {len(messages)}")
        
        for attempt in range(self.max_retries):
            try:
                api_key = self._get_api_key()
                if not api_key:
                    logger.error("未找到API密钥")
                    return "错误: 未找到API密钥，请在设置中配置"
                
                client = OpenAI(
                    api_key=api_key,
                    base_url=global_config.model_config.base_url
                )
                
                params = {
                    "model": global_config.model_config.model,
                    "messages": messages,
                    "temperature": global_config.generation_params.temperature,
                    "top_p": global_config.generation_params.top_p,
                    "frequency_penalty": global_config.generation_params.frequency_penalty,
                    "presence_penalty": global_config.generation_params.presence_penalty,
                    "max_tokens": self._calculate_max_tokens(messages),
                    "stream": False,
                }
                
                logger.debug(f"使用模型: {params['model']}")
                
                response = client.chat.completions.create(**params)
                return response.choices[0].message.content or ""
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP错误 (尝试 {attempt+1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    return f"API请求失败: {str(e)}"
                    
            except Exception as e:
                logger.exception(f"生成文本时发生错误: {str(e)}")
                return f"生成失败: {str(e)}"
    
    def stream_generate(self, messages: List[Dict[str, Any]], callback=None) -> Iterator[str]:
        """流式生成文本，支持回调函数处理每个块"""
        logger.debug(f"开始流式生成文本，消息数: {len(messages)}")
        
        for attempt in range(self.max_retries):
            try:
                api_key = self._get_api_key()
                if not api_key:
                    logger.error("未找到API密钥")
                    yield "错误: 未找到API密钥，请在设置中配置"
                    return
                
                client = OpenAI(
                    api_key=api_key,
                    base_url=global_config.model_config.base_url
                )
                
                params = {
                    'model': global_config.model_config.model,
                    'messages': messages,
                    'temperature': global_config.generation_params.temperature,
                    'frequency_penalty': global_config.generation_params.frequency_penalty,
                    'presence_penalty': global_config.generation_params.presence_penalty,
                    'top_p': global_config.generation_params.top_p,
                    'stream': True,  # 改为True启用真正的流式输出
                    'response_format': global_config.generation_params.response_format
                }
                
                # 设定最大tokens
                params['max_tokens'] = min(
                    global_config.generation_params.max_tokens,
                    self._calculate_max_tokens(messages)
                )
                
                logger.debug(f"使用模型: {params['model']}，流式模式")
                
                # 获取流式响应
                stream = client.chat.completions.create(**params)
                
                # 检查是否是DeepSeek-R1或Qwen-R1模型，这些模型支持思维链
                model_name = global_config.model_config.name
                is_reasoning_model = "DeepSeek-R1" in model_name or "Qwen-R1" in model_name
                
                # 记录已处理内容，防止重复
                last_content = None
                last_reasoning = None
                
                # 处理流式响应
                for chunk in stream:
                    if not hasattr(chunk, 'choices') or not chunk.choices:
                        continue
                    
                    # 尝试提取思维链内容（仅支持思维链的模型）
                    if is_reasoning_model:
                        delta = chunk.choices[0].delta
                        reasoning = getattr(delta, 'reasoning_content', None)
                        
                        # 防止重复发送相同的思维链内容
                        if reasoning and reasoning != last_reasoning:
                            last_reasoning = reasoning
                            if callback:
                                callback({"reasoning_content": reasoning})
                            continue  # 思维链内容仅通过回调传递，不作为返回值
                    
                    # 提取内容增量
                    content_delta = chunk.choices[0].delta.content
                    
                    # 确保不是空内容且不重复
                    if content_delta and content_delta != last_content:
                        last_content = content_delta
                        if callback:
                            callback(content_delta)
                        yield content_delta
                
                return
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP错误 (尝试 {attempt+1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    yield f"API请求失败: {str(e)}"
                    
            except Exception as e:
                logger.exception(f"流式生成文本时发生错误: {str(e)}")
                yield f"生成失败: {str(e)}"
    
    def _build_params(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建API请求参数"""
        params = {
            "model": global_config.model_config.model,
            "messages": messages,
            "temperature": global_config.generation_params.temperature,
            "top_p": global_config.generation_params.top_p,
            "max_tokens": self._calculate_max_tokens(messages),
            "frequency_penalty": global_config.generation_params.frequency_penalty,
            "presence_penalty": global_config.generation_params.presence_penalty,
        }
        
        # 添加响应格式（如果配置了）
        if hasattr(global_config.generation_params, 'response_format'):
            params["response_format"] = global_config.generation_params.response_format
            
        return params
    
    def _calculate_max_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """计算最大令牌数，确保不超过模型上下文窗口"""
        # 简单估算已用token
        used_tokens = sum(len(m.get("content", "")) // 4 for m in messages)
        
        # 确保不超过模型上下文窗口的80%
        max_context = global_config.model_config.context_window
        available = max(max_context - used_tokens, 0)
        
        # 取配置值和可用值的较小值
        return min(global_config.generation_params.max_tokens, int(available * 0.8))
    
    def check_connection(self) -> bool:
        """检查与API的连接状态"""
        try:
            client = httpx.Client(timeout=5)
            response = client.get(f"{global_config.model_config.base_url}/models")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API连接检查失败: {str(e)}")
            return False

# 单例实例
api_client = DeepSeekAPIClient() 