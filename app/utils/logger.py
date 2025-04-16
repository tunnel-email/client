import logging
import os
from datetime import datetime
import sys
import ctypes
from app.utils.api import script_path


# создание директории с логами
log_dir = script_path('.logs')

if not os.path.exists(log_dir):
    os.mkdir(log_dir)

    if sys.platform == "win32":
        # making the folder hidden in windows
        ctypes.windll.kernel32.SetFileAttributesW(log_dir, 0x02)

# имя файла с текущей датой
log_file = os.path.join(log_dir, f'mailtunnel_{datetime.now().strftime("%Y-%m-%d")}.log')

def setup_logger(name):
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to setup file handler: {e}")
    
    # вывод в консоль info
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
