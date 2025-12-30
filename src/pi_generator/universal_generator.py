#!/usr/bin/env python3
"""
Универсальный генератор π с поддержкой всех алгоритмов
Автоматический выбор оптимального алгоритма и конфигурации
"""

import os
import time
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass
from enum import Enum

# Импортируем все алгоритмы
from .algorithms.single_thread import (
    BasePiGenerator, ChudnovskySingleThread, BBPSingleThread, MonteCarloSingleThread
)
from .algorithms.multi_thread import (
    BaseParallelGenerator, ChudnovskyBinarySplitting, 
    ChudnovskyBlockParallel, BBPParallel
)
from .algorithms.gpu_accelerated import (
    BaseGPUGenerator, OpenCLChudnovsky, NumpyOptimizedChudnovsky, CudaChudnovsky
)

class AlgorithmType(Enum):
    """Типы алгоритмов"""
    SINGLE_THREAD = "single_thread"
    MULTI_THREAD = "multi_thread"
    GPU_ACCELERATED = "gpu_accelerated"

class PerformanceMode(Enum):
    """Режимы производительности"""
    FASTEST = "fastest"
    BALANCED = "balanced"
    PRECISION = "precision"
    MEMORY_EFFICIENT = "memory_efficient"

@dataclass
class AlgorithmConfig:
    """Конфигурация алгоритма"""
    algorithm_type: AlgorithmType
    algorithm_class: Union[type, str]
    num_workers: int = 1
    device_id: int = 0
    cache_enabled: bool = True
    cache_dir: Optional[str] = None
    extra_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extra_params is None:
            self.extra_params = {}

class UniversalPiGenerator:
    """
    Универсальный генератор π с автоматическим выбором алгоритма
    """
    
    def __init__(self, cache_dir: str = "pi_storage", auto_detect: bool = True):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Доступные алгоритмы
        self.available_algorithms = self._detect_available_algorithms() if auto_detect else self._get_default_algorithms()
        
        # Текущий алгоритм
        self.current_algorithm = None
        self.current_config = None
        
        # Статистика производительности
        self.performance_stats = {}
    
    def _detect_available_algorithms(self) -> Dict[AlgorithmType, List[AlgorithmConfig]]:
        """Автоматически определяет доступные алгоритмы"""
        algorithms = {
            AlgorithmType.SINGLE_THREAD: [
                AlgorithmConfig(
                    AlgorithmType.SINGLE_THREAD,
                    ChudnovskySingleThread,
                    num_workers=1,
                    cache_enabled=True,
                    cache_dir=self.cache_dir
                ),
                AlgorithmConfig(
                    AlgorithmType.SINGLE_THREAD,
                    BBPSingleThread,
                    num_workers=1,
                    cache_enabled=True,
                    cache_dir=self.cache_dir
                ),
                AlgorithmConfig(
                    AlgorithmType.SINGLE_THREAD,
                    MonteCarloSingleThread,
                    num_workers=1,
                    cache_enabled=False
                )
            ],
            AlgorithmType.MULTI_THREAD: [
                AlgorithmConfig(
                    AlgorithmType.MULTI_THREAD,
                    ChudnovskyBinarySplitting,
                    num_workers=4,
                    cache_enabled=True,
                    cache_dir=self.cache_dir
                ),
                AlgorithmConfig(
                    AlgorithmType.MULTI_THREAD,
                    ChudnovskyBlockParallel,
                    num_workers=4,
                    cache_enabled=True,
                    cache_dir=self.cache_dir
                ),
                AlgorithmConfig(
                    AlgorithmType.MULTI_THREAD,
                    BBPParallel,
                    num_workers=4,
                    cache_enabled=True,
                    cache_dir=self.cache_dir
                )
            ],
            AlgorithmType.GPU_ACCELERATED: []
        }
        
        # Проверяем доступность GPU алгоритмов
        try:
            import numpy as np
            algorithms[AlgorithmType.GPU_ACCELERATED].append(
                AlgorithmConfig(
                    AlgorithmType.GPU_ACCELERATED,
                    NumpyOptimizedChudnovsky,
                    num_workers=1,
                    cache_enabled=True,
                    cache_dir=self.cache_dir
                )
            )
        except ImportError:
            pass
        
        # Проверяем OpenCL
        try:
            import pyopencl
            algorithms[AlgorithmType.GPU_ACCELERATED].append(
                AlgorithmConfig(
                    AlgorithmType.GPU_ACCELERATED,
                    OpenCLChudnovsky,
                    num_workers=1,
                    device_id=0,
                    cache_enabled=True,
                    cache_dir=self.cache_dir
                )
            )
        except ImportError:
            pass
        
        # Проверяем CUDA
        try:
            import cupy
            algorithms[AlgorithmType.GPU_ACCELERATED].append(
                AlgorithmConfig(
                    AlgorithmType.GPU_ACCELERATED,
                    CudaChudnovsky,
                    num_workers=1,
                    device_id=0,
                    cache_enabled=True,
                    cache_dir=self.cache_dir
                )
            )
        except ImportError:
            pass
        
        return algorithms
    
    def _get_default_algorithms(self) -> Dict[AlgorithmType, List[AlgorithmConfig]]:
        """Возвращает алгоритмы по умолчанию"""
        return {
            AlgorithmType.SINGLE_THREAD: [
                AlgorithmConfig(
                    AlgorithmType.SINGLE_THREAD,
                    ChudnovskySingleThread,
                    num_workers=1,
                    cache_enabled=True,
                    cache_dir=self.cache_dir
                )
            ],
            AlgorithmType.MULTI_THREAD: [],
            AlgorithmType.GPU_ACCELERATED: []
        }
    
    def get_available_algorithms(self) -> Dict[str, List[str]]:
        """Возвращает список доступных алгоритмов"""
        result = {}
        
        for algo_type, configs in self.available_algorithms.items():
            algo_names = []
            for config in configs:
                if hasattr(config.algorithm_class, '__name__'):
                    algo_names.append(config.algorithm_class.__name__)
                else:
                    algo_names.append(str(config.algorithm_class))
            result[algo_type.value] = algo_names
        
        return result
    
    def select_algorithm(self, digits: int, mode: PerformanceMode = PerformanceMode.BALANCED,
                        algorithm_type: Optional[AlgorithmType] = None,
                        num_workers: Optional[int] = None) -> AlgorithmConfig:
        """
        Автоматически выбирает оптимальный алгоритм
        """
        # Фильтруем по типу алгоритма
        candidates = []
        if algorithm_type:
            candidates = self.available_algorithms.get(algorithm_type, [])
        else:
            # Собираем все доступные
            for configs in self.available_algorithms.values():
                candidates.extend(configs)
        
        if not candidates:
            raise ValueError("Нет доступных алгоритмов")
        
        # Выбираем лучший алгоритм на основе режима и размера
        best_config = self._choose_best_algorithm(candidates, digits, mode, num_workers)
        
        self.current_config = best_config
        return best_config
    
    def _choose_best_algorithm(self, candidates: List[AlgorithmConfig], 
                              digits: int, mode: PerformanceMode,
                              num_workers: Optional[int]) -> AlgorithmConfig:
        """Выбирает лучший алгоритм из кандидатов"""
        
        # Приоритеты в зависимости от режима
        if mode == PerformanceMode.FASTEST:
            # Приоритет: GPU > Multi-thread > Single-thread
            priority_order = [
                AlgorithmType.GPU_ACCELERATED,
                AlgorithmType.MULTI_THREAD,
                AlgorithmType.SINGLE_THREAD
            ]
        elif mode == PerformanceMode.PRECISION:
            # Приоритет: Single-thread > Multi-thread > GPU
            priority_order = [
                AlgorithmType.SINGLE_THREAD,
                AlgorithmType.MULTI_THREAD,
                AlgorithmType.GPU_ACCELERATED
            ]
        elif mode == PerformanceMode.MEMORY_EFFICIENT:
            # Приоритет: Single-thread > Multi-thread > GPU
            priority_order = [
                AlgorithmType.SINGLE_THREAD,
                AlgorithmType.MULTI_THREAD,
                AlgorithmType.GPU_ACCELERATED
            ]
        else:  # BALANCED
            # Приоритет: Multi-thread > GPU > Single-thread
            priority_order = [
                AlgorithmType.MULTI_THREAD,
                AlgorithmType.GPU_ACCELERATED,
                AlgorithmType.SINGLE_THREAD
            ]
        
        # Выбираем по приоритетам
        for algo_type in priority_order:
            for config in candidates:
                if config.algorithm_type == algo_type:
                    # Настраиваем количество потоков
                    if num_workers and config.algorithm_type in [AlgorithmType.MULTI_THREAD]:
                        config.num_workers = num_workers
                    
                    # Для больших чисел предпочитаем более мощные алгоритмы
                    if digits > 100000 and config.algorithm_type == AlgorithmType.SINGLE_THREAD:
                        continue
                    
                    return config
        
        # Если ничего не подошло, возвращаем первый доступный
        return candidates[0]
    
    def generate_pi(self, digits: int, 
                    mode: PerformanceMode = PerformanceMode.BALANCED,
                    algorithm_type: Optional[AlgorithmType] = None,
                    num_workers: Optional[int] = None,
                    progress_callback: Optional[Callable] = None,
                    force_regenerate: bool = False,
                    **kwargs) -> str:
        """
        Генерирует π используя оптимальный алгоритм
        """
        # Выбираем алгоритм
        config = self.select_algorithm(digits, mode, algorithm_type, num_workers)
        
        print(f"Используем алгоритм: {config.algorithm_class.__name__}")
        print(f"Тип: {config.algorithm_type.value}, потоков: {config.num_workers}")
        
        # Создаем экземпляр алгоритма
        if config.algorithm_type == AlgorithmType.SINGLE_THREAD:
            generator = config.algorithm_class(cache_dir=config.cache_dir if config.cache_enabled else None)
        elif config.algorithm_type == AlgorithmType.MULTI_THREAD:
            generator = config.algorithm_class(cache_dir=config.cache_dir if config.cache_enabled else None)
        elif config.algorithm_type == AlgorithmType.GPU_ACCELERATED:
            generator = config.algorithm_class(device_id=config.device_id)
        else:
            raise ValueError(f"Неизвестный тип алгоритма: {config.algorithm_type}")
        
        self.current_algorithm = generator
        
        # Генерируем π
        start_time = time.time()
        
        try:
            if config.algorithm_type == AlgorithmType.SINGLE_THREAD:
                pi_digits = generator.compute_pi(digits, progress_callback=progress_callback, **kwargs)
            elif config.algorithm_type == AlgorithmType.MULTI_THREAD:
                pi_digits = generator.compute_pi(digits, num_workers=config.num_workers, 
                                               progress_callback=progress_callback, **kwargs)
            elif config.algorithm_type == AlgorithmType.GPU_ACCELERATED:
                pi_digits = generator.compute_pi(digits, progress_callback=progress_callback, **kwargs)
            
            elapsed = time.time() - start_time
            
            # Сохраняем статистику
            stats_key = f"{config.algorithm_class.__name__}_{digits}_{config.num_workers}"
            self.performance_stats[stats_key] = {
                'time': elapsed,
                'digits': digits,
                'algorithm': config.algorithm_class.__name__,
                'type': config.algorithm_type.value,
                'workers': config.num_workers
            }
            
            print(f"Генерация завершена за {elapsed:.2f} сек")
            return pi_digits
            
        except Exception as e:
            print(f"Ошибка генерации: {e}")
            
            # Пробуем запасной алгоритм
            if config.algorithm_type != AlgorithmType.SINGLE_THREAD:
                print("Пробуем запасной однопоточный алгоритм...")
                fallback_config = AlgorithmConfig(
                    AlgorithmType.SINGLE_THREAD,
                    ChudnovskySingleThread,
                    num_workers=1,
                    cache_enabled=True,
                    cache_dir=self.cache_dir
                )
                
                generator = ChudnovskySingleThread(cache_dir=self.cache_dir)
                return generator.compute_pi(digits, progress_callback=progress_callback, **kwargs)
            else:
                raise
        
        finally:
            # Очищаем ресурсы для GPU
            if config.algorithm_type == AlgorithmType.GPU_ACCELERATED:
                if hasattr(generator, 'cleanup'):
                    generator.cleanup()
    
    def benchmark_algorithms(self, digits: int = 1000, iterations: int = 3) -> Dict[str, Dict[str, float]]:
        """
        Тестирует производительность всех доступных алгоритмов
        """
        results = {}
        
        print(f"🧪 Бенчмарк алгоритмов для {digits:,} цифр:")
        
        for algo_type, configs in self.available_algorithms.items():
            for config in configs:
                algo_name = config.algorithm_class.__name__
                print(f"\n📊 Тестируем {algo_name}...")
                
                times = []
                
                for i in range(iterations):
                    try:
                        start = time.time()
                        self.generate_pi(
                            digits, 
                            algorithm_type=algo_type,
                            num_workers=config.num_workers
                        )
                        elapsed = time.time() - start
                        times.append(elapsed)
                        
                        print(f"   Запуск {i+1}: {elapsed:.3f} сек")
                        
                    except Exception as e:
                        print(f"   Запуск {i+1}: ❌ {e}")
                        times.append(float('inf'))
                
                # Статистика
                valid_times = [t for t in times if t != float('inf')]
                if valid_times:
                    results[algo_name] = {
                        'avg_time': sum(valid_times) / len(valid_times),
                        'min_time': min(valid_times),
                        'max_time': max(valid_times),
                        'success_rate': len(valid_times) / iterations,
                        'type': algo_type.value,
                        'workers': config.num_workers
                    }
                    
                    print(f"   Среднее: {results[algo_name]['avg_time']:.3f} сек")
                    print(f"   Успешность: {results[algo_name]['success_rate']*100:.1f}%")
                else:
                    print(f"   ❌ Все запуски неудачны")
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Dict[str, Any]]:
        """Возвращает статистику производительности"""
        return self.performance_stats.copy()
    
    def clear_cache(self):
        """Очищает кэш"""
        if os.path.exists(self.cache_dir):
            import shutil
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)
            print("Кэш очищен")

