#!/usr/bin/env python3
"""
Chudnovsky Block Parallel - блочный параллельный алгоритм
"""

from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
import time
import threading
from typing import List, Tuple, Optional, Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

class ChudnovskyBlockParallel:
    """Блочный параллельный Chudnovsky"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
    
    def get_algorithm_name(self) -> str:
        return "Chudnovsky (Block Parallel)"
    
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
        
        # Создаем прогресс-бар
        try:
            from utils.working_progress import create_working_progress_bar
            progress_bar = create_working_progress_bar("Block", 20)
            progress_bar(0)
        except ImportError:
            progress_bar = None
        
        # Вычисляем количество итераций
        max_iterations = digits // 14 + 1
        block_size = max(1, max_iterations // num_workers)
        
        print(f"Требуется итераций: {max_iterations:,}")
        print(f"Размер блока: {block_size:,} итераций")
        
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
        
        # Разделяем на блоки
        blocks = []
        for i in range(num_workers):
            start = i * block_size
            end = min(start + block_size, max_iterations)
            if start < max_iterations:
                blocks.append((i, start, end, precision))
        
        # Вычисляем блоки параллельно
        block_results = []
        
        with ProcessPoolExecutor(max_workers=min(num_workers, len(blocks))) as executor:
            future_to_block = {
                executor.submit(self._compute_block, block): block 
                for block in blocks
            }
            
            for future in as_completed(future_to_block):
                try:
                    result = future.result()
                    block_results.append(result)
                    completed += 1
                    
                    if progress_callback:
                        progress = (completed / num_workers) * 100
                        progress_callback(progress, completed, num_workers)
                        
                except Exception as e:
                    print(f"Ошибка в блоке: {e}")
        
        if progress_bar:
            progress_bar(100)
        
        # Комбинируем результаты блоков
        total_sum = Decimal(0)
        for block_id, block_sum in sorted(block_results):
            total_sum += block_sum
        
        # Вычисляем π
        C = Decimal(426880) * Decimal(10005).sqrt()
        pi = C / total_sum
        
        pi_str = str(pi)[:digits]
        
        # Сохраняем в кэш
        if self.cache_dir:
            with open(cache_file, 'w') as f:
                f.write(pi_str)
        
        elapsed = time.time() - start_time
        print(f"Блочное вычисление завершено за {elapsed:.2f} сек")
        
        if progress_callback:
            progress_callback(100, num_workers, num_workers)
        
        return pi_str
    
    @staticmethod
    def _compute_block(args: Tuple[int, int, int, int]) -> Tuple[int, Decimal]:
        """
        Вычисляет блок итераций Chudnovsky
        """
        worker_id, start, end, precision = args
        getcontext().prec = precision
        
        # Константы
        C = Decimal(426880) * Decimal(10005).sqrt()
        
        # Инициализация
        M = Decimal(1)
        L = Decimal(13591409)
        X = Decimal(1)
        K = 6
        
        # Пропускаем до start
        for i in range(start):
            M = M * (K**3 - 16*K) // (i + 1)**3
            L += 545140134
            X *= -2625374126407680000
            K += 12
        
        # Вычисляем сумму для блока
        block_sum = Decimal(0)
        for i in range(start, end):
            term = M * L / X
            block_sum += term
            
            M = M * (K**3 - 16*K) // (i + 1)**3
            L += 545140134
            X *= -2625374126407680000
            K += 12
        
        return (worker_id, block_sum)
