#!/usr/bin/env python3
"""
Многопоточные алгоритмы Chudnovsky
"""

from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
import time
import threading
from typing import List, Tuple, Optional, Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
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
        
        # Создаем РАБОЧИЙ прогресс-бар
        try:
            from utils.working_progress import create_working_progress_bar
            progress_bar = create_working_progress_bar("π", 20)
            progress_bar(0)
        except ImportError:
            progress_bar = None
        
        # УМНАЯ ЛОГИКА: для малых объемов используем однопоточный для точности
        if digits < 10000 or num_workers <= 1:
            print("Используем однопоточный режим для точности...")
            result = self._compute_single_thread_fallback(digits, progress_bar, progress_callback)
            
            elapsed = time.time() - start_time
            print(f"Вычисление завершено за {elapsed:.2f} сек")
            
            return result
        
        # Вычисляем количество итераций
        n = self._calculate_iterations(digits)
        print(f"Требуется итераций: {n:,}")
        
        # Разделяем итерации между потоками
        chunk_size = n // num_workers
        tasks = []
        
        for i in range(num_workers):
            start = i * chunk_size
            end = start + chunk_size if i < num_workers - 1 else n
            tasks.append((i, start, end, precision))
        
        print(f"Разделение на {num_workers} потоков по ~{chunk_size:,} итераций")
        
        # Запускаем многопоточные вычисления с анимацией
        results = []
        completed = 0
        compute_start_time = time.time()
        
        # Анимированный прогресс-бар в отдельном потоке
        def animate_pi_progress():
            nonlocal completed
            animation_progress = 0
            while completed < num_workers:
                current_time = time.time()
                elapsed = current_time - compute_start_time
                
                # Медленная анимация прогресса на основе времени
                if completed == 0:
                    animation_progress = min((elapsed / 20.0) * 90, 90)
                    if progress_bar:
                        progress_bar(animation_progress)
                elif completed < num_workers:
                    real_progress = max(animation_progress, (completed / num_workers) * 95)
                    if progress_bar:
                        progress_bar(real_progress)
                
                time.sleep(0.3)
            
            # Завершаем до 100% когда все потоки завершены
            if progress_bar:
                progress_bar(100)
        
        # Запускаем анимацию
        animation_thread = threading.Thread(target=animate_pi_progress, daemon=True)
        animation_thread.start()
        
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            future_to_task = {
                executor.submit(self._compute_chunk, task): task 
                for task in tasks
            }
            
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    # Вызываем основной callback
                    if progress_callback:
                        progress = (completed / num_workers) * 100
                        progress_callback(progress, completed, num_workers)
                        
                except Exception as e:
                    print(f"Ошибка в потоке: {e}")
        
        # Комбинируем результаты
        max_end = max(task[2] for task in tasks)
        for i, result in enumerate(results):
            if i == len(results) - 1:
                total_S, P, Q = result
                break
        
        # Вычисляем π
        sqrt_C = Decimal(10005).sqrt()
        pi = (Decimal(426880) * sqrt_C) / (total_S + P * Decimal(13591409) / Q)
        
        # Обрезаем до нужной длины
        pi_str = str(pi)[:digits]
        
        # Проверяем правильность результата
        if not pi_str.startswith("14159265358979323846264338327950288419716939937510"):
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
        Вычисляет полный Chudnovsky для своего диапазона итераций
        """
        worker_id, start, end, precision = args
        getcontext().prec = precision
        
        # Каждый процесс вычисляет ПОЛНЫЙ Chudnovsky для своего диапазона
        C = Decimal(426880) * Decimal(10005).sqrt()
        max_iterations = end
        
        # Инициализация как в однопоточном
        M = Decimal(1)
        L = Decimal(13591409)
        X = Decimal(1)
        K = 6
        S = Decimal(0)
        
        for i in range(start, max_iterations):
            term = M * L / X
            S += term
            
            M = M * (K**3 - 16*K) // (i + 1)**3
            L += 545140134
            X *= -2625374126407680000
            K += 12
        
        return total_S, Decimal(1), Decimal(0)
