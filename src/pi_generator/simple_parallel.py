#!/usr/bin/env python3
"""
Простая и надежная многопоточная генерация π
Каждый поток генерирует свой блок цифр независимо
"""

import multiprocessing as mp
from decimal import Decimal, getcontext
import time
from typing import List, Tuple, Optional

def generate_pi_block(args: Tuple[int, int, int]) -> Tuple[int, str]:
    """
    Генерирует блок цифр π используя однопоточный алгоритм
    Каждый процесс полностью независим
    """
    worker_id, start_digit, num_digits = args
    
    # Устанавливаем высокую точность
    precision = start_digit + num_digits + 100
    getcontext().prec = precision
    
    # Используем тот же алгоритм что и в однопоточном режиме
    C = Decimal(426880) * Decimal(10005).sqrt()
    max_iterations = (start_digit + num_digits) // 14 + 1
    
    # Инициализация
    M = Decimal(1)
    L = Decimal(13591409)
    X = Decimal(1)
    K = 6
    S = Decimal(L) / Decimal(X)
    
    # Вычисляем сумму
    for i in range(1, max_iterations):
        M = M * (K**3 - 16*K) // (i**3)
        L += Decimal(545140134)
        X *= Decimal(-262537412640768000)
        
        term = M * L / X
        S += term
        K += 12
    
    # Вычисляем π
    pi = C / S
    pi_str = str(pi)[2:]  # Убираем "3."
    
    # Возвращаем нужный блок
    block = pi_str[start_digit:start_digit + num_digits]
    
    return worker_id, block

def parallel_pi_generator(num_digits: int, num_workers: int = 4) -> str:
    """
    Простая многопоточная генерация π
    """
    print(f"Генерация {num_digits:,} цифр π с {num_workers} потоками...")
    start_time = time.time()
    
    # Разделяем работу на блоки
    block_size = num_digits // num_workers
    tasks = []
    
    for i in range(num_workers):
        start = i * block_size
        end = start + block_size if i < num_workers - 1 else num_digits
        size = end - start
        tasks.append((i, start, size))
    
    # Запускаем процессы
    with mp.Pool(processes=num_workers) as pool:
        results = pool.map(generate_pi_block, tasks)
    
    # Собираем результаты
    pi_digits = ""
    for worker_id, block in sorted(results):
        pi_digits += block
    
    # Обрезаем до нужной длины
    pi_digits = pi_digits[:num_digits]
    
    elapsed = time.time() - start_time
    print(f"Генерация завершена за {elapsed:.2f} сек")
    
    return pi_digits

if __name__ == "__main__":
    # Тест
    pi_1000 = parallel_pi_generator(1000, 4)
    print(f"Первые 50 цифр: {pi_1000[:50]}")
    print(f"Длина: {len(pi_1000)}")
