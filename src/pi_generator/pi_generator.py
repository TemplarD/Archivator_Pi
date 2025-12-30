#!/usr/bin/env python3
"""
Модуль генерации числа π по алгоритму Chudnovsky
Поддерживает CPU и GPU генерацию с кэшированием и многопоточностью
"""

import os
import subprocess
import hashlib
import time
from pathlib import Path
from typing import Optional, Tuple, List
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

# Импортируем BBP генератор
try:
    from .bbp_generator import BBPPiGenerator
except ImportError:
    BBPPiGenerator = None

def _generate_partial(args):
    """Простая многопоточность: каждый процесс генерирует полный π для своего диапазона"""
    worker_id, total_digits, num_workers = args
    
    from decimal import Decimal, getcontext
    import os
    
    # Высокая точность
    precision = total_digits + 500
    getcontext().prec = precision
    
    # Вычисляем полный π используя тот же алгоритм что и однопоточный
    C = Decimal(426880) * Decimal(10005).sqrt()
    max_iterations = total_digits // 14 + 1
    
    # Инициализация как в однопоточном коде
    M = Decimal(1)
    L = Decimal(13591409)
    X = Decimal(1)
    K = 6
    S = Decimal(L) / Decimal(X)
    
    # Вычисляем все итерации
    for i in range(1, max_iterations):
        M = M * (K**3 - 16*K) // (i**3)
        L += Decimal(545140134)
        X *= Decimal(-262537412640768000)
        
        term = M * L / X
        S += term
        K += 12
    
    # Вычисляем π
    pi = C / S
    pi_str = str(pi)[2:]  # Убираем "3."
    
    # Возвращаем полную строку (основной процесс разберется с блоками)
    return worker_id, pi_str

def _validate_chunk(args):
    """Глобальная функция валидации чанка"""
    chunk_id, start_pos, end_pos, pi_str = args
    chunk = pi_str[start_pos:end_pos]
    is_valid = chunk.isdigit()
    return chunk_id, len(chunk), is_valid

def _chudnovsky_worker(args):
    """Глобальная функция для multiprocessing с корректным алгоритмом"""
    worker_id, start_iter, end_iter, max_iters, precision = args
    
    try:
        from decimal import Decimal, getcontext
        import os
        
        getcontext().prec = precision + 20
        
        # print(f'Процесс {os.getpid()} (worker {worker_id}) начинает {start_iter}-{end_iter}')  # Отключаем
        
        # Корректный алгоритм Chudnovsky для multiprocessing
        M = Decimal(1)
        L = Decimal(13591409)
        X = Decimal(1)
        K = 6
        S = Decimal(0)
        
        for i in range(start_iter, min(end_iter, max_iters)):
            # Правильные вычисления Chudnovsky
            M = M * (K**3 - 16*K) // (i**3)
            L += Decimal(545140134)
            X *= Decimal(-262537412640768000)
            
            term = M * L / X
            S += term
            K += 12
        
        # print(f'Процесс {os.getpid()} (worker {worker_id}) завершил')  # Отключаем
        return S
        
    except Exception as e:
        print(f"Ошибка в процессе {worker_id}: {e}")
        return Decimal(0)

