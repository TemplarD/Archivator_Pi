#!/usr/bin/env python3
"""
Однопоточные алгоритмы Chudnovsky
"""

from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
import time
import os
import math
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
        precision = digits + 100
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
        
        # Предвычисленные константы (правильная реализация)
        A = Decimal(13591409)
        B = Decimal(545140134)
        C = Decimal(640320)
        C3_OVER_24 = C**3 / Decimal(24)  # 640320^3 / 24
        
        # Количество итераций для нужной точности
        max_iterations = int(digits / 14.18) + 3
        
        # Инициализация (правильная)
        P = Decimal(1)  # P_0
        Q = Decimal(1)  # Q_0
        S = A           # S_0 = A * P_0 / Q_0
        
        k = Decimal(1)
        
        # Вычисление суммы
        for i in range(max_iterations):
            # Вычисляем множитель для P_k
            # M = (6k-5)(2k-1)(6k-1)
            M = (6*k - 5) * (2*k - 1) * (6*k - 1)
            
            # Обновляем P и Q по рекуррентным формулам
            P = P * (-M)  # P_k = P_{k-1} * (-(6k-5)(2k-1)(6k-1))
            Q = Q * (k**3 * C3_OVER_24)  # Q_k = Q_{k-1} * (k^3 * C3_OVER_24)
            
            # Вычисляем член ряда: T_k = P_k/Q_k * (A + B*k)
            K_term = A + B * k
            term = (P * K_term) / Q
            
            # Добавляем к сумме
            S += term
            
            # Обновляем прогресс
            if progress_callback and i % 10 == 0:
                progress = (i / max_iterations) * 100
                progress_callback(progress, i, max_iterations)
            
            k += 1
        
        # Вычисление π
        sqrt_10005 = Decimal(10005).sqrt()
        pi = (Decimal(426880) * sqrt_10005) / S
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
