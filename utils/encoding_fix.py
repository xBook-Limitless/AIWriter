"""
编码修复工具 - 用于检测和修复Windows系统上的编码问题
主要针对中文环境下的编码不一致问题
"""

import sys
import os
import locale
import logging
from pathlib import Path

def check_encoding():
    """
    检查当前系统的编码设置
    返回包含编码信息的字典
    """
    encoding_info = {
        "sys.stdout.encoding": getattr(sys.stdout, "encoding", "未知"),
        "sys.stderr.encoding": getattr(sys.stderr, "encoding", "未知"),
        "sys.stdin.encoding": getattr(sys.stdin, "encoding", "未知"),
        "sys.getdefaultencoding()": sys.getdefaultencoding(),
        "locale.getpreferredencoding()": locale.getpreferredencoding(),
        "file system encoding": sys.getfilesystemencoding(),
    }
    
    # 检查是否Windows系统
    if sys.platform.startswith('win'):
        try:
            # 获取Windows控制台代码页
            import subprocess
            cp_result = subprocess.run(
                ["chcp"], 
                shell=True, 
                capture_output=True, 
                text=True
            )
            encoding_info["windows_codepage"] = cp_result.stdout.strip()
        except Exception as e:
            encoding_info["windows_codepage"] = f"获取失败: {str(e)}"
            
        # 检查是否处于UTF-8模式
        if hasattr(sys, 'get_windows_console_utf8_mode'):
            try:
                encoding_info["windows_utf8_mode"] = sys.get_windows_console_utf8_mode()
            except Exception:
                encoding_info["windows_utf8_mode"] = "获取失败"
    
    return encoding_info

def fix_encoding():
    """
    尝试修复编码问题，主要针对Windows系统
    """
    if not sys.platform.startswith('win'):
        print("非Windows系统，无需修复编码")
        return True
        
    # 检查当前编码
    encoding_info = check_encoding()
    preferred_encoding = encoding_info.get("locale.getpreferredencoding()")
    
    # 如果已经是UTF-8，则无需修复
    if preferred_encoding.lower() == 'utf-8':
        print("当前系统已使用UTF-8编码，无需修复")
        return True
    
    try:
        # 尝试设置UTF-8模式
        if hasattr(sys, 'set_windows_console_utf8_mode'):
            sys.set_windows_console_utf8_mode(True)
            print("已启用Windows控制台UTF-8模式")
        
        # 尝试设置控制台代码页
        import subprocess
        subprocess.run(["chcp", "65001"], shell=True)
        print("已设置控制台代码页为65001 (UTF-8)")
        
        # 验证设置是否生效
        new_encoding_info = check_encoding()
        if new_encoding_info.get("windows_codepage", "").find("65001") != -1:
            print("编码设置成功!")
            return True
        else:
            print("警告: 编码设置可能未生效")
            return False
            
    except Exception as e:
        print(f"修复编码时出错: {str(e)}")
        return False

def create_encoding_test_file():
    """
    创建一个测试文件，写入中文内容
    用于测试文件编码设置是否正确
    """
    test_file = Path(__file__).parent.parent / "logs" / "encoding_test.txt"
    
    try:
        # 使用不同的编码方式写入文件
        encodings = ['utf-8', 'gb2312', 'gbk', 'cp936']
        
        for encoding in encodings:
            output_file = test_file.with_name(f"encoding_test_{encoding}.txt")
            with open(output_file, 'w', encoding=encoding) as f:
                f.write(f"这是使用 {encoding} 编码写入的中文内容\n")
                f.write("测试字符: 你好，世界！中国 123\n")
                f.write(f"当前系统编码: {locale.getpreferredencoding()}\n")
            
            print(f"已创建测试文件: {output_file}")
            
        return True
    except Exception as e:
        print(f"创建编码测试文件时出错: {str(e)}")
        return False

def configure_logger_encoding():
    """
    配置Python logging模块使用正确的编码
    """
    # 获取系统日志目录
    log_dir = Path(__file__).parent.parent / "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建一个专门用于编码测试的日志记录器
    logger = logging.getLogger("encoding_test")
    
    # 清除现有处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建日志文件处理器，使用UTF-8编码
    handler = logging.FileHandler(
        str(log_dir / "encoding_test.log"), 
        encoding='utf-8'
    )
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    # 记录编码信息和测试中文
    encoding_info = check_encoding()
    logger.info("=== 编码测试开始 ===")
    for key, value in encoding_info.items():
        logger.info(f"{key}: {value}")
    
    logger.info("中文测试: 你好，世界！")
    logger.info("特殊字符: ♥★☆※∮◎")
    logger.info("=== 编码测试结束 ===")
    
    return logger

if __name__ == "__main__":
    print("=== 系统编码检查 ===")
    encoding_info = check_encoding()
    for key, value in encoding_info.items():
        print(f"{key}: {value}")
    
    print("\n=== 尝试修复编码 ===")
    fix_encoding()
    
    print("\n=== 创建编码测试文件 ===")
    create_encoding_test_file()
    
    print("\n=== 配置日志编码 ===")
    configure_logger_encoding()
    
    print("\n编码检查和修复完成!") 