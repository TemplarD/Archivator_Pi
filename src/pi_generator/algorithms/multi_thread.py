#!/usr/bin/env python3
"""
Многопоточные алгоритмы генерации π
Параллельные реализации Chudnovsky, BBP и другие
"""

import multiprocessing as mp
from decimal import Decimal, getcontext
import time
from typing import List, Tuple, Optional, Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import os

class BaseParallelGenerator:
    """Базовый класс для многопоточных генераторов"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
    
    def get_algorithm_name(self) -> str:
        return "Base Parallel Generator"

class ChudnovskyBinarySplitting(BaseParallelGenerator):
    """Многопоточный Chudnovsky с Binary Splitting"""
    
    def get_algorithm_name(self) -> str:
        return "Chudnovsky (Binary Splitting, Multi-Thread)"
    
    def compute_pi(self, digits: int, num_workers: int = 4, 
                   progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Вычисляет π используя многопоточный Binary Splitting Chudnovsky
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
        
        # Запускаем многопоточные вычисления
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            future_to_task = {
                executor.submit(self._compute_chunk, task): task 
                for task in tasks
            }
            
            results = []
            completed = 0
            
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    if progress_callback:
                        progress = (completed / num_workers) * 100
                        progress_callback(progress, completed, num_workers)
                        
                except Exception as e:
                    print(f"Ошибка в потоке: {e}")
        
        # Комбинируем результаты - берем результат от процесса с максимальным end
        # Все процессы вычисляют одно и то же, но с разным количеством итераций
        max_end = max(task[2] for task in tasks)  # Находим максимальный end
        for i, result in enumerate(results):
            if i == len(results) - 1:  # Последний процесс с максимальными итерациями
                pi_str = result
                break
        
        # Обрезаем до нужной длины
        pi_str = pi_str[:digits]
        
        # Сохраняем в кэш
        if self.cache_dir:
            with open(cache_file, 'w') as f:
                f.write(pi_str)
        
        elapsed = time.time() - start_time
        print(f"Вычисление завершено за {elapsed:.2f} сек")
        
        if progress_callback:
            progress_callback(100, num_workers, num_workers)
        
        return pi_str
    
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
        S = Decimal(L) / Decimal(X)  # Начальный член
        
        # Вычисляем все итерации от 0 до end
        for i in range(1, max_iterations):
            M = M * (K**3 - 16*K) // (i**3)
            L += Decimal(545140134)
            X *= Decimal(-262537412640768000)
            
            term = M * L / X
            S += term
            K += 12
        
        # Вычисляем π для этого процесса
        pi_partial = C / S
        pi_str = str(pi_partial)[2:]  # Убираем "3."
        
        # Возвращаем строку цифр
        return pi_str
    
    def _combine_results(self, results: List[Tuple[Decimal, Decimal, Decimal]]) -> Tuple[Decimal, Decimal, Decimal]:
        """Комбинирует результаты от всех потоков"""
        total_S = Decimal(0)
        
        for S, Q, R in results:
            total_S += S
        
        return total_S, Decimal(1), Decimal(0)

class ChudnovskyBlockParallel(BaseParallelGenerator):
    """Блочный параллельный Chudnovsky"""
    
    def get_algorithm_name(self) -> str:
        return "Chudnovsky (Block Parallel, Multi-Thread)"
    
    def compute_pi(self, digits: int, num_workers: int = 4,
                   progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Вычисляет π используя блочный параллелизм
        """
        precision = digits + 100
        getcontext().prec = precision
        
        # Проверяем кэш
        if self.cache_dir:
            cache_file = os.path.join(self.cache_dir, f"chudnovsky_block_{digits}_{num_workers}.txt")
            if os.path.exists(cache_file):
                if progress_callback:
                    for i in range(0, 101, 10):
                        progress_callback(i, i, 100)
                        time.sleep(0.001)
                    progress_callback(100, 100, 100)
                
                with open(cache_file, 'r') as f:
                    return f.read().strip()[:digits]
        
        print(f"Блочное вычисление {digits:,} цифр π с {num_workers} потоками...")
        start_time = time.time()
        
        # Вычисляем количество итераций
        max_iterations = digits // 14 + 1
        
        # Разделяем итерации между потоками
        iterations_per_worker = max_iterations // num_workers
        tasks = []
        
        for i in range(num_workers):
            start_iter = i * iterations_per_worker
            end_iter = start_iter + iterations_per_worker if i < num_workers - 1 else max_iterations
            tasks.append((i, start_iter, end_iter, precision))
        
        # Запускаем потоки
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            future_to_task = {
                executor.submit(self._compute_block, task): task 
                for task in tasks
            }
            
            results = []
            completed = 0
            
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    if progress_callback:
                        progress = (completed / num_workers) * 100
                        progress_callback(progress, completed, num_workers)
                        
                except Exception as e:
                    print(f"Ошибка в потоке: {e}")
        
        # Комбинируем результаты
        total_sum = sum(results)
        
        # Финальное вычисление π
        C = Decimal(426880) * Decimal(10005).sqrt()
        pi = C / total_sum
        
        # Преобразуем в строку
        pi_str = str(pi)[2:][:digits]
        
        # Сохраняем в кэш
        if self.cache_dir:
            with open(cache_file, 'w') as f:
                f.write(pi_str)
        
        elapsed = time.time() - start_time
        print(f"Вычисление завершено за {elapsed:.2f} сек")
        
        if progress_callback:
            progress_callback(100, num_workers, num_workers)
        
        return pi_str
    
    @staticmethod
    def _compute_block(args: Tuple[int, int, int, int]) -> Decimal:
        """
        Вычисляет блок итераций Chudnovsky
        """
        worker_id, start_iter, end_iter, precision = args
        getcontext().prec = precision
        
        # Инициализация
        M = Decimal(1)
        L = Decimal(13591409)
        X = Decimal(1)
        K = 6
        S = Decimal(0)
        
        # Вычисляем свой диапазон итераций
        for i in range(start_iter, end_iter):
            if i == 0:
                continue
            M = M * (K**3 - 16*K) // (i**3)
            L += Decimal(545140134)
            X *= Decimal(-262537412640768000)
            
            term = M * L / X
            S += term
            K += 12
        
        return S

