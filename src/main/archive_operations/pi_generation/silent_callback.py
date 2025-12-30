#!/usr/bin/env python3
"""
Тихий callback для бенчмарка - не выводит ничего лишнего
"""

import sys
import time
from typing import Callable


class SilentCallback:
    """Тихий callback для бенчмарка"""
    
    def __init__(self, workers: int):
        self.workers = workers
        self.start_time = None
        self.last_update = 0
    
    def create_callback(self) -> Callable:
        """Создает callback функцию для бенчмарка"""
        self.start_time = time.time()
        
        def callback(progress_percent: float, current_iter: int, total_iters: int):
            """Тихий callback - обновляется только каждые 10%"""
            # Обновляем только каждые 10% чтобы не ломать вывод
            if int(progress_percent) % 10 == 0 and int(progress_percent) != self.last_update:
                self.last_update = int(progress_percent)
                
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
                
                # Простая строка прогресса
                progress_line = f"{progress_percent:.0f}% [{rate:.0f} итер/сек] | {self.workers} потоков | {eta_str}"
                
                # Очищаем строку и выводим
                sys.stdout.write('\r' + progress_line.ljust(80))
                sys.stdout.flush()
            
            # Переход на новую строку при завершении
            if progress_percent >= 100:
                print()
        
        return callback
