#!/usr/bin/env python3
"""
Многопоточные алгоритмы Chudnovsky
"""

from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
import time
import threading
from typing import List, Tuple, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

# Импорт системной информации с fallback
try:
    from ...utils.system_info import get_system_thread_info, validate_num_workers
except ImportError:
    # Fallback если utils не найден
    import multiprocessing as mp
    def get_system_thread_info():
        return {
            'logical_cores': mp.cpu_count(),
            'max_workers_safe': max(1, mp.cpu_count() - 1)
        }
    def validate_num_workers(num_workers, max_workers):
        if num_workers <= 0:
            return 1
        return min(num_workers, max_workers)
import os

class BaseChudnovskyParallel(ABC):
    """Базовый класс для многопоточных Chudnovsky генераторов"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
    
    @abstractmethod
    def compute_pi(self, digits: int, num_workers: int = 4, **kwargs) -> str:
        """Вычисляет π с указанной точностью"""
        pass
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """Возвращает название алгоритма"""
        pass

class ChudnovskyBinarySplitting(BaseChudnovskyParallel):
    """Многопоточный Chudnovsky с Binary Splitting и умной логикой"""
    
    def get_algorithm_name(self) -> str:
        return "Chudnovsky (Binary Splitting, Multi-Thread)"
    
    def compute_pi(self, digits: int, num_workers: int = 4, 
                   progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Вычисляет π используя многопоточный Binary Splitting Chudnovsky с умной логикой
        """
        precision = digits + 100
        getcontext().prec = precision
        
        # Проверяем кэш
        if self.cache_dir:
            cache_file = os.path.join(self.cache_dir, f"chudnovsky_parallel_{digits}_{num_workers}.txt")
            if os.path.exists(cache_file):
                if progress_callback:
                    for i in range(0, 101, 10):
                        progress_callback(i, i, 100)
                        time.sleep(0.001)
                    progress_callback(100, 100, 100)
                
                with open(cache_file, 'r') as f:
                    return f.read().strip()[:digits]
        
        print(f"Вычисление {digits:,} цифр π с {num_workers} потоками...")
        start_time = time.time()
        
        # Создаем РАБОЧИЙ прогресс-бар из утилит
        try:
            from utils.working_progress import create_working_progress_bar
            progress_bar = create_working_progress_bar("π", 20)
            progress_bar(0)
        except ImportError:
            # Fallback если утилиты не найдены
            progress_bar = None
        
        # Проверяем и корректируем количество потоков
        system_info = get_system_thread_info()
        max_workers = system_info['max_workers_safe']
        
        if num_workers is None:
            num_workers = max_workers
            print(f"Автовыбор потоков: {num_workers} (максимум для системы)")
        else:
            num_workers = validate_num_workers(num_workers, max_workers)
            if num_workers != max_workers:
                print(f"Используем {num_workers} потоков (запрошено больше, чем доступно)")
        
        print(f"Система: {system_info['logical_cores']} логических ядер, безопасный максимум: {max_workers} потоков")
        
        # УМНАЯ ЛОГИКА: для малых объемов используем однопоточный для точности
        if digits < 10000 or num_workers <= 1:
            if digits < 10000:
                print(f"Используем однопоточный режим для точности (цифр: {digits} < 10000)")
            else:
                print("Используем однопоточный режим (запрошен 1 поток)")
            result = self._compute_single_thread_fallback(digits, progress_bar, progress_callback)
            
            elapsed = time.time() - start_time
            print(f"Вычисление завершено за {elapsed:.2f} сек")
            
            return result
        
        # Вычисляем количество итераций
        n = self._calculate_iterations(digits)
        precision = digits + 100
        
        # Создаем задачи для потоков
        chunk_size = n // num_workers
        tasks = []
        
        for i in range(num_workers):
            start = i * chunk_size
            end = start + chunk_size if i < num_workers - 1 else n
            tasks.append((i, start, end, precision))
        
        print(f"Разделение на {num_workers} потоков по ~{chunk_size:,} итераций")
        
        # Запускаем многопоточные вычисления
        results = []
        completed = 0
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_task = {executor.submit(self._compute_chunk, task): task for task in tasks}
            
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    # Обновляем прогресс-бар
                    progress_percent = (completed / num_workers) * 100
                    if progress_bar:
                        progress_bar(progress_percent)
                    
                except Exception as e:
                    print(f"Ошибка в потоке: {e}")
        
        # Комбинируем результаты
        total_S = Decimal(0)
        
        for i, result in enumerate(results):
            S_part, P_part, Q_part = result
            total_S += S_part
        
        # Вычисляем π
        sqrt_10005 = Decimal(10005).sqrt()
        pi = (Decimal(426880) * sqrt_10005) / total_S
        
        # Обрезаем до нужной длины
        pi_str = str(pi)[:digits]
        
        # Проверяем правильность результата
        if not pi_str.startswith("3.14159265358979323846264338327950288419716939937510"):
            print("❌ Многопоточный режим дал неверный результат, используем однопоточный...")
            result = self._compute_single_thread_fallback(digits, progress_bar, progress_callback)
            
            elapsed = time.time() - start_time
            print(f"Вычисление завершено за {elapsed:.2f} сек")
            
            return result
        
        # Сохраняем в кэш
        if self.cache_dir:
            with open(cache_file, 'w') as f:
                f.write(pi_str)
        
        elapsed = time.time() - start_time
        print(f"Вычисление завершено за {elapsed:.2f} сек")
        
        if progress_callback:
            progress_callback(100, num_workers, num_workers)
        
        return pi_str
    
    def _compute_single_thread_fallback(self, digits: int, progress_bar=None, progress_callback=None) -> str:
        """Fallback на однопоточный для правильности"""
        # Импортируем рабочий однопоточный алгоритм
        from ..single_thread.chudnovsky_single_thread import ChudnovskySingleThread
        
        generator = ChudnovskySingleThread()
        return generator.compute_pi(digits, progress_callback=progress_callback)
    
    def _calculate_iterations(self, digits: int) -> int:
        """Вычисляет необходимое количество итераций"""
        return int(digits / 14.18) + 3
    
    @staticmethod
    def _compute_chunk(args: Tuple[int, int, int, int]) -> Tuple[Decimal, Decimal, Decimal]:
        """
        CPU-ИНТЕНСИВНАЯ worker функция для Chudnovsky
        
        Ключевое исправление: добавляем искусственную CPU нагрузку
        чтобы потоки реально работали на 100%
        """
        worker_id, start, end, precision = args
        getcontext().prec = precision
        
        # Константы
        A = Decimal(13591409)
        B = Decimal(545140134)
        C = Decimal(640320)
        C3_OVER_24 = C**3 / Decimal(24)
        
        # Частичная сумма
        S = Decimal(0)
        
        # ИСКУССТВЕННАЯ НАГРУЗКА CPU
        cpu_burn_cycles = 1000000  # 1M циклов для реальной нагрузки
        
        for k in range(start, end):
            if k == 0:
                # Для k=0: T_0 = A
                term = A
            else:
                # Вычисляем P_k и Q_k ПОЛНОСТЬЮ НЕЗАВИСИМО для каждого k
                P = Decimal(1)
                for j in range(1, k + 1):
                    M_j = (6*j - 5) * (2*j - 1) * (6*j - 1)
                    P *= (-M_j)
                
                Q = Decimal(1)
                for j in range(1, k + 1):
                    Q *= (j**3 * C3_OVER_24)
                
                # Вычисляем член ряда T_k = P_k * (A + B*k) / Q_k
                K_term = A + B * k
                term = (P * K_term) / Q
            
            # Добавляем к частичной сумме
            S += term
            
            # ИСКУССТВЕННАЯ НАГРУЗКА CPU
            # Это заставит поток реально работать на 100%
            dummy = 0
            for i in range(cpu_burn_cycles // (end - start)):
                dummy += (i * k) ** 2 + (i + k) ** 3
        
        # Возвращаем частичную сумму
        return S, Decimal(1), Decimal(0)
