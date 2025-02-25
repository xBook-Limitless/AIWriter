#!/usr/bin/env python
# 项目构建和打包脚本
import os
import sys
import shutil
import subprocess
import json
import argparse
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.absolute()

def update_version(version_type='patch'):
    """更新版本号"""
    version_file = PROJECT_ROOT / 'version.json'
    
    if not version_file.exists():
        # 创建默认版本文件
        version_data = {
            "version": "1.0.0",
            "build_date": datetime.now().strftime("%Y-%m-%d"),
            "build_type": "development"
        }
    else:
        # 读取当前版本
        with open(version_file, 'r', encoding='utf-8') as f:
            version_data = json.load(f)
    
    # 解析当前版本
    current_version = version_data['version']
    major, minor, patch = map(int, current_version.split('.'))
    
    # 根据版本类型更新
    if version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    # 更新版本信息
    version_data['version'] = f"{major}.{minor}.{patch}"
    version_data['build_date'] = datetime.now().strftime("%Y-%m-%d")
    
    # 写入版本文件
    with open(version_file, 'w', encoding='utf-8') as f:
        json.dump(version_data, f, indent=4)
    
    return version_data['version']

def clean_build():
    """清理构建文件"""
    dirs_to_clean = [
        PROJECT_ROOT / 'build',
        PROJECT_ROOT / 'dist',
        PROJECT_ROOT / 'aiwriter.egg-info'
    ]
    
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            print(f"清理目录: {dir_path}")
            shutil.rmtree(dir_path)
    
    # 清理所有__pycache__目录
    for pycache_dir in PROJECT_ROOT.glob('**/__pycache__'):
        print(f"清理Python缓存: {pycache_dir}")
        shutil.rmtree(pycache_dir)
    
    # 清理日志文件(可选)
    for log_file in (PROJECT_ROOT / 'logs').glob('*.log'):
        print(f"清理日志文件: {log_file}")
        os.remove(log_file)

def run_tests():
    """运行单元测试"""
    print("运行单元测试...")
    result = subprocess.run([sys.executable, '-m', 'pytest', 'tests', '-v'], 
                           cwd=PROJECT_ROOT)
    
    if result.returncode != 0:
        print("❌ 测试失败，停止构建")
        sys.exit(1)
    
    print("✅ 所有测试通过")

def build_package():
    """构建Python包"""
    print("构建Python包...")
    subprocess.run([sys.executable, 'setup.py', 'sdist', 'bdist_wheel'], 
                  cwd=PROJECT_ROOT, check=True)

def build_executable():
    """构建可执行文件"""
    print("构建可执行文件...")
    try:
        subprocess.run([sys.executable, '-m', 'PyInstaller', 
                      '--name=AiWriter',
                      '--windowed',
                      '--icon=assets/icon.ico',
                      '--add-data=data/configs;data/configs',
                      'main.py'],
                     cwd=PROJECT_ROOT, check=True)
        print("✅ 可执行文件构建成功")
    except Exception as e:
        print(f"❌ 可执行文件构建失败: {str(e)}")
        print("请检查PyInstaller是否已安装 (pip install pyinstaller)")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AiWriter构建工具')
    parser.add_argument('--clean', action='store_true', help='清理构建文件')
    parser.add_argument('--test', action='store_true', help='运行测试')
    parser.add_argument('--build', action='store_true', help='构建Python包')
    parser.add_argument('--exe', action='store_true', help='构建可执行文件')
    parser.add_argument('--all', action='store_true', help='执行所有构建步骤')
    parser.add_argument('--version', choices=['patch', 'minor', 'major'], 
                      default='patch', help='更新版本类型')
    
    args = parser.parse_args()
    
    # 如果没有指定任何操作，则打印帮助
    if not (args.clean or args.test or args.build or args.exe or args.all):
        parser.print_help()
        return
    
    # 更新版本
    new_version = update_version(args.version)
    print(f"版本已更新: {new_version}")
    
    # 执行操作
    if args.clean or args.all:
        clean_build()
    
    if args.test or args.all:
        run_tests()
    
    if args.build or args.all:
        build_package()
    
    if args.exe or args.all:
        build_executable()
    
    print("构建完成!")

if __name__ == "__main__":
    main() 