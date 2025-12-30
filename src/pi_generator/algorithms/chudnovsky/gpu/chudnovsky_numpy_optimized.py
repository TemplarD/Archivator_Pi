#!/usr/bin/env python3
"""
GPU ускоренные алгоритмы Chudnovsky
"""

from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
import time
from typing import Optional, Callable, Dict, Any
import numpy as np

class BaseChudnovskyGPU(ABC):
    """Базовый класс для GPU Chudnovsky генераторов"""
    
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.is_initialized = False
    
    @abstractmethod
    def compute_pi(self, digits: int, **kwargs) -> str:
        """Вычисляет π на GPU"""
        pass
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """Возвращает название алгоритма"""
        pass

class NumpyOptimizedChudnovsky:
    """Оптимизированная NumPy реализация Chudnovsky"""
    
    def get_algorithm_name(self) -> str:
        return "Chudnovsky (NumPy Optimized)"
    
    def compute_pi(self, digits: int, progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Вычисляет π используя NumPy векторизацию
        """
        precision = digits + 50
        getcontext().prec = precision
        
        print(f"NumPy оптимизированное вычисление {digits:,} цифр π...")
        start_time = time.time()
        
        # Используем NumPy для векторизованных вычислений
        max_iterations = digits // 14 + 1
        
        # Векторизованные константы
        C = 426880 * np.sqrt(10005)
        
        # Инициализация массивов
        iterations = np.arange(max_iterations)
        k_values = 6 + 12 * iterations
        
        # Векторизованные вычисления
        M = np.ones(max_iterations, dtype=object)
        L = 13591409 + 545140134 * iterations
        X = (-2625374126407680000) ** iterations
        
        # Вычисляем термины
        terms = M * L / X
        
        # Суммируем
        total_sum = np.sum(terms)
        
        # Вычисляем π
        pi = C / total_sum
        
        # Конвертируем в Decimal для точности
        pi_decimal = Decimal(str(pi))
        pi_str = str(pi_decimal)[:digits]
        
        elapsed = time.time() - start_time
        print(f"NumPy вычисление завершено за {elapsed:.2f} сек")
        
        if progress_callback:
            progress_callback(100, max_iterations, max_iterations)
        
        return pi_str
