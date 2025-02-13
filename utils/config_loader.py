import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / 'data/configs'

def load_config(config_name):
    """通用配置加载方法"""
    try:
        with open(CONFIG_PATH / config_name) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}  # 返回空字典避免报错

# 添加版本配置加载
def get_version_info():
    try:
        config_path = CONFIG_PATH / 'version.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get('version', '0.0.0')
    except Exception as e:
        print(f"Error loading version: {e}")
        return '0.0.0'

def load_configurations(*args, **kwargs):
    pass 