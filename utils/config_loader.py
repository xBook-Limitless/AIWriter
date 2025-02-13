import yaml
from pathlib import Path

project_root = Path(__file__).absolute().parent.parent.parent
CONFIG_PATH = project_root / 'data/configs'

print(f"项目根目录: {Path(__file__).parent.parent.parent}")
print(f"最终配置路径: {CONFIG_PATH}")

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
        print(f"[Debug] 配置文件路径: {config_path}")  # 新增路径显示
        print(f"[Debug] 文件是否存在: {config_path.exists()}")  # 检查文件存在性
        
        with open(config_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()  # 读取原始内容
            print(f"[Debug] 文件原始内容:\n{raw_content}")
            
            config = yaml.safe_load(raw_content)
            print(f"[Debug] 解析后内容: {config}")
            
            # return "0.0.1"  # 强制返回测试值 ← 注释这行
            return config.get('version', '0.0.0')  # 取消注释这行
    except Exception as e:
        print(f"[ERROR] 配置加载异常: {str(e)}")
        return '0.0.0'

def load_configurations(*args, **kwargs):
    pass 