import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / 'data/configs'

def load_config(file_path):
    try:
        with open(f'data/configs/{file_path}') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"配置加载失败: {str(e)}")
        return {}

# 添加版本配置加载
def get_version_info():
    """示例实现，返回版本信息"""
    return {
        "version": "1.0.0",
        "build_date": "2024-01-01"
    }

def load_configurations(*args, **kwargs):
    pass

def get_config_path(file_name: str) -> Path:
    """获取配置文件完整路径"""
    return CONFIG_PATH / file_name 

def save_config(file_name: str, config: dict):
    """保存配置到文件"""
    config_path = get_config_path(file_name)
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config, f, allow_unicode=True)
    except Exception as e:
        print(f"保存配置文件 {file_name} 失败: {str(e)}") 

def get_api_key():
    """获取API密钥配置"""
    try:
        config_path = Path(__file__).parent.parent / 'data/configs/apikey.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}

def save_api_key(data: dict):
    """保存API密钥配置"""
    config_path = Path(__file__).parent.parent / 'data/configs/apikey.yaml'
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, allow_unicode=True) 