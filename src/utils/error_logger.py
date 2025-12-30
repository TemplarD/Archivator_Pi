#!/usr/bin/env python3
"""
Логирование ошибок Pi-Archiver Ultra
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

class PiArchiverLogger:
    """Специализированный логгер для Pi-Archiver"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Создаем логгер
        self.logger = logging.getLogger("PiArchiver")
        self.logger.setLevel(logging.DEBUG)
        
        # Формат логов
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Файл лога ошибок
        error_handler = logging.FileHandler(
            self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # Файл общего лога
        debug_handler = logging.FileHandler(
            self.log_dir / f"debug_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        
        # Консольный вывод
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Добавляем обработчики
        self.logger.addHandler(error_handler)
        self.logger.addHandler(debug_handler)
        self.logger.addHandler(console_handler)
    
    def error(self, message: str, exception: Exception = None):
        """Логирует ошибку"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(message)
    
    def info(self, message: str):
        """Логирует информационное сообщение"""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Логирует отладочное сообщение"""
        self.logger.debug(message)
    
    def compression_error(self, file_path: str, error: Exception):
        """Логирует ошибку сжатия"""
        self.error(f"Ошибка сжатия файла {file_path}", error)
    
    def extraction_error(self, archive_name: str, error: Exception):
        """Логирует ошибку извлечения"""
        self.error(f"Ошибка извлечения архива {archive_name}", error)
    
    def pi_generation_error(self, precision: int, error: Exception):
        """Логирует ошибку генерации π"""
        self.error(f"Ошибка генерации π с точностью {precision}", error)

# Глобальный логгер
archiver_logger = PiArchiverLogger()