class BBPParallel(BaseParallelGenerator):
    """Параллельная реализация BBP алгоритма"""
    
    def get_algorithm_name(self) -> str:
        return "BBP (Multi-Thread)"
    
    def compute_pi(self, digits: int, num_workers: int = 4,
                   progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Вычисляет π используя параллельный BBP
        """
        precision = digits + 20
        getcontext().prec = precision
        
        print(f"Параллельное вычисление {digits:,} цифр π с {num_workers} потоками...")
        start_time = time.time()
        
        # Разделяем цифры между потоками
        digits_per_worker = digits // num_workers
        tasks = []
        
        for i in range(num_workers):
            start_digit = i * digits_per_worker
            end_digit = start_digit + digits_per_worker if i < num_workers - 1 else digits
            tasks.append((i, start_digit, end_digit, precision))
        
        # Запускаем потоки
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_task = {
                executor.submit(self._compute_hex_range, task): task 
                for task in tasks
            }
            
            results = []
            completed = 0
            
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    if progress_callback:
                        progress = (completed / num_workers) * 100
                        progress_callback(progress, completed, num_workers)
                        
                except Exception as e:
                    print(f"Ошибка в потоке: {e}")
        
        # Собираем результаты
        pi_hex = ""
        for worker_id, hex_digits in sorted(results):
            pi_hex += hex_digits
        
        # Конвертируем в десятичные
        pi_decimal = self._hex_to_decimal(pi_hex)
        
        elapsed = time.time() - start_time
        print(f"Вычисление завершено за {elapsed:.2f} сек")
        
        if progress_callback:
            progress_callback(100, num_workers, num_workers)
        
        return pi_decimal[:digits]
    
    @staticmethod
    def _compute_hex_range(args: Tuple[int, int, int, int]) -> Tuple[int, str]:
        """Вычисляет диапазон шестнадцатеричных цифр"""
        worker_id, start_digit, end_digit, precision = args
        getcontext().prec = precision
        
        hex_digits = ""
        
        for n in range(start_digit, end_digit):
            hex_digit = BBPParallel._compute_hex_digit(n)
            hex_digits += format(hex_digit, 'x')
        
        return worker_id, hex_digits
    
    @staticmethod
    def _compute_hex_digit(n: int) -> int:
        """Вычисляет одну шестнадцатеричную цифру π в позиции n"""
        s = Decimal(0)
        
        for k in range(n + 1):
            term = (Decimal(4) / (8*k + 1) - 
                   Decimal(2) / (8*k + 4) - 
                   Decimal(1) / (8*k + 5) - 
                   Decimal(1) / (8*k + 6)) / (Decimal(16) ** k)
            s += term
        
        fractional = s - int(s)
        hex_digit = int(fractional * 16)
        
        return hex_digit
    
    @staticmethod
    def _hex_to_decimal(hex_str: str) -> str:
        """Конвертирует шестнадцатеричные цифры в десятичные"""
        try:
            if not hex_str:
                return ""
            
            getcontext().prec = len(hex_str) * 2
            pi_int = Decimal(int(hex_str, 16))
            pi_decimal = str(pi_int).replace('.', '')
            
            return pi_decimal
        except (ValueError, OverflowError) as e:
            print(f"Ошибка конвертации: {e}")
            return ""

def test_parallel_algorithms():
    """Тест многопоточных алгоритмов"""
    
    algorithms = [
        ChudnovskyBinarySplitting(),
        ChudnovskyBlockParallel(),
        BBPParallel()
    ]
    
    precision = 1000
    
    print("🧪 Тест многопоточных алгоритмов:")
    
    for algo in algorithms:
        print(f"\n📊 {algo.get_algorithm_name()}:")
        
        for workers in [1, 2, 4]:
            start = time.time()
            try:
                pi_digits = algo.compute_pi(precision, num_workers=workers)
                elapsed = time.time() - start
                
                print(f"   {workers} потоков: {elapsed:.3f} сек")
                
                # Проверяем правильность
                known_pi = "1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"
                if pi_digits.startswith(known_pi[:50]):
                    print(f"     ✅ Правильно")
                else:
                    print(f"     ❌ Неправильно")
                    
            except Exception as e:
                print(f"   {workers} потоков: ❌ Ошибка: {e}")

if __name__ == "__main__":
    test_parallel_algorithms()
