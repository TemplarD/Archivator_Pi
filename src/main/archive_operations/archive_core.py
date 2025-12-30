#!/usr/bin/env python3
"""
Основные операции архивации Pi-Archiver Ultra
Реализует сжатие файлов с использованием многопоточности
"""

import time
import multiprocessing as mp
from pathlib import Path
from typing import Optional, List, Tuple

# Абсолютные импорты для избежания проблем с относительными импортами
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from progress_indicators.pi_progress.pi_generator_callback import PiProgressCallback
from progress_indicators.compression_progress.compression_callback import CompressionProgressCallback
from pi_generator.pi_generator import PiGenerator
from compression.compression_core import CompressionCore
from search_engine.pi_search import PiSearchEngine


class ArchiveOperations:
    """Класс для операций архивации"""
    
    def __init__(self, pi_generator: PiGenerator, compression_core: CompressionCore, 
                 search_engine: PiSearchEngine):
        self.pi_generator = pi_generator
        self.compression_core = compression_core
        self.search_engine = search_engine
    
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
    
    def compress_file_data(self, file_data: bytes, pi_digits: str, 
                          num_workers: Optional[int] = None) -> Tuple[List, any]:
        """
        Сжимает данные файла с прогресс-индикатором
        
        Args:
            file_data: данные файла
            pi_digits: строка с цифрами π
            num_workers: количество потоков
            
        Returns:
            кортеж (blocks, stats)
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
    
    def get_optimal_workers(self) -> int:
        """
        Определяет оптимальное количество потоков для системы
        
        Returns:
            оптимальное количество потоков
        """
        try:
            import os
            available_cores = len(os.sched_getaffinity(0))
        except AttributeError:
            available_cores = mp.cpu_count()
        
        # Анализируем архитектуру процессоров
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                
                # Количество физических процессоров
                physical_ids = set()
                for line in cpuinfo.split('\n'):
                    if line.startswith('physical id'):
                        physical_ids.add(line.split(':')[1].strip())
                
                # Количество ядер на процессор
                cores_per_cpu = None
                for line in cpuinfo.split('\n'):
                    if line.startswith('cpu cores'):
                        cores_per_cpu = int(line.split(':')[1].strip())
                        break
                
                physical_processors = len(physical_ids)
                total_physical_cores = len(physical_ids) * (cores_per_cpu or 1)
                
        except Exception:
            # Запасной вариант
            physical_processors = 1
            total_physical_cores = available_cores
        
        # Рекомендации по количеству потоков
        if total_physical_cores >= 20:
            # Для мощных систем (2+ процессора)
            optimal_workers = min(total_physical_cores, 16)
        else:
            # Для обычных систем
            optimal_workers = min(available_cores, 8)
        
        return optimal_workers
    
    def print_system_info(self, num_workers: int = None):
        """
        Выводит информацию о системе и потоках
        
        Args:
            num_workers: используемое количество потоков
        """
        info = self._get_system_info()
        
        print('=== Информация о потоках и процессорах ===')
        print(f'Платформа: {info["platform"]}')
        print(f'Процессор: {info["processor"]}')
        print(f'Физических процессоров: {info["physical_processors"]}')
        print(f'Ядер на процессор: {info["cores_per_processor"]}')
        print(f'Всего физических ядер: {info["total_physical_cores"]}')
        print(f'Логических потоков: {info["cpu_count_logical"]}')
        print(f'Доступно потоков процессу: {info["available_cores"]}')
        
        if num_workers:
            print(f'Будет использоваться потоков: {num_workers}')
            efficiency = (num_workers / info['available_cores']) * 100
            print(f'Эффективность использования: {efficiency:.1f}%')
        
        optimal_workers = self.get_optimal_workers()
        print(f'Рекомендуемое количество потоков: {optimal_workers}')
        print('=' * 55)
    
    def _get_system_info(self) -> dict:
        """Возвращает информацию о системе и потоках"""
        import platform
        
        info = {
            'platform': f'{platform.system()} {platform.release()}',
            'processor': platform.processor(),
            'cpu_count_logical': mp.cpu_count(),
            'available_cores': mp.cpu_count()
        }
        
        # Получаем количество доступных ядер для текущего процесса
        try:
            import os
            info['available_cores'] = len(os.sched_getaffinity(0))
        except AttributeError:
            pass
        
        # Анализируем архитектуру процессоров
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                
                # Количество физических процессоров
                physical_ids = set()
                for line in cpuinfo.split('\n'):
                    if line.startswith('physical id'):
                        physical_ids.add(line.split(':')[1].strip())
                
                # Количество ядер на процессор
                cores_per_cpu = None
                for line in cpuinfo.split('\n'):
                    if line.startswith('cpu cores'):
                        cores_per_cpu = int(line.split(':')[1].strip())
                        break
                
                info['physical_processors'] = len(physical_ids)
                info['cores_per_processor'] = cores_per_cpu
                info['total_physical_cores'] = len(physical_ids) * (cores_per_cpu or 1)
                
        except Exception:
            # Запасной вариант
            info['physical_processors'] = 1
            info['cores_per_processor'] = info['cpu_count_logical']
            info['total_physical_cores'] = info['cpu_count_logical']
        
        return info
