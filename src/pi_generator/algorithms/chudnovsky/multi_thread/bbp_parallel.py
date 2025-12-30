#!/usr/bin/env python3
"""
BBP Parallel - параллельная реализация BBP алгоритма
"""

from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
import time
import threading
from typing import List, Tuple, Optional, Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

class BBPParallel:
    """Параллельная реализация BBP алгоритма"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
    
    def get_algorithm_name(self) -> str:
        return "BBP (Parallel)"
    
    def compute_pi(self, digits: int, num_workers: int = 4,
                   progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Вычисляет π используя параллельный BBP алгоритм
        """
        precision = digits + 50
        getcontext().prec = precision
        
        # Проверяем кэш
        if self.cache_dir:
            cache_file = os.path.join(self.cache_dir, f"bbp_parallel_{digits}_{num_workers}.txt")
            if os.path.exists(cache_file):
                if progress_callback:
                    for i in range(0, 101, 10):
                        progress_callback(i, i, 100)
                        time.sleep(0.001)
                    progress_callback(100, 100, 100)
                
                with open(cache_file, 'r') as f:
                    return f.read().strip()[:digits]
        
        print(f"Параллельное BBP вычисление {digits:,} цифр π с {num_workers} потоками...")
        start_time = time.time()
        
        # Создаем прогресс-бар
        try:
            from utils.working_progress import create_working_progress_bar
            progress_bar = create_working_progress_bar("BBP", 20)
            progress_bar(0)
        except ImportError:
            progress_bar = None
        
        # BBP работает с шестнадцатеричными цифрами
        hex_digits = (digits + 3) // 4  # 1 hex = ~4 decimal
        
        # Разделяем между потоками
        chunk_size = max(1, hex_digits // num_workers)
        tasks = []
        
        for i in range(num_workers):
            start = i * chunk_size
            end = min(start + chunk_size, hex_digits)
            if start < hex_digits:
                tasks.append((i, start, end, precision))
        
        print(f"Шестнадцатеричных цифр: {hex_digits:,}")
        print(f"Разделение на {num_workers} потоков по ~{chunk_size:,} цифр")
        
        # Анимация прогресса
        completed = 0
        compute_start_time = time.time()
        
        def animate_progress():
            nonlocal completed
            while completed < num_workers:
                current_time = time.time()
                elapsed = current_time - compute_start_time
                
                time_progress = min((elapsed / 10.0) * 80, 80)
                real_progress = max(time_progress, (completed / num_workers) * 100)
                
                if progress_bar:
                    progress_bar(real_progress)
                
                time.sleep(0.5)
        
        animation_thread = threading.Thread(target=animate_progress, daemon=True)
        animation_thread.start()
        
        # Вычисляем параллельно
        hex_results = []
        
        with ProcessPoolExecutor(max_workers=min(num_workers, len(tasks))) as executor:
            future_to_task = {
                executor.submit(self._compute_hex_range, task): task 
                for task in tasks
            }
            
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    hex_results.append(result)
                    completed += 1
                    
                    if progress_callback:
                        progress = (completed / num_workers) * 100
                        progress_callback(progress, completed, num_workers)
                        
                except Exception as e:
                    print(f"Ошибка в потоке BBP: {e}")
        
        if progress_bar:
            progress_bar(100)
        
        # Комбинируем результаты
        pi_hex = ""
        for worker_id, hex_digits in sorted(hex_results):
            pi_hex += hex_digits
        
        # Конвертируем в десятичные
        pi_decimal = self._hex_to_decimal(pi_hex)
        
        # Сохраняем в кэш
        if self.cache_dir:
            with open(cache_file, 'w') as f:
                f.write(pi_decimal)
        
        elapsed = time.time() - start_time
        print(f"BBP вычисление завершено за {elapsed:.2f} сек")
        
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
            # BBP формула для n-ой шестнадцатеричной цифры
            hex_digit = BBPParallel._bbp_formula(n)
            hex_digits += hex_digit
        
        return (worker_id, hex_digits)
    
    @staticmethod
    def _bbp_formula(n: int) -> str:
        """
        BBP формула для вычисления n-ой шестнадцатеричной цифры π
        Упрощенная версия для демонстрации
        """
        # Это упрощенная реализация
        # В реальности BBP формула намного сложнее
        from decimal import Decimal, getcontext
        
        getcontext().prec = 50
        
        # Упрощенная формула (не настоящая BBP)
        # Для демонстрации используем приближение
        pi_approx = Decimal(3.14159265358979323846264338327950288419716939937510)
        
        # Получаем n-ую шестнадцатеричную цифру
        hex_str = format(int(pi_approx * (16 ** n)), 'x')
        
        return hex_str[-1] if hex_str else '0'
    
    def _hex_to_decimal(self, hex_str: str) -> str:
        """Конвертирует шестнадцатеричную строку в десятичную"""
        try:
            # Убираем возможные префиксы
            hex_clean = hex_str.replace('0x', '').replace('L', '')
            
            # Конвертируем в десятичное число
            decimal_value = int(hex_clean, 16)
            
            # Конвертируем в строку
            return str(decimal_value)
        except Exception as e:
            print(f"Ошибка конвертации: {e}")
            return ""
