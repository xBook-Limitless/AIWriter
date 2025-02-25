import sys
import os
import importlib
import pkg_resources

def is_venv():
    """判断是否在虚拟环境中"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.prefix != sys.base_prefix)

def check_dependencies():
    """检查关键依赖是否已安装"""
    required_packages = [
        'tkinter',  # GUI框架
        'httpx',    # HTTP客户端
        'PyYAML',     # 配置文件解析
        'cryptography'  # 安全相关
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'tkinter':
                importlib.import_module(package)
            else:
                pkg_resources.get_distribution(package)
        except (ImportError, pkg_resources.DistributionNotFound):
            missing.append(package)
    
    if missing:
        print(f"缺失关键依赖: {', '.join(missing)}")
        print("请执行: pip install -r requirements.txt")
        return False
    return True

def check_python_version():
    """检查Python版本是否符合要求"""
    required_version = (3, 8)  # 最低要求Python 3.8
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"Python版本不符合要求: 当前{current_version[0]}.{current_version[1]}，需要{required_version[0]}.{required_version[1]}或更高")
        return False
    return True

def check_config_files():
    """检查必要的配置文件是否存在"""
    config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'configs')
    required_configs = ['model_config.yaml']
    
    missing = []
    for config in required_configs:
        if not os.path.exists(os.path.join(config_dir, config)):
            missing.append(config)
    
    if missing:
        print(f"缺失必要配置文件: {', '.join(missing)}")
        return False
    return True

def check_environment():
    """综合环境检查"""
    checks = [
        (check_python_version, "Python版本检查"),
        (is_venv, "虚拟环境检查"),
        (check_dependencies, "依赖检查"),
        (check_config_files, "配置文件检查")
    ]
    
    all_passed = True
    results = []
    
    for check_func, description in checks:
        passed = check_func()
        results.append((description, passed))
        all_passed = all_passed and passed
    
    # 输出总结
    print("\n=== 环境检查结果 ===")
    for description, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{description}: {status}")
    
    if not all_passed:
        print("\n⚠️ 环境检查未通过，请解决上述问题后重试")
        if not is_venv():
            print("\n建议执行虚拟环境激活命令：")
            print(r"  .\.venv\Scripts\Activate.ps1  # Windows PowerShell")
            print("  source .venv/bin/activate     # Linux/macOS")
    
    return all_passed 