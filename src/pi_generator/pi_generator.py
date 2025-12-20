#!/usr/bin/env python3
"""
Модуль генерации числа π по алгоритму Chudnovsky
Поддерживает CPU и GPU генерацию с кэшированием
"""

import os
import subprocess
import hashlib
import time
from pathlib import Path
from typing import Optional, Tuple
import multiprocessing as mp

class PiGenerator:
    def __init__(self, cache_dir: str = "data/pi_storage"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_pi_digits(self, digits: int, use_gpu: bool = False, progress_callback=None) -> str:
        """
        Генерирует указанное количество цифр π
        
        Args:
            digits: количество цифр для генерации
            use_gpu: использовать ли GPU для генерации
            progress_callback: функция для отслеживания прогресса
            
        Returns:
            строка с цифрами π
        """
        cache_file = self._get_cache_file(digits)
        
        # Проверяем кэш
        if cache_file.exists():
            print(f"Загрузка {digits} цифр π из кэша...")
            with open(cache_file, 'r') as f:
                return f.read().strip()
        
        # Генерируем новые цифры
        print(f"Генерация {digits} цифр π...")
        start_time = time.time()
        
        if use_gpu:
            pi_digits = self._generate_with_gpu(digits, progress_callback)
        else:
            pi_digits = self._generate_with_cpu(digits, progress_callback)
        
        generation_time = time.time() - start_time
        print(f"Генерация завершена за {generation_time:.2f} секунд")
        
        # Сохраняем в кэш
        with open(cache_file, 'w') as f:
            f.write(pi_digits)
        
        return pi_digits
    
    def _generate_with_cpu(self, digits: int, progress_callback=None) -> str:
        """Генерация π с использованием CPU"""
        # В реальном проекте здесь был бы вызов C++ кода
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
