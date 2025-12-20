#!/usr/bin/env python3
"""
Тестовый скрипт для проверки прогресс-индикатора сжатия
"""

import sys
import os
from pathlib import Path

# Добавляем пути к модулям
sys.path.append(str(Path(__file__).parent / "src"))

# Импортируем напрямую
from src.compression.compression_core import CompressionCore
from src.pi_generator.pi_generator import PiGenerator

def test_compression_progress():
    """Тест прогресс-индикатора сжатия"""
    
    # Создаем генератор π
    pi_generator = PiGenerator()
    
    # Создаем ядро сжатия
    compression_core = CompressionCore(pi_generator)
    
    # Генерируем небольшое количество π цифр для теста
    print("Генерация π для теста...")
    pi_digits = pi_generator.generate_pi_digits(10000, use_gpu=False)
    
    # Создаем тестовые данные
    test_data = b"Test data for compression. " * 1000
    
    # Функция для отображения прогресса
    def compression_progress_callback(progress, current, total, remaining_time=None):
        bar_length = 50
        filled_length = int(bar_length * progress / 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        if remaining_time is not None:
            if remaining_time > 3600:
                time_str = f"{remaining_time/3600:.1f} ч"
            elif remaining_time > 60:
                time_str = f"{remaining_time/60:.1f} мин"
            else:
                time_str = f"{remaining_time:.0f} сек"
            print(f"\rСжатие: |{bar}| {progress:.1f}% ({current}/{total} блоков) Осталось: {time_str}", end="")
        else:
            print(f"\rСжатие: |{bar}| {progress:.1f}% ({current}/{total} блоков)", end="")
        
        if progress >= 100:
            print()
    
    print("Начинаем сжатие...")
    blocks, stats = compression_core.compress_data(
        test_data, 
        pi_digits,
        progress_callback=compression_progress_callback
    )
    
    print(f"Сжатие завершено!")
    print(f"Блоков найдено: {len(blocks)}")
    print(f"Степень сжатия: {stats.compression_ratio:.2f}")

if __name__ == "__main__":
    test_compression_progress()
