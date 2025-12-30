#!/usr/bin/env python3
"""
Прогресс-индикаторы для Pi-Archiver Ultra
Реализует callback функции для отображения прогресса генерации π, сжатия и извлечения
"""

import sys
import time
from typing import Optional, Callable


class PiProgressCallback:
    """Callback для прогресса генерации π"""
    
    def __init__(self):
        self.start_time = None
        self.progress_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def create_callback(self, start_time: float) -> Callable:
        """Создает callback функцию для генерации π"""
        self.start_time = start_time
        
        def callback(progress_percent: float, current_iter: int, total_iters: int):
            """Callback для реального прогресса генерации"""
            # Расчет оставшегося времени
            elapsed = time.time() - self.start_time
            if progress_percent > 0 and progress_percent < 99.9:
                estimated_total = elapsed / (progress_percent / 100)
                remaining = estimated_total - elapsed
                if remaining > 0:
                    minutes = int(remaining // 60)
                    seconds = int(remaining % 60)
                    time_str = f" (осталось ~{minutes}:{seconds:02d})"
                else:
                    time_str = " (почти завершено)"
            elif progress_percent >= 99.9:
                time_str = " (почти завершено)"
            else:
                time_str = ""
            
            # Вывод прогресса с очисткой строки
            char_idx = int(progress_percent) % len(self.progress_chars)
            sys.stdout.write('\r' + ' ' * 150 + '\r')  # Очистка строки
            sys.stdout.write(f"{self.progress_chars[char_idx]} Генерация π: {progress_percent:6.2f}% [{current_iter:,}/{total_iters:,}]{time_str}")
            sys.stdout.flush()
        
        return callback


class CompressionProgressCallback:
    """Callback для прогресса сжатия"""
    
    def __init__(self):
        self.progress_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.last_update = 0
        self.char_index = 0
    
    def create_callback(self) -> Callable:
        """Создает callback функцию для сжатия"""
        
        def callback(progress: float, current: int, total: int, remaining_time: Optional[float] = None):
            """Callback для отображения прогресса сжатия"""
            self.char_index = (self.char_index + 1) % len(self.progress_chars)
            char = self.progress_chars[self.char_index]
            
            bar_length = 30
            filled_length = int(bar_length * progress / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # Форматирование времени
            time_str = ""
            if remaining_time is not None:
                if remaining_time > 3600:
                    time_str = f" | Осталось: {remaining_time/3600:.1f} ч"
                elif remaining_time > 60:
                    time_str = f" | Осталось: {remaining_time/60:.1f} мин"
                else:
                    time_str = f" | Осталось: {remaining_time:.0f} сек"
            
            # Формируем строку прогресса
            progress_str = (f"{char} Сжатие: |{bar}| {progress:6.2f}% "
                          f"[{current:>6}/{total:<6} блоков]{time_str}")
            
            # Выводим с очисткой строки
            sys.stdout.write('\r' + ' ' * 150 + '\r')
            sys.stdout.write(progress_str[:150])  # Ограничиваем длину на всякий случай
            sys.stdout.flush()
            
            if progress >= 100:
                print()  # Переход на новую строку при завершении
        
        return callback


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
        
        # Вычисляем прогресс
        current_file_progress = (file_blocks_processed / file_blocks_total) * 100 if file_blocks_total > 0 else 0
        completed_files = self.processed_files - 1 if self.processed_files > 0 else 0
        
        # Формируем строку прогресса
        progress_str = (f"\rИзвлечение: {current_file_progress:6.2f}% | "
                      f"Файл {self.processed_files}/{self.total_files} | "
                      f"Блоки: {file_blocks_processed}/{file_blocks_total}")
        
        # Выводим с очисткой строки
        sys.stdout.write('\r' + ' ' * 150 + '\r')
        sys.stdout.write(progress_str[:150])
        sys.stdout.flush()
        
        # Выводим прогресс только в конце файла
        if file_blocks_processed == file_blocks_total:
            self.processed_files += 1
            print()  # Переход на новую строку при завершении файла
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
