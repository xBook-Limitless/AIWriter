import yaml
import os
from pathlib import Path
import json
from typing import Dict, Any, Optional

CONFIG_PATH = Path(__file__).parent.parent / 'data/configs'

def ensure_config_dir():
    """确保配置目录存在"""
    CONFIG_PATH.mkdir(parents=True, exist_ok=True)

def load_config(file_path: str) -> Dict[str, Any]:
    """
    加载配置文件
    
    参数:
        file_path: 相对于configs目录的配置文件路径
    
    返回:
        配置字典，加载失败则返回空字典
    """
    ensure_config_dir()
    config_file = CONFIG_PATH / file_path
    
    try:
        if not config_file.exists():
            print(f"配置文件不存在: {file_path}，将使用默认配置")
            create_default_config(file_path)
            
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"配置加载失败 ({file_path}): {str(e)}")
        return {}

def create_default_config(file_path: str) -> bool:
    """
    创建默认配置文件
    
    参数:
        file_path: 配置文件名
        
    返回:
        是否成功创建默认配置
    """
    default_configs = {
        'model_config.yaml': {
            'models': {
                'DeepSeek-R1': {
                    'provider': 'DeepSeek',
                    'base_url': 'https://api.deepseek.com/v1',
                    'model': 'deepseek-chat',
                    'context_window': 128000
                }
            }
        },
        'user_config.yaml': {
            'selected_model': 'DeepSeek-R1',
            'ui': {
                'theme': 'default',
                'font_size': 12
            }
        },
        'apikey.yaml': {
            'providers': {
                'DeepSeek': '',
                'Qwen': ''
            }
        }
    }
    
    if file_path not in default_configs:
        print(f"没有 {file_path} 的默认配置模板")
        return False
    
    try:
        save_config(file_path, default_configs[file_path])
        return True
    except Exception as e:
        print(f"创建默认配置失败: {str(e)}")
        return False

# 添加版本配置加载
def get_version_info() -> Dict[str, str]:
    """获取应用程序版本信息"""
    version_file = Path(__file__).parent.parent / 'version.json'
    
    if not version_file.exists():
        # 默认版本信息
        return {
            "version": "1.0.0",
            "build_date": "2024-02-25",
            "build_type": "development"
        }
    
    try:
        with open(version_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {
            "version": "unknown",
            "build_date": "unknown",
            "build_type": "unknown"
        }

def load_configurations(*args, **kwargs):
    pass

def get_config_path(file_name: str) -> Path:
    """获取配置文件完整路径"""
    ensure_config_dir()
    return CONFIG_PATH / file_name

def save_config(file_name: str, config: dict) -> bool:
    """
    保存配置到文件
    
    参数:
        file_name: 配置文件名
        config: 要保存的配置字典
        
    返回:
        是否成功保存
    """
    ensure_config_dir()
    config_path = get_config_path(file_name)
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config, f, allow_unicode=True)
        return True
    except Exception as e:
        print(f"保存配置文件 {file_name} 失败: {str(e)}")
        return False

def get_api_key() -> Dict[str, Dict[str, str]]:
    """获取API密钥配置"""
    try:
        config_path = get_config_path('apikey.yaml')
        if not config_path.exists():
            # 创建默认API密钥配置
            create_default_config('apikey.yaml')
            
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            # 确保providers结构存在
            data.setdefault("providers", {"DeepSeek": "", "Qwen": ""})
            return data
    except FileNotFoundError:
        default_config = {"providers": {"DeepSeek": "", "Qwen": ""}}
        save_config('apikey.yaml', default_config)
        return default_config

def save_api_key(data: dict) -> bool:
    """保存API密钥配置"""
    return save_config('apikey.yaml', data)

def validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    验证配置是否符合预期结构
    
    参数:
        config: 待验证的配置
        schema: 配置结构定义
        
    返回:
        配置是否有效
    """
    # 简单实现，仅检查关键字段是否存在
    for key, value in schema.items():
        if key not in config:
            return False
        
        if isinstance(value, dict) and key in config:
            if not isinstance(config[key], dict):
                return False
            if not validate_config(config[key], value):
                return False
    
    return True 