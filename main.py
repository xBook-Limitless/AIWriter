import sys
import traceback
import locale
from ui.iHome import create_main_window
from utils.env_checker import check_environment
from utils.logger import setup_logger
import os
from pathlib import Path
from utils.encoding_fix import fix_encoding, check_encoding, configure_logger_encoding

def setup_application():
    """应用程序初始化设置"""
    # 修复编码问题
    if sys.platform.startswith('win'):
        try:
            # 检查并修复编码
            fix_encoding()
            # 配置日志编码
            encoding_logger = configure_logger_encoding()
            encoding_logger.info("应用程序启动时进行了编码检查")
        except Exception as e:
            print(f"修复编码时出错: {str(e)}")
    
    # 确保日志目录存在
    log_dir = Path(__file__).parent / 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # 设置日志记录器
    logger = setup_logger('app', str(log_dir / 'app.log'))
    
    # 打印系统信息
    logger.info("=== 系统信息 ===")
    encoding_info = check_encoding()
    logger.info(f"操作系统: {sys.platform}")
    logger.info(f"系统编码: {encoding_info['locale.getpreferredencoding()']}")
    logger.info(f"控制台编码: {encoding_info['sys.stdout.encoding']}")
    logger.info(f"Python版本: {sys.version.split()[0]}")
    
    if 'windows_codepage' in encoding_info:
        logger.info(f"Windows代码页: {encoding_info['windows_codepage']}")
    
    try:
        import tkinter as tk
        logger.info(f"Tkinter版本: {tk.TkVersion}")
    except ImportError:
        logger.error("Tkinter未安装或无法导入")
        return False
    
    return True

def main():
    """主程序入口点"""
    try:
        # 初始化应用程序
        if not setup_application():
            print("应用程序初始化失败，请检查日志")
            return 1
        
        # 环境检查
        if not check_environment():
            return 1
        
        # 创建并运行主窗口
        window = create_main_window()
        if window:
            window.mainloop()
        else:
            print("窗口初始化失败，请检查错误日志")
            return 1
        
        return 0
    except Exception as e:
        # 捕获未处理的异常
        print(f"发生未处理的异常: {str(e)}")
        traceback.print_exc()
        
        # 记录到日志文件
        log_dir = Path(__file__).parent / 'logs'
        crash_logger = setup_logger('crash', str(log_dir / 'crash.log'))
        crash_logger.error(f"严重错误: {str(e)}")
        crash_logger.error(traceback.format_exc())
        
        return 1

if __name__ == "__main__":
    sys.exit(main()) 