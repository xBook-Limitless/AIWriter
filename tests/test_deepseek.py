import unittest
from unittest.mock import patch, MagicMock
from modules.GlobalModule import global_api_config
from core.api_client.deepseek import DeepSeekAPIClient

class TestDeepSeekClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """测试环境初始化"""
        # 使用生产环境默认配置
        cls.api_client = DeepSeekAPIClient()
        
        # 覆盖部分测试参数
        global_api_config.parameters.max_tokens = 256
        global_api_config.advanced.stop = ["\n"]

    @patch('core.api_client.deepseek.OpenAI')
    def test_basic_generation(self, mock_openai):
        """测试完整参数传递"""
        # 修复mock配置
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "TEST_OK"  # 确保响应结构完整
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        # 需要重新初始化客户端以应用mock
        self.api_client._init_client()  # 新增初始化
        
        result = self.api_client.generate("测试输入")
        self.assertEqual(result, "TEST_OK")
        
        # 验证核心参数
        called_args = mock_openai.return_value.chat.completions.create.call_args[1]
        self.assertEqual(called_args['model'], "deepseek-chat")
        self.assertEqual(called_args['temperature'], 1.0)
        self.assertEqual(called_args['response_format'], {"type": "text"})
        self.assertEqual(called_args['stop'], ["\n"])

    @patch('core.api_client.deepseek.OpenAI')
    def test_stream_generation(self, mock_openai):
        """测试流式参数结构"""
        # 修复流式mock结构
        mock_openai.return_value.chat.completions.create.return_value = iter([
            MagicMock(choices=[MagicMock(delta=MagicMock(content="STREAM_"))])
        ])
        
        # 需要重新初始化客户端以应用mock
        self.api_client._init_client()  # 新增初始化
        
        stream = self.api_client.stream_generate("流式输入")
        self.assertTrue(any("STREAM_" in chunk.choices[0].delta.content for chunk in stream))
        
        # 确保方法被调用后再获取参数
        mock_openai.return_value.chat.completions.create.assert_called_once()
        called_args = mock_openai.return_value.chat.completions.create.call_args.kwargs
        
        self.assertTrue(called_args['stream'])

if __name__ == '__main__':
    unittest.main() 