import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from pathlib import Path
import locale

def setup_logger(name, log_file, level=logging.INFO, console_level=logging.WARNING, 
                max_size_mb=5, backup_count=5, format_str=None):
    """
    设置日志记录器，支持文件和控制台输出
    
    参数:
        name: 日志记录器名称
        log_file: 日志文件路径
        level: 文件日志级别
        console_level: 控制台日志级别
        max_size_mb: 日志文件最大大小（MB）
        backup_count: 保留的备份文件数量
        format_str: 日志格式字符串
    """
    # 确保日志目录存在
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:  # 只有当目录不为空时才创建
            os.makedirs(log_dir, exist_ok=True)
    
    # 设置日志格式
    if format_str is None:
        format_str = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    formatter = logging.Formatter(format_str)
    
    # 获取日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(min(level, console_level))  # 设置为最低级别
    
    # 清除现有处理器（防止重复添加）
    if logger.handlers:
        logger.handlers.clear()
    
    # 添加文件处理器
    if log_file:
        # 在Windows上，特别是中文环境，确保正确的编码设置
        file_encoding = 'utf-8'
        try:
            if sys.platform.startswith('win'):
                # 尝试获取系统编码
                system_encoding = locale.getpreferredencoding()
                # 如果系统编码不是UTF-8，记录这个信息但仍使用UTF-8
                if system_encoding.lower() != 'utf-8':
                    print(f"系统编码为 {system_encoding}，日志将使用 UTF-8 编码")
        except Exception as e:
            print(f"获取系统编码时出错: {str(e)}，将使用 UTF-8")
            
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=1024*1024*max_size_mb,
            backupCount=backup_count,
            encoding=file_encoding
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
    
    # 添加控制台处理器
    # 检测控制台编码，以确保正确显示
    console_encoding = sys.stdout.encoding if hasattr(sys.stdout, 'encoding') else 'utf-8'
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(console_level)
    logger.addHandler(console_handler)
    
    # 记录编码信息
    if log_file:
        logger.debug(f"日志文件编码: {file_encoding}, 控制台编码: {console_encoding}")
    
    return logger

def setup_app_loggers():
    """设置应用程序所有日志记录器"""
    log_dir = Path(__file__).parent.parent / 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # 应用主日志
    app_logger = setup_logger('app', str(log_dir / 'app.log'), 
                             level=logging.INFO, 
                             console_level=logging.WARNING)
    
    # API调用日志
    api_logger = setup_logger('api', str(log_dir / 'api.log'), 
                             level=logging.DEBUG, 
                             console_level=logging.ERROR)
    
    # 调试日志
    debug_logger = setup_logger('debug', str(log_dir / 'debug.log'), 
                               level=logging.DEBUG, 
                               console_level=logging.ERROR)
    
    # 错误日志
    error_logger = setup_logger('error', str(log_dir / 'error.log'), 
                               level=logging.ERROR, 
                               console_level=logging.ERROR)
    
    # 邮件日志
    email_logger = setup_logger('email', str(log_dir / 'email.log'), 
                               level=logging.INFO, 
                               console_level=logging.ERROR)
    
    return {
        'app': app_logger,
        'api': api_logger,
        'debug': debug_logger,
        'error': error_logger,
        'email': email_logger
    }

# 确保日志目录存在
log_dir = Path(__file__).parent.parent / 'logs'
os.makedirs(log_dir, exist_ok=True)

# 默认邮件日志
email_logger = setup_logger('email', str(log_dir / 'email.log')) 