#!/usr/bin/env python3
"""
Чистый callback который не ломает вывод
"""

import sys
import time
from typing import Callable


class CleanCallback:
    """Чистый callback для бенчмарка"""
    
    def __init__(self, workers: int):
        self.workers = workers
        self.start_time = None
        self.last_progress = -1
        self.progress_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def create_callback(self) -> Callable:
        """Создает callback функцию"""
        self.start_time = time.time()
        
        def callback(progress_percent: float, current_iter: int, total_iters: int):
            # Обновляем только если прогресс изменился значительно
            if int(progress_percent) == self.last_progress:
                return
            
            self.last_progress = int(progress_percent)
            
            # Расчет времени и скорости
            elapsed = time.time() - self.start_time
            rate = current_iter / elapsed if elapsed > 0 else 0
            
            # Расчет ETA
            if rate > 0:
                remaining_iters = total_iters - current_iter
                eta = remaining_iters / rate
                eta_str = f"ETA: {eta:.0f}сек"
            else:
                eta_str = "ETA: --"
            
            # Формируем строку
            char_idx = int(progress_percent) % len(self.progress_chars)
            progress_line = (f"{self.progress_chars[char_idx]} {progress_percent:.1f}% "
                           f"[{current_iter:,}/{total_iters:,}] {rate:.0f} итер/сек "
                           f"| Потоков: {self.workers} | {eta_str}")
            
            # Очищаем всю строку и выводим новую
            sys.stdout.write('\r' + ' ' * 150 + '\r')  # Полная очистка
            sys.stdout.write(progress_line)
            sys.stdout.flush()
            
            # Новая строка при завершении
            if progress_percent >= 100:
                print()
        
        return callback
