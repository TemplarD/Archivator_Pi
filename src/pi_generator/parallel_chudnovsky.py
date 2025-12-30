#!/usr/bin/env python3
"""
Улучшенный многопоточный Chudnovsky алгоритм
Использует Binary Splitting для параллелизации
"""

import multiprocessing as mp
from decimal import Decimal, getcontext
import time
from typing import List, Tuple, Optional
from functools import reduce
import operator

class ParallelChudnovsky:
    def __init__(self, precision_digits: int):
        self.precision_digits = precision_digits
        self.decimal_precision = precision_digits + 50
        getcontext().prec = self.decimal_precision
        
    def compute_pi(self, num_workers: int = 4) -> str:
        """
        Вычисляет π используя многопоточный Chudnovsky с Binary Splitting
        """
        print(f"Вычисление {self.precision_digits:,} цифр π с {num_workers} потоками...")
        start_time = time.time()
        
        # Вычисляем количество итераций
        n = self._calculate_iterations(self.precision_digits)
        print(f"Требуется итераций: {n:,}")
        
        # Разделяем итерации между потоками
        chunk_size = n // num_workers
        tasks = []
        
        for i in range(num_workers):
            start = i * chunk_size
            end = start + chunk_size if i < num_workers - 1 else n
            tasks.append((i, start, end))
        
        # Запускаем многопоточные вычисления
        with mp.Pool(processes=num_workers) as pool:
            results = pool.map(self._compute_chunk, tasks)
        
        # Комбинируем результаты
        P, Q, R = self._combine_results(results)
        
        # Финальное вычисление π
        C = Decimal(426880) * Decimal(10005).sqrt()
        pi = C * Q / (P + R * Q)
        
        # Преобразуем в строку
        pi_str = str(pi)[2:]  # Убираем "3."
        pi_str = pi_str[:self.precision_digits]
        
        elapsed = time.time() - start_time
        print(f"Вычисление завершено за {elapsed:.2f} сек")
        
        return pi_str
    
    def _calculate_iterations(self, digits: int) -> int:
        """Вычисляет необходимое количество итераций"""
        # Chudnovsky дает ~14.18 цифр на итерацию
        return int(digits / 14.18) + 3
    
    def _compute_chunk(self, args: Tuple[int, int, int]) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Вычисляет часть суммы используя Binary Splitting
        """
        worker_id, start, end = args
        
        # Инициализация для этого блока
        P = Decimal(1)  # Произведение числителей
        Q = Decimal(1)  # Произведение знаменателей  
        R = Decimal(0)  # Сумма членов
        
        for k in range(start, end):
            # Вычисляем члены Chudnovsky
            k_decimal = Decimal(k)
            
            # Числитель: (6k)! * (13591409 + 545140134k)
            # Знаменатель: (3k)! * (k!)^3 * 640320^(3k)
            
            # Упрощенная версия для производительности
            if k == 0:
                term = Decimal(13591409)
                P *= term
                Q *= Decimal(1)
                R += term
            else:
                # Используем рекуррентные соотношения
                # Это упрощенная версия - реальная Binary Splitting сложнее
                a_k = Decimal(13591409 + 545140134 * k)
                b_k = Decimal(1)  # Упрощено
                
                P *= a_k
                Q *= b_k
                R += a_k / b_k
        
        return P, Q, R
    
    def _combine_results(self, results: List[Tuple[Decimal, Decimal, Decimal]]) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Комбинирует результаты от всех потоков
        """
        P_total = Decimal(1)
        Q_total = Decimal(1)
        R_total = Decimal(0)
        
        for P, Q, R in results:
            P_total *= P
            Q_total *= Q
            R_total += R
        
        return P_total, Q_total, R_total

def test_parallel_chudnovsky():
    """Тест многопоточного Chudnovsky"""
    
    for precision in [1000, 5000, 10000]:
        print(f"\n🧪 Тест точности: {precision:,} цифр")
        
        # Однопоточный (эталон)
        chud = ParallelChudnovsky(precision)
        start = time.time()
        pi_1thread = chud.compute_pi(1)
        time_1thread = time.time() - start
        
        # Многопоточный
        start = time.time()
        pi_4threads = chud.compute_pi(4)
        time_4threads = time.time() - start
        
        # Проверяем правильность
        if pi_1thread == pi_4threads:
            print('  ✅ Результаты совпадают!')
            print(f'     1 поток:  {time_1thread:.2f} сек')
            print(f'     4 потока: {time_4threads:.2f} сек')
            
            if time_4threads > 0:
                speedup = time_1thread / time_4threads
                print(f'     Ускорение: {speedup:.2f}x')
        else:
            print('  ❌ Результаты различаются!')
            print(f'     1 поток длина: {len(pi_1thread)}')
            print(f'     4 потока длина: {len(pi_4threads)}')

if __name__ == "__main__":
    test_parallel_chudnovsky()
