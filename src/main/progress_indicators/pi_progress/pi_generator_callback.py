#!/usr/bin/env python3
"""
Универсальный прогресс-индикатор для генерации π
"""

import time
import sys
from typing import Callable


class PiProgressCallback:
    """Универсальный callback для прогресса генерации π"""
    
    def __init__(self):
        self.start_time = None
        self.progress_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.last_progress = -1
        self.completed = False  # Флаг завершения
    
    def create_callback(self, start_time: float, extra_info: str = "") -> Callable:
        """Создает универсальную callback функцию"""
        self.start_time = start_time
        
        def callback(progress_percent: float, current_iter: int, total_iters: int):
            """Универсальный callback для генерации π"""
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
            
            # Формируем ОЧЕНЬ КОРОТКУЮ строку прогресса
            char_idx = int(progress_percent) % len(self.progress_chars)
            progress_line = (f"{self.progress_chars[char_idx]} {progress_percent:.0f}% "
                           f"{rate:.0f} итер/сек {eta_str} | {extra_info}")
            
            # ПОЛНАЯ очистка строки и вывод - БЕЗ НОВЫХ СТРОК
            sys.stdout.write('\r' + ' ' * 60 + '\r')  # Еще меньше
            sys.stdout.write(progress_line)
            sys.stdout.flush()
            
            # Новая строку при завершении - ТОЛЬКО ОДИН РАЗ
            if progress_percent >= 100 and not self.completed:
                print()  # Переход на новую строку после прогресс-бара
                self.completed = True  # Больше не выводим
        
        return callback
