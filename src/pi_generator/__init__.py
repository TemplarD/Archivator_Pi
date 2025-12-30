#!/usr/bin/env python3
"""
Pi-Archiver Generator Package
Унифицированный доступ ко всем алгоритмам генерации π
"""

# Базовые классы
from .algorithms.chudnovsky.single_thread import BaseChudnovskySingleThread, ChudnovskySingleThread
from .algorithms.chudnovsky.multi_thread import ChudnovskyBinarySplitting, ChudnovskyBlockParallel, BBPParallel, SimpleParallelChudnovsky
from .algorithms.chudnovsky.gpu import BaseChudnovskyGPU, NumpyOptimizedChudnovsky, OpenCLChudnovsky, CudaChudnovsky, GPUChudnovskyGenerator, AMDGPUChudnovskyGenerator
from .algorithms.native import CPiGenerator
from .algorithms.other import BBPPiGenerator

# Временные заглушки для обратной совместимости
class BasePiGenerator(BaseChudnovskySingleThread):
    """Заглушка для обратной совместимости"""
    pass

class BaseParallelGenerator:
    """Заглушка для обратной совместимости"""
    def __init__(self, cache_dir=None): pass
    def get_algorithm_name(self): return "Base Parallel Generator"

class BaseGPUGenerator(BaseChudnovskyGPU):
    """Заглушка для обратной совместимости"""
    pass

# Временные заглушки для других алгоритмов
class BBPSingleThread:
    """Заглушка для BBP"""
    def __init__(self, cache_dir=None): pass
    def compute_pi(self, digits, **kwargs): return ""

class MonteCarloSingleThread:
    """Заглушка для Monte Carlo"""
    def __init__(self, cache_dir=None): pass
    def compute_pi(self, digits, **kwargs): return ""

# Универсальный генератор
from .universal_generator import UniversalPiGenerator, AlgorithmType, PerformanceMode, AlgorithmConfig

# Основной класс для обратной совместимости
from .pi_generator import PiGenerator

# Экспортируем основные классы
__all__ = [
    # Универсальный интерфейс
    'UniversalPiGenerator',
    'AlgorithmType', 
    'PerformanceMode',
    'AlgorithmConfig',
    
    # Базовые классы
    'BasePiGenerator',
    'BaseParallelGenerator', 
    'BaseGPUGenerator',
    
    # Однопоточные алгоритмы
    'ChudnovskySingleThread',
    'BBPSingleThread',
    'MonteCarloSingleThread',
    
    # Многопоточные алгоритмы
    'ChudnovskyBinarySplitting',
    'ChudnovskyBlockParallel', 
    'BBPParallel',
    
    # GPU алгоритмы
    'OpenCLChudnovsky',
    'NumpyOptimizedChudnovsky',
    'CudaChudnovsky',
    
    # Обратная совместимость
    'PiGenerator'
]

# Версия пакета
__version__ = '2.0.0'

# Удобные функции для быстрого доступа
def create_generator(generator_type: str = 'auto', cache_dir: str = 'pi_storage'):
    """
    Создает генератор π указанного типа
    
    Args:
        generator_type: 'auto', 'single', 'multi', 'gpu', 'universal'
        cache_dir: директория для кэша
        
    Returns:
        экземпляр генератора
    """
    if generator_type == 'auto' or generator_type == 'universal':
        return UniversalPiGenerator(cache_dir=cache_dir)
    elif generator_type == 'single':
        return ChudnovskySingleThread(cache_dir=cache_dir)
    elif generator_type == 'multi':
        return ChudnovskyBinarySplitting(cache_dir=cache_dir)
    elif generator_type == 'gpu':
        return NumpyOptimizedChudnovsky()
    else:
        raise ValueError(f"Неизвестный тип генератора: {generator_type}")

