import logging
from logging.handlers import RotatingFileHandler

# 创建日志记录器
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 创建控制台处理程序并设置级别为INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建文件处理程序并设置级别为INFO
log_file = "QEpuber.log"
file_handler = RotatingFileHandler(
    log_file, maxBytes=5 * 1024, backupCount=0, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# 创建格式化器并将其添加到处理程序
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 将处理程序添加到日志记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)
