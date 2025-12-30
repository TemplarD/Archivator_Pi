#!/usr/bin/env python3
"""
Операции генерации π для Pi-Archiver Ultra
"""

import time
import multiprocessing as mp
from pathlib import Path
from typing import Optional

# Абсолютные импорты
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from progress_indicators.pi_progress.pi_generator_callback import PiProgressCallback
from pi_generator.pi_generator import PiGenerator


class PiGeneratorOperations:
    """Класс для операций генерации π"""
    
    def __init__(self, pi_generator: PiGenerator):
        self.pi_generator = pi_generator
    
    def generate_pi_for_compression(self, pi_precision: int, use_gpu: bool = False, 
                                   num_workers: Optional[int] = None, 
                                   force_regenerate: bool = False) -> str:
        """
        Генерирует π для сжатия с прогресс-индикатором
        
        Args:
            pi_precision: количество цифр π
            use_gpu: использовать GPU
            num_workers: количество потоков
            force_regenerate: принудительно перегенерировать
            
        Returns:
            строка с цифрами π
        """
        print("🔄 Генерация цифр π...")
        
        # Определяем количество потоков для генерации π
        if num_workers is None:
            num_workers = min(mp.cpu_count(), 8)  # Ограничиваем до 8 потоков
        print(f"Используем {num_workers} потоков для генерации π")
        
        # Создаем callback для прогресса
        progress_callback = PiProgressCallback()
        start_time = time.time()
        callback = progress_callback.create_callback(start_time)
        
        # Генерируем π
        pi_digits = self.pi_generator.generate_pi_digits(
            pi_precision, use_gpu, callback, num_workers, force_regenerate
        )
        
        generation_time = time.time() - start_time
        print(f"✅ Генерация завершена! [{len(pi_digits):,} цифр за {generation_time:.2f} сек] {' ' * 30}")
        
        return pi_digits