def quick_generate_pi(digits: int, mode: str = 'balanced', num_workers: int = None):
    """
    Быстрая генерация π с автоматическим выбором алгоритма
    
    Args:
        digits: количество цифр
        mode: 'fastest', 'balanced', 'precision', 'memory_efficient'
        num_workers: количество потоков (для многопоточных алгоритмов)
        
    Returns:
        строка с цифрами π
    """
    generator = UniversalPiGenerator()
    
    # Конвертируем строку в enum
    mode_map = {
        'fastest': PerformanceMode.FASTEST,
        'balanced': PerformanceMode.BALANCED,
        'precision': PerformanceMode.PRECISION,
        'memory_efficient': PerformanceMode.MEMORY_EFFICIENT
    }
    
    perf_mode = mode_map.get(mode, PerformanceMode.BALANCED)
    
    return generator.generate_pi(digits, mode=perf_mode, num_workers=num_workers)

def benchmark_all(digits: int = 1000):
    """
    Запускает бенчмарк всех доступных алгоритмов
    
    Args:
        digits: количество цифр для теста
        
    Returns:
        словарь с результатами
    """
    generator = UniversalPiGenerator()
    return generator.benchmark_algorithms(digits, iterations=3)

def get_system_info():
    """
    Возвращает информацию о системе и доступных алгоритмах
    
    Returns:
        словарь с информацией
    """
    import multiprocessing as mp
    import platform
    
    generator = UniversalPiGenerator()
    available = generator.get_available_algorithms()
    
    info = {
        'platform': platform.platform(),
        'cpu_count': mp.cpu_count(),
        'python_version': platform.python_version(),
        'available_algorithms': available,
        'cache_dir': generator.cache_dir
    }
    
    # Проверяем GPU
    gpu_info = {}
    
    # NumPy
    try:
        import numpy as np
        gpu_info['numpy'] = np.__version__
    except ImportError:
        gpu_info['numpy'] = 'Not available'
    
    # OpenCL
    try:
        import pyopencl as cl
        platforms = cl.get_platforms()
        gpu_info['opencl'] = {
            'available': True,
            'platforms': len(platforms),
            'devices': sum(len(p.get_devices()) for p in platforms)
        }
    except ImportError:
        gpu_info['opencl'] = 'Not available'
    except Exception as e:
        gpu_info['opencl'] = f'Error: {e}'
    
    # CUDA
    try:
        import cupy as cp
        gpu_info['cuda'] = {
            'available': cp.cuda.is_available(),
            'devices': cp.cuda.runtime.getDeviceCount()
        }
    except ImportError:
        gpu_info['cuda'] = 'Not available'
    except Exception as e:
        gpu_info['cuda'] = f'Error: {e}'
    
    info['gpu'] = gpu_info
    
    return info

# Тестирование при запуске
if __name__ == '__main__':
    print("🧪 Pi-Archiver Generator Package Test")
    print("=" * 50)
    
    # Информация о системе
    print("\n📊 Системная информация:")
    sys_info = get_system_info()
    for key, value in sys_info.items():
        if key == 'gpu':
            print(f"  {key}:")
            for gpu_type, info in value.items():
                print(f"    {gpu_type}: {info}")
        else:
            print(f"  {key}: {value}")
    
    # Тест генерации
    print("\n🔢 Тест генерации π:")
    try:
        pi_digits = quick_generate_pi(100, mode='balanced')
        print(f"  Первые 50 цифр: {pi_digits[:50]}")
        print("  ✅ Генерация успешна")
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
    
    # Бенчмарк
    print("\n🏃 Бенчмарк алгоритмов:")
    try:
        results = benchmark_all(500)
        
        if results:
            print("  Результаты:")
            for algo_name, stats in sorted(results.items(), key=lambda x: x[1].get('avg_time', float('inf'))):
                if stats['avg_time'] != float('inf'):
                    print(f"    {algo_name}: {stats['avg_time']:.3f} сек")
        else:
            print("  Нет доступных алгоритмов")
            
    except Exception as e:
        print(f"  ❌ Ошибка бенчмарка: {e}")
    
    print("\n✅ Тест завершен!")