#!/usr/bin/env python3
"""
Правильная реализация алгоритма Чудновских
Основано на полном математическом разборе
"""

import os
import time
import math
from decimal import Decimal, getcontext
from typing import Optional, Callable

class CorrectChudnovskySingleThread:
    """Правильная реализация Chudnovsky с полной математической основой"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
    
    def get_algorithm_name(self) -> str:
        return "Chudnovsky (Correct Implementation)"
    
    def compute_pi(self, digits: int, progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Правильная реализация Chudnovsky
        
        Основная формула:
        1/π = 12 ∑ (-1)^k * (6k)! * (545140134k + 13591409) / [(3k)! * (k!)^3 * (640320)^(3k + 3/2)]
        
        Упрощенная версия:
        π = [426880 * √10005] / ∑ T_k
        где T_k = (-1)^k * (6k)! * (545140134k + 13591409) / [(3k)! * (k!)^3 * (640320)^(3k)]
        """
        # 1. Установка точности
        precision = digits + 50  # запас для точности
        getcontext().prec = precision
        
        # 2. Проверяем кэш
        if self.cache_dir:
            cache_file = os.path.join(self.cache_dir, f"chudnovsky_correct_{digits}.txt")
            if os.path.exists(cache_file):
                if progress_callback:
                    for i in range(0, 101, 10):
                        progress_callback(i, i, 100)
                        time.sleep(0.001)
                    progress_callback(100, 100, 100)
                
                with open(cache_file, 'r') as f:
                    return f.read().strip()[:digits]
        
        # 3. Константы (из математического разбора)
        A = Decimal(13591409)
        B = Decimal(545140134)
        C = Decimal(640320)
        C3_OVER_24 = C**3 / Decimal(24)  # 640320^3 / 24
        
        # 4. Инициализация (правильная)
        P = Decimal(1)  # P_0
        Q = Decimal(1)  # Q_0
        S = A           # S_0 = A * P_0 / Q_0
        
        k = Decimal(1)
        
        # 5. Вычисление суммы
        # Количество итераций для нужной точности: digits / 14.18 + 3
        max_iterations = int(digits / 14.18) + 3
        
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
        
        # 6. Вычисление π
        # π = (426880 * √10005) / S
        sqrt_10005 = Decimal(10005).sqrt()
        pi = (Decimal(426880) * sqrt_10005) / S
        
        pi_str = str(pi)[:digits]
        
        # 7. Сохраняем в кэш
        if self.cache_dir:
            with open(cache_file, 'w') as f:
                f.write(pi_str)
        
        return pi_str

def test_correct_implementation():
    """Тест правильной реализации"""
    print("🧪 Тест правильной реализации Chudnovsky:")
    print("=" * 60)
    
    generator = CorrectChudnovskySingleThread()
    
    # Тест с 100 цифр
    print("📊 100 цифр: ", end="")
    start = time.time()
    result = generator.compute_pi(100)
    elapsed = time.time() - start
    
    expected = "3.14159265358979323846264338327950288419716939937510"
    correct = result.startswith(expected)
    
    print(f"{elapsed:.3f}s, коррект: {correct}")
    print(f"   Результат: {result[:50]}...")
    
    print()
    print("🎯 Сравнение:")
    print(f"Ожидается: {expected[:30]}...")
    print(f"Получено  : {result[:30]}...")
    print(f"Совпадает : {result.startswith(expected)}")
    
    if correct:
        print("🎉🎉🎉 ПРАВИЛЬНАЯ РЕАЛИЗАЦИЯ РАБОТАЕТ! 🎉🎉🎉")
        return True
    else:
        print("❌ Все еще есть проблемы")
        for i in range(min(30, len(result))):
            if i < len(expected) and result[i] != expected[i]:
                print(f"  Позиция {i}: ожид=\"{expected[i]}\" получ=\"{result[i]}\"")
                break
        return False

if __name__ == "__main__":
    test_correct_implementation()
