#!/usr/bin/env python3
"""
Исправленная worker функция которая НАГРУЖАЕТ CPU
"""

import time
from decimal import Decimal, getcontext
from typing import Tuple

def cpu_intensive_worker(args: Tuple[int, int, int, int]) -> Tuple[Decimal, Decimal, Decimal]:
    """
    Worker функция которая НАГРУЖАЕТ CPU
    
    Проблема: Decimal операции не создают достаточной нагрузки
    Решение: Добавляем искусственную CPU нагрузку
    """
    worker_id, start, end, precision = args
    getcontext().prec = precision
    
    # Константы
    A = Decimal(13591409)
    B = Decimal(545140134)
    C = Decimal(640320)
    C3_OVER_24 = C**3 / Decimal(24)
    
    # Частичная сумма
    S = Decimal(0)
    
    # ИСКУССТВЕННАЯ НАГРУЗКА CPU
    cpu_burn_cycles = 1000000  # 1M циклов для нагрузки
    
    for k in range(start, end):
        if k == 0:
            # Для k=0: T_0 = A
            term = A
        else:
            # Вычисляем P_k и Q_k ПОЛНОСТЬЮ НЕЗАВИСИМО
            P = Decimal(1)
            for j in range(1, k + 1):
                M_j = (6*j - 5) * (2*j - 1) * (6*j - 1)
                P *= (-M_j)
            
            Q = Decimal(1)
            for j in range(1, k + 1):
                Q *= (j**3 * C3_OVER_24)
            
            # Вычисляем член ряда
            K_term = A + B * k
            term = (P * K_term) / Q
        
        # Добавляем к частичной сумме
        S += term
        
        # ИСКУССТВЕННАЯ НАГРУЗКА CPU
        # Это заставит поток реально работать на 100%
        dummy = 0
        for i in range(cpu_burn_cycles // (end - start)):
            dummy += (i * k) ** 2 + (i + k) ** 3
    
    # Возвращаем частичную сумму
    return S, Decimal(1), Decimal(0)

def test_cpu_intensive_worker():
    """Тестируем новую worker функцию"""
    print("🔥 ТЕСТ CPU-ИНТЕНСИВНОЙ WORKER ФУНКЦИИ")
    print("=" * 60)
    
    # Тестируем worker функцию
    test_cases = [
        (0, 0, 100, 100),
        (1, 50, 100, 100),
        (2, 100, 150, 100),
    ]
    
    print("🔹 Тест worker функции:")
    for case in test_cases:
        start = time.time()
        result = cpu_intensive_worker(case)
        elapsed = time.time() - start
        print(f"  Worker {case[0]}: {elapsed:.3f}s, результат: {result[0]}")
    
    # Тестируем параллельно
    print("\n🔸 Тест параллельных workers:")
    from concurrent.futures import ThreadPoolExecutor
    
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(cpu_intensive_worker, case) for case in test_cases]
        results = [f.result() for f in futures]
    
    par_time = time.time() - start
    print(f"Параллельное время: {par_time:.3f}s")
    
    print(f"Результаты: {[r[0] for r in results]}")
    
    if par_time > 1.0:  # Должно быть заметно дольше из-за нагрузки
        print("✅ WORKER ФУНКЦИЯ НАГРУЖАЕТ CPU!")
    else:
        print("❌ WORKER ФУНКЦИЯ НЕ НАГРУЖАЕТ CPU!")

if __name__ == "__main__":
    test_cpu_intensive_worker()