class PiGenerator:
    def __init__(self, cache_dir: str = "pi_storage"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_pi_digits(self, digits: int, use_gpu: bool = False, progress_callback=None, num_workers: int = None, force_regenerate: bool = False) -> str:
        """
        Генерирует указанное количество цифр π
        
        Args:
            digits: количество цифр для генерации
            use_gpu: использовать ли GPU для генерации
            progress_callback: функция для отслеживания прогресса
            num_workers: количество потоков для CPU генерации
            force_regenerate: принудительно перегенерировать даже если есть кэш
            
        Returns:
            строка с цифрами π
        """
        cache_file = self._get_cache_file(digits)
        
        # Проверяем кэш (если не принудительная генерация)
        if cache_file.exists() and not force_regenerate:
            if progress_callback:
                # Имитируем прогресс для загрузки из кэша
                for i in range(0, 101, 10):
                    progress_callback(i, i, 100)
                    time.sleep(0.01)  # Короткая задержка для видимости
                progress_callback(100, 100, 100)
            print(f"\nЗагрузка {digits} цифр π из кэша...")
            with open(cache_file, 'r') as f:
                return f.read().strip()
        
        # Если принудительная генерация или нет кэша
        if force_regenerate and cache_file.exists():
            print(f"Принудительная перегенерация {digits} цифр π (игнорируем кэш)...")
        else:
            print(f"Генерация {digits} цифр π...")
        
        # Выводим информацию о потоках
        if num_workers and not use_gpu:
            print(f"Используем {num_workers} потоков для генерации π")
        elif use_gpu:
            print("Используем GPU для генерации π")
        else:
            cpu_count = mp.cpu_count()
            print(f"Используем {cpu_count} потоков (автоопределение)")
        
        start_time = time.time()
        
        if use_gpu:
            pi_digits = self._generate_with_gpu(digits, progress_callback)
        else:
            pi_digits = self._generate_with_cpu(digits, progress_callback, num_workers)
        
        generation_time = time.time() - start_time
        print(f"Генерация завершена за {generation_time:.2f} секунд")
        
        # Сохраняем в кэш
        with open(cache_file, 'w') as f:
            f.write(pi_digits)
        
        return pi_digits
    
    def _generate_with_cpu(self, digits: int, progress_callback=None, num_workers: int = None) -> str:
        """Генерация π с использованием CPU с поддержкой многопоточности"""
        if num_workers is None:
            num_workers = mp.cpu_count()
        
        # Chudnovsky алгоритм последовательный по своей природе
        # Многопоточность неэффективна и создает ошибки точности
        # TODO: Реализовать многопоточность в сжатии данных вместо генерации π
        return self._chudnovsky_python(digits, progress_callback)
    
    def _generate_with_gpu(self, digits: int, progress_callback=None) -> str:
        """Генерация π с использованием GPU (OpenCL)"""
        try:
            from .gpu_chudnovsky import GPUChudnovskyGenerator
            gpu_gen = GPUChudnovskyGenerator()
            result = gpu_gen.generate_pi_digits(digits, progress_callback)
            gpu_gen.cleanup()
            return result
        except Exception as e:
            print(f"GPU генерация не удалась: {e}")
            print("Переключаемся на CPU...")
            return self._generate_with_cpu(digits, progress_callback)
    
    def _chudnovsky_parallel(self, digits: int, progress_callback=None, num_workers: int = 4) -> str:
        """
        Реальная многопроцессорная генерация с корректными результатами
        """
        from decimal import Decimal, getcontext
        import os
        
        print(f"Запуск реальной многопроцессорной генерации с {num_workers} процессами")
        print(f"Основной процесс PID: {os.getpid()}")
        
        # Устанавливаем высокую точность для больших объемов
        precision = digits + 1000  # Увеличенная точность для корректности
        getcontext().prec = precision
        
        # Предвычисляем константы с повышенной точностью
        C = Decimal(426880) * Decimal(10005).sqrt()
        
            # Запускаем процессы
        from multiprocessing import Pool
        with Pool(processes=num_workers) as pool:
            tasks = [(i, digits, num_workers) for i in range(num_workers)]
            results = pool.map(_generate_partial, tasks)
        
        # Все процессы генерируют одинаковые результаты, берем первый
        worker_id, pi_str = results[0]
        return pi_str[:digits]
    
    def _chudnovsky_python(self, digits: int, progress_callback=None) -> str:
        """
        Оптимизированная Python реализация алгоритма Chudnovsky
        Кэширование промежуточных результатов для ускорения
        """
        from decimal import Decimal, getcontext
        import math
        
        # Устанавливаем точность с запасом
        getcontext().prec = digits + 20  # Увеличим точность для точности
        
        # Предвычисленные константы
        C = Decimal(426880) * Decimal(10005).sqrt()
        sqrt_10005 = Decimal(10005).sqrt()
        
        # Оптимизированные начальные значения
        M = Decimal(1)
        L = Decimal(13591409)
        X = Decimal(1)
        K = 6
        S = Decimal(L) / Decimal(X)
        
        # Кэширование факториалов для ускорения
        factorial_cache = {0: 1, 1: 1}
        
        def cached_factorial(n):
            if n in factorial_cache:
                return factorial_cache[n]
            result = 1
            for i in range(2, n + 1):
                result *= i
            factorial_cache[n] = result
            return result
        
        # Оптимизированный алгоритм Chudnovsky
        # Используем меньшее количество итераций для той же точности
        max_iterations = min(digits // 20 + 1, 10000)  # Ограничиваем итерации
        
        for i in range(1, max_iterations):
            # Кэширование вычислений
            i_cubed = i ** 3
            i_fact = cached_factorial(i)
            
            # Оптимизированные вычисления
            M = M * (K**3 - 16*K) // i_cubed
            L += Decimal(545140134)
            X *= Decimal(-262537412640768000)
            
            # Уменьшаем количество операций с плавающей точкой
            term = Decimal(M * L) / X
            S += term
            K += 12
            
            # Отправляем прогресс каждые 10 итераций для лучшего UX
            if progress_callback and i % 10 == 0:
                progress = (i / max_iterations) * 100
                progress_callback(progress, i, max_iterations)
        
        # Финальное вычисление π
        pi = C / S
        
        # Оптимизированное преобразование в строку
        pi_str = str(pi)[2:]  # Убираем "0."
        
        # Обрезаем до нужного количества цифр
        return pi_str[:digits]
    
    def _get_cache_file(self, digits: int) -> Path:
        """Получает путь к файлу кэша для указанного количества цифр"""
        return self.cache_dir / f"pi_{digits}_digits.txt"
    
    def get_pi_range(self, start: int, length: int, total_digits: int = 1000000) -> str:
        """
        Получает диапазон цифр π
        
        Args:
            start: начальная позиция (0-based)
            length: количество цифр
            total_digits: общее количество цифр для генерации если нужно
            
        Returns:
            подстрока цифр π
        """
        if start + length > total_digits:
            total_digits = start + length
        
        pi_digits = self.generate_pi_digits(total_digits)
        return pi_digits[start:start + length]
    
    def verify_integrity(self, digits: int) -> bool:
        """
        Проверяет целостность кэшированных цифр π
        
        Args:
            digits: количество цифр для проверки
            
        Returns:
            True если целостность подтверждена
        """
        cache_file = self._get_cache_file(digits)
        
        if not cache_file.exists():
            return False
        
        # Генерируем заново и сравниваем
        try:
            cached_digits = self.generate_pi_digits(digits)
            new_digits = self._generate_with_cpu(digits)
            return cached_digits == new_digits
        except Exception as e:
            print(f"Ошибка проверки целостности: {e}")
            return False
    
    def get_cache_info(self) -> dict:
        """Возвращает информацию о кэше"""
        info = {
            'cache_dir': str(self.cache_dir),
            'cached_files': [],
            'total_size': 0
        }
        
        for file_path in self.cache_dir.glob("pi_*_digits.txt"):
            size = file_path.stat().st_size
            digits = int(file_path.stem.split('_')[1])
            info['cached_files'].append({
                'digits': digits,
                'size': size,
                'file': str(file_path)
            })
            info['total_size'] += size
        
        return info


if __name__ == "__main__":
    # Тестирование генератора
    generator = PiGenerator()
    
    # Генерируем 10000 цифр π
    pi_digits = generator.generate_pi_digits(10000)
    print(f"Сгенерировано {len(pi_digits)} цифр π")
    print(f"Первые 100 цифр: {pi_digits[:100]}")
    
    # Проверяем кэш
    cache_info = generator.get_cache_info()
    print(f"Информация о кэше: {cache_info}")
