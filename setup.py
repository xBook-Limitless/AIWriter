#!/usr/bin/env python
from setuptools import setup, find_packages
import json
from pathlib import Path

# 读取版本信息
def get_version():
    try:
        with open('version.json', 'r', encoding='utf-8') as f:
            version_info = json.load(f)
            return version_info.get('version', '0.0.1')
    except Exception:
        return '0.0.1'

# 读取README作为长描述
def get_long_description():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return "AI写作助手 - 支持小说创作和角色生成"

# 解析依赖列表
def get_requirements():
    requirements = []
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if line and not line.startswith('#'):
                    requirements.append(line)
    except Exception:
        # 基本依赖
        requirements = [
            'httpx>=0.28.0',
            'PyYAML>=6.0.0',
            'cryptography>=44.0.0',
            'tqdm>=4.66.0'
        ]
    return requirements

setup(
    name="aiwriter",
    version=get_version(),
    author="AiWriter Team",
    author_email="your.email@example.com",
    description="AI写作助手 - 支持小说创作和角色生成",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AiWriter",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Processing :: General",
    ],
    python_requires=">=3.8",
    install_requires=get_requirements(),
    entry_points={
        "console_scripts": [
            "aiwriter=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["data/configs/*.yaml", "*.json"],
    },
) 