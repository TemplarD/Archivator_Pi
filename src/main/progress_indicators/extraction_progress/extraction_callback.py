#!/usr/bin/env python3
"""
Прогресс-индикатор для извлечения
"""

import sys
from pathlib import Path
from typing import List, Dict, Any


class ExtractionProgressCallback:
    """Callback для прогресса извлечения"""
    
    def __init__(self, total_files: int, total_blocks: int):
        self.total_files = total_files
        self.total_blocks = total_blocks
        self.processed_files = 0
        self.processed_blocks = 0
    
    def update_file_progress(self, file_blocks_processed: int, file_blocks_total: int):
        """Обновляет прогресс по текущему файлу"""
        self.processed_blocks += 1
        
        # Выводим прогресс только в конце файла
        if file_blocks_processed == file_blocks_total:
            # Общий прогресс - правильный расчет без отрицательных чисел
            current_file_progress = file_blocks_processed / file_blocks_total if file_blocks_total > 0 else 0
            completed_files = self.processed_files - 1 if self.processed_files > 0 else 0
            total_progress = ((completed_files + current_file_progress) / self.total_files) * 100 if self.total_files > 0 else 0
            
            # Объединенный прогресс-бар как в архивации
            bar_length = 50
            total_filled_length = int(bar_length * (completed_files + current_file_progress) / self.total_files) if self.total_files > 0 else 0
            total_bar = '█' * total_filled_length + '-' * (bar_length - total_filled_length)
            
            # Выводим прогресс с терминальными последовательностями как в архивации
            sys.stdout.write('\033[F')  # Перемещаем курсор на строку вверх
            sys.stdout.write('\033[K')  # Очищаем строку до конца
            sys.stdout.write(f"Извлечение: |{total_bar}| {total_progress:.1f}% ({self.processed_files}/{self.total_files} файлов)")
            sys.stdout.flush()
    
    def increment_file(self):
        """Увеличивает счетчик обработанных файлов"""
        self.processed_files += 1
    
    def file_restore_progress(self, written: int, file_size: int):
        """Прогресс восстановления конкретного файла"""
        progress = (written / file_size) * 100 if file_size > 0 else 100
        bar_length = 30
        filled_length = int(bar_length * progress / 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        sys.stdout.write(f"\rВосстановление файла: |{bar}| {progress:.1f}% ({written}/{file_size} байт)")
        sys.stdout.flush()
