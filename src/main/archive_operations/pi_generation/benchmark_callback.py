#!/usr/bin/env python3
"""
Специальный callback для бенчмарка с чистым выводом
"""

import sys
import time
from typing import Callable


class BenchmarkCallback:
    """Callback для бенчмарка с чистым выводом в одной строке"""
    
    def __init__(self, workers: int):
        self.workers = workers
        self.start_time = None
        self.progress_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def create_callback(self) -> Callable:
        """Создает callback функцию для бенчмарка"""
        self.start_time = time.time()
        
        def callback(progress_percent: float, current_iter: int, total_iters: int):
            """Callback для бенчмарка с полной информацией в одной строке"""
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
            
            # Формируем полную информацию в одной строке
            char_idx = int(progress_percent) % len(self.progress_chars)
            progress_line = (f"{self.progress_chars[char_idx]} {progress_percent:.1f}% "
                           f"[{current_iter:,}/{total_iters:,}] {rate:.0f} итер/сек "
                           f"| Потоков: {self.workers} | {eta_str}")
            
            # Полностью очищаем строку и выводим новую информацию
            sys.stdout.write('\r' + ' ' * 120 + '\r')  # Сначала очищаем
            sys.stdout.write(progress_line)  # Затем выводим
            sys.stdout.flush()
            
            # Переход на новую строку при завершении
            if progress_percent >= 100:
                print()
        
        return callback
