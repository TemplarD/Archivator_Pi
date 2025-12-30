#!/usr/bin/env python3
"""
Операции сжатия данных для Pi-Archiver Ultra
"""

from pathlib import Path
from typing import Optional, List, Tuple

# Абсолютные импорты
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from progress_indicators.compression_progress.compression_callback import CompressionProgressCallback
from compression.compression_core import CompressionCore


class DataCompressionOperations:
    """Класс для операций сжатия данных"""
    
    def __init__(self, compression_core: CompressionCore):
        self.compression_core = compression_core
    
    def compress_file_data(self, file_data: bytes, pi_digits: str, 
                          num_workers: Optional[int] = None) -> Tuple[List, any]:
        """
        Сжимает данные файла с прогресс-индикатором
        
        Args:
            file_data: данные файла
            pi_digits: строка с цифрами π
            num_workers: количество потоков
            
        Returns:
            кортеж (blocks, stats, xor_key)
        """
        print("Сжатие данных...")
        
        # Используем параллельность для больших файлов
        use_parallel = len(file_data) > 10240  # > 10KB
        
        # Создаем callback для прогресса сжатия
        compression_callback = CompressionProgressCallback.create_callback()
        
        if use_parallel:
            print(f"Используем параллельное сжатие ({num_workers} потоков)...")
            blocks, stats = self.compression_core.compress_data(
                file_data, pi_digits, progress_callback=compression_callback, 
                num_workers=num_workers
            )
        else:
            blocks, stats = self.compression_core.compress_data(
                file_data, pi_digits, progress_callback=compression_callback
            )
        
        # Получаем реальный XOR ключ из процесса сжатия
        xor_data, real_xor_key = self.compression_core._xor_decorrelate(file_data, pi_digits)
        print(f"Реальный XOR ключ: 0x{real_xor_key:02X}")
        
        return blocks, stats, real_xor_key