def test_universal_generator():
    """Тест универсального генератора"""
    
    print("🧪 Тест универсального генератора π:")
    
    generator = UniversalPiGenerator(cache_dir="/tmp/test_universal_pi")
    
    # Показываем доступные алгоритмы
    print("\n📋 Доступные алгоритмы:")
    available = generator.get_available_algorithms()
    for algo_type, names in available.items():
        print(f"  {algo_type}: {', '.join(names)}")
    
    # Тестируем разные режимы
    modes = [PerformanceMode.BALANCED, PerformanceMode.FASTEST, PerformanceMode.PRECISION]
    precision = 1000
    
    for mode in modes:
        print(f"\n🎯 Режим: {mode.value}")
        
        start = time.time()
        pi_digits = generator.generate_pi(precision, mode=mode)
        elapsed = time.time() - start
        
        print(f"   Время: {elapsed:.3f} сек")
        print(f"   Первые 20 цифр: {pi_digits[:20]}")
        
        # Проверяем правильность
        known_pi = "14159265358979323846"
        if pi_digits.startswith(known_pi):
            print("   ✅ Правильно")
        else:
            print("   ❌ Неправильно")
    
    # Бенчмарк
    print("\n🏃 Бенчмарк алгоритмов:")
    benchmark_results = generator.benchmark_algorithms(1000, 2)
    
    # Сортируем по среднему времени
    sorted_results = sorted(benchmark_results.items(), key=lambda x: x[1]['avg_time'])
    
    print("\n📊 Результаты бенчмарка:")
    for algo_name, stats in sorted_results:
        print(f"  {algo_name}: {stats['avg_time']:.3f} сек "
              f"({stats['type']}, {stats['workers']} потоков)")

if __name__ == "__main__":
    test_universal_generator()
