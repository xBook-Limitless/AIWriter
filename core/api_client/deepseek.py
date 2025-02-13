from openai import OpenAI
from typing import List, Dict
from core.api_client.retry import exponential_backoff_retry
from modules.GlobalModule import global_api_config

class DeepSeekAPIClient:
    def __init__(self):
        global_api_config.validate()  # 先验证配置
        self._init_client()
    
    def _init_client(self):
        """初始化DeepSeek客户端"""
        self.client = OpenAI(
            api_key=global_api_config.credential.api_key,
            base_url=global_api_config.provider.base_url,
            default_headers={
                "Authorization": f"Bearer {global_api_config.credential.api_key}"
            }
        )

    def generate(self, user_input: str) -> str:
        """生成文本"""
        params = {
            'model': global_api_config.model.base_model,
            'messages': [{"role": "user", "content": user_input}],
            'temperature': global_api_config.parameters.temperature,
            'max_tokens': global_api_config.parameters.max_tokens,
            'top_p': global_api_config.parameters.top_p,
            'frequency_penalty': global_api_config.parameters.frequency_penalty,
            'presence_penalty': global_api_config.parameters.presence_penalty,
            'response_format': global_api_config.parameters.response_format,
            'stop': global_api_config.advanced.stop,
            'stream': global_api_config.advanced.stream,
            'stream_options': global_api_config.advanced.stream_options,
            'logprobs': global_api_config.advanced.logprobs,
            'top_logprobs': global_api_config.advanced.top_logprobs,
            'tools': global_api_config.advanced.tools,
            'tool_choice': global_api_config.advanced.tool_choice
        }

        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content

    def stream_generate(self, user_input: str):
        """流式生成"""
        params = {
            'model': global_api_config.model.base_model,
            'messages': [{"role": "user", "content": user_input}],
            'temperature': global_api_config.parameters.temperature,
            'max_tokens': global_api_config.parameters.max_tokens,
            'top_p': global_api_config.parameters.top_p,
            'stream': True,
            'stream_options': global_api_config.advanced.stream_options,
            'logprobs': global_api_config.advanced.logprobs,
            'top_logprobs': global_api_config.advanced.top_logprobs
        }
        return self.client.chat.completions.create(**params)

# 单例实例
api_client = DeepSeekAPIClient() 