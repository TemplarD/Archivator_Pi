#!/usr/bin/env python3
"""
Рабочий прогресс-бар - точная копия из archiver_main.py
"""

import sys
import time


def create_working_progress_bar(description: str = "Прогресс", length: int = 20) -> callable:
    """
    Создает прогресс-бар который работает точно как в archiver_main.py
    
    Args:
        description: Описание процесса
        length: Длина прогресс-бара
        
    Returns:
        Callback функция
    """
    def callback(progress_percent: float, current: int = 0, total: int = 0):
        """
        Обновляет прогресс-бар в одной строке - ТОЧНО как в archiver_main.py
        """
        filled_length = int(length * progress_percent / 100)
        bar = '█' * filled_length + '░' * (length - filled_length)
        
        # НЕ очищаем строку полностью, только обновляем прогресс - как в archiver_main.py строка 396
        sys.stdout.write(f"\r{description}: |{bar}| {progress_percent:3.0f}%")
        sys.stdout.flush()
        
        if progress_percent >= 100:
            print()  # Новая строка при завершении
    
    return callback


# Тест с правильной частотой обновления
if __name__ == "__main__":
    print("🧪 Тест рабочего прогресс-бара:")
    
    callback = create_working_progress_bar("Тест", length=20)
    
    for i in range(101):
        callback(i, i, 100)
        time.sleep(0.05)  # Реже обновляем как в реальной программе
    
    print("✅ Тест завершен!")
