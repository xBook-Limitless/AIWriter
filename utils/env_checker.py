import sys
import os

def is_venv():
    """判断是否在虚拟环境中"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.prefix != sys.base_prefix)

def check_dependencies():
    missing = []
    if missing:
        print(f"缺失关键依赖: {', '.join(missing)}")
        return False
    return True

def check_environment():
    """综合环境检查"""
    if not is_venv():
        print("⚠️ 未检测到虚拟环境，建议执行：")
        print(r"  .\.venv\Scripts\Activate.ps1  # Windows PowerShell")
        print("  source .venv/bin/activate     # Linux/macOS")
        return False
    return True 