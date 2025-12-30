#!/usr/bin/env python3
"""
Прогресс-индикатор для сжатия
"""

import sys
from typing import Callable, Optional


class CompressionProgressCallback:
    """Callback для прогресса сжатия"""
    
    @staticmethod
    def create_callback() -> Callable:
        """Создает callback функцию для сжатия"""
        
        def callback(progress: float, current: int, total: int, remaining_time: Optional[float] = None):
            """Callback для отображения прогресса сжатия"""
            bar_length = 50
            filled_length = int(bar_length * progress / 100)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            
            # Используем терминальные последовательности для очистки строки
            sys.stdout.write('\r' + ' ' * 150 + '\r')
            
            if remaining_time is not None:
                if remaining_time > 3600:
                    time_str = f"{remaining_time/3600:.1f} ч"
                elif remaining_time > 60:
                    time_str = f"{remaining_time/60:.1f} мин"
                else:
                    time_str = f"{remaining_time:.0f} сек"
                sys.stdout.write(f"Сжатие: |{bar}| {progress:.1f}% ({current}/{total} блоков) Осталось: {time_str}")
            else:
                sys.stdout.write(f"Сжатие: |{bar}| {progress:.1f}% ({current}/{total} блоков)")
            sys.stdout.flush()
            
            if progress >= 100:
                print()
        
        return callback
