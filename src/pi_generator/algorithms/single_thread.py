#!/usr/bin/env python3
"""
Базовые однопоточные алгоритмы генерации π
Chudnovsky, BBP, и другие последовательные реализации
"""

from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
import time
from typing import Optional, Callable
import os

class BasePiGenerator(ABC):
    """Базовый класс для генераторов π"""
    
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

class ChudnovskySingleThread(BasePiGenerator):
    """Однопоточная реализация Chudnovsky алгоритма"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        super().__init__(cache_dir)
        self._factorial_cache = {0: 1, 1: 1}
    
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
        S = Decimal(L) / Decimal(X)
        
        # Основной цикл
        for i in range(1, max_iterations):
            if progress_callback and i % 10 == 0:
                progress = (i / max_iterations) * 100
                progress_callback(progress, i, max_iterations)
            
            # Кэширование вычислений
            i_cubed = i ** 3
            i_fact = self._cached_factorial(i)
            
            M = M * (K**3 - 16*K) // i_cubed
            L += Decimal(545140134)
            X *= Decimal(-262537412640768000)
            
            term = M * L / X
            S += term
            K += 12
        
        # Финальное вычисление
        pi = C / S
        pi_str = str(pi)[2:][:digits]
        
        # Сохраняем в кэш
        if self.cache_dir:
            with open(cache_file, 'w') as f:
                f.write(pi_str)
        
        if progress_callback:
            progress_callback(100, max_iterations, max_iterations)
        
        return pi_str
    
    def _cached_factorial(self, n: int) -> int:
        """Кэшированное вычисление факториала"""
        if n in self._factorial_cache:
            return self._factorial_cache[n]
        
        result = 1
        for i in range(2, n + 1):
            result *= i
        
        self._factorial_cache[n] = result
        return result

class BBPSingleThread(BasePiGenerator):
    """Однопоточная реализация BBP алгоритма для шестнадцатеричных цифр"""
    
    def get_algorithm_name(self) -> str:
        return "BBP (Single Thread)"
    
    def compute_pi(self, digits: int, progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Вычисляет π используя BBP формулу (для шестнадцатеричных цифр)
        """
        precision = digits + 20
        getcontext().prec = precision
        
        pi_hex = ""
        
        for n in range(digits):
            if progress_callback and n % 100 == 0:
                progress = (n / digits) * 100
                progress_callback(progress, n, digits)
            
            hex_digit = self._compute_hex_digit(n)
            pi_hex += format(hex_digit, 'x')
        
        # Конвертируем в десятичные
        pi_decimal = self._hex_to_decimal(pi_hex)
        
        if progress_callback:
            progress_callback(100, digits, digits)
        
        return pi_decimal[:digits]
    
    def _compute_hex_digit(self, n: int) -> int:
        """Вычисляет одну шестнадцатеричную цифру π в позиции n"""
        s = Decimal(0)
        
        for k in range(n + 1):
            term = (Decimal(4) / (8*k + 1) - 
                   Decimal(2) / (8*k + 4) - 
                   Decimal(1) / (8*k + 5) - 
                   Decimal(1) / (8*k + 6)) / (Decimal(16) ** k)
            s += term
        
        # Извлекаем дробную часть
        fractional = s - int(s)
        hex_digit = int(fractional * 16)
        
        return hex_digit
    
    def _hex_to_decimal(self, hex_str: str) -> str:
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

class MonteCarloSingleThread(BasePiGenerator):
    """Однопоточный метод Монте-Карло (для демонстрации)"""
    
    def get_algorithm_name(self) -> str:
        return "Monte Carlo (Single Thread)"
    
    def compute_pi(self, digits: int, progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Вычисляет π методом Монте-Карло (медленно, для демонстрации)
        """
        import random
        
        # Для Монте-Карло нам нужно много точек для точности
        points = 10 ** (digits // 2 + 2)
        inside_circle = 0
        
        for i in range(points):
            if progress_callback and i % 100000 == 0:
                progress = (i / points) * 100
                progress_callback(progress, i, points)
            
            x = random.random()
            y = random.random()
            
            if x**2 + y**2 <= 1:
                inside_circle += 1
        
        pi_estimate = 4 * inside_circle / points
        
        # Преобразуем в строку с нужной точностью
        getcontext().prec = digits + 10
        pi_decimal = str(Decimal(pi_estimate))[2:][:digits]
        
        if progress_callback:
            progress_callback(100, points, points)
        
        return pi_decimal

def test_single_thread_algorithms():
    """Тест однопоточных алгоритмов"""
    
    algorithms = [
        ChudnovskySingleThread(),
        BBPSingleThread(),
        MonteCarloSingleThread()
    ]
    
    precision = 100
    
    print("🧪 Тест однопоточных алгоритмов:")
    
    for algo in algorithms:
        print(f"\n📊 {algo.get_algorithm_name()}:")
        
        start = time.time()
        try:
            pi_digits = algo.compute_pi(precision)
            elapsed = time.time() - start
            
            print(f"   Время: {elapsed:.3f} сек")
            print(f"   Первые 20 цифр: {pi_digits[:20]}")
            
            # Проверяем правильность (известные цифры π)
            known_pi = "14159265358979323846"
            if pi_digits.startswith(known_pi):
                print("   ✅ Правильно")
            else:
                print("   ❌ Неправильно")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    test_single_thread_algorithms()
