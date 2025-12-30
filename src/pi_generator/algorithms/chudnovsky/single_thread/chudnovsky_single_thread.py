#!/usr/bin/env python3
"""
Однопоточные алгоритмы Chudnovsky
"""

from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
import time
import os
from typing import Optional, Callable

class BaseChudnovskySingleThread(ABC):
    """Базовый класс для однопоточных Chudnovsky генераторов"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
    
    @abstractmethod
    def compute_pi(self, digits: int, **kwargs) -> str:
        """Вычисляет π с указанной точностью"""
        pass
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """Возвращает название алгоритма"""
        pass

class ChudnovskySingleThread(BaseChudnovskySingleThread):
    """Однопоточная реализация Chudnovsky алгоритма"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        super().__init__(cache_dir)
        self._factorial_cache = {}
    
    def get_algorithm_name(self) -> str:
        return "Chudnovsky (Single Thread)"
    
    def compute_pi(self, digits: int, progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Однопоточный алгоритм Chudnovsky с кэшированием факториалов
        """
        # Устанавливаем точность с запасом
        precision = digits + 50
        getcontext().prec = precision
        
        # Проверяем кэш
        if self.cache_dir:
            cache_file = os.path.join(self.cache_dir, f"chudnovsky_{digits}.txt")
            if os.path.exists(cache_file):
                if progress_callback:
                    for i in range(0, 101, 10):
                        progress_callback(i, i, 100)
                        time.sleep(0.001)
                    progress_callback(100, 100, 100)
                
                with open(cache_file, 'r') as f:
                    return f.read().strip()[:digits]
        
        # Предвычисленные константы
        C = Decimal(426880) * Decimal(10005).sqrt()
        max_iterations = digits // 14 + 1
        
        # Инициализация
        M = Decimal(1)
        L = Decimal(13591409)
        X = Decimal(1)
        K = 6
        
        total_sum = Decimal(0)
        
        for i in range(max_iterations):
            term = M * L / X
            total_sum += term
            
            M = M * (K**3 - 16*K) // (i + 1)**3
            L += 545140134
            X *= -2625374126407680000
            K += 12
            
            # Обновляем прогресс
            if progress_callback and i % 10 == 0:
                progress = (i / max_iterations) * 100
                progress_callback(progress, i, max_iterations)
        
        pi = C / total_sum
        pi_str = str(pi)[:digits]
        
        # Сохраняем в кэш
        if self.cache_dir:
            with open(cache_file, 'w') as f:
                f.write(pi_str)
        
        if progress_callback:
            progress_callback(100, max_iterations, max_iterations)
        
        return pi_str
    
    def _cached_factorial(self, n: int) -> Decimal:
        """Кэшированное вычисление факториала"""
        if n in self._factorial_cache:
            return self._factorial_cache[n]
        
        result = Decimal(1)
        for i in range(2, n + 1):
            result *= i
        
        self._factorial_cache[n] = result
        return result
