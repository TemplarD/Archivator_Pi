#!/usr/bin/env python3
"""
Простой тест проверки работы потоков
"""

import sys
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Добавляем путь к модулям
test_dir = Path(__file__).parent
project_root = test_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

def simple_cpu_task():
    """Простая CPU задача"""
    end = time.time() + 2
    count = 0
    while time.time() < end:
        count += 1
        # Интенсивные вычисления
        _ = [i**2 for i in range(1000)]
    return count

def test_threadpool_executor():
    """Тест ThreadPoolExecutor"""
    print("🧪 ТЕСТ THREADPOOLEXECUTOR")
    print("=" * 50)
    
    # Тест 1: Последовательно
    print("🔹 Последовательное выполнение:")
    start = time.time()
    results = []
    for i in range(4):
        result = simple_cpu_task()
        results.append(result)
        print(f"  Поток {i}: {result:,} операций")
    seq_time = time.time() - start
    print(f"Общее время: {seq_time:.2f}s")
    
    # Тест 2: Параллельно
    print("\n🔸 Параллельное выполнение:")
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(simple_cpu_task) for i in range(4)]
        results = [f.result() for f in futures]
        for i, result in enumerate(results):
            print(f"  Поток {i}: {result:,} операций")
    par_time = time.time() - start
    print(f"Общее время: {par_time:.2f}s")
    
    # Сравнение
    speedup = seq_time / par_time
    print(f"\n📈 Ускорение: {speedup:.2f}x")
    
    if speedup > 2.0:
        print("✅ ПОТОКИ РАБОТАЮТ ПАРАЛЛЕЛЬНО!")
    elif speedup > 1.2:
        print("🔄 ПОТОКИ РАБОТАЮТ, НО НЕ ОПТИМАЛЬНО")
    else:
        print("❌ ПОТОКИ НЕ РАБОТАЮТ ПАРАЛЛЕЛЬНО!")

def test_chudnovsky_worker():
    """Тест worker функции Chudnovsky"""
    print("\n🧪 ТЕСТ WORKER ФУНКЦИИ CHUDNOVSKY")
    print("=" * 50)
    
    try:
        from pi_generator.algorithms.chudnovsky.multi_thread.chudnovsky_binary_splitting import ChudnovskyBinarySplitting
        
        # Создаем простую задачу для worker
        worker = ChudnovskyBinarySplitting._compute_chunk
        
        print("🔹 Тест worker функции:")
        
        # Тестируем с разными параметрами
        test_cases = [
            (0, 0, 10, 100),  # worker_id, start, end, precision
            (1, 5, 10, 100),
            (2, 10, 15, 100),
        ]
        
        results = []
        for case in test_cases:
            start = time.time()
            result = worker(case)
            elapsed = time.time() - start
            results.append((case, result, elapsed))
            print(f"  Worker {case[0]}: {elapsed:.3f}s, результат: {result[0]}")
        
        # Тестируем параллельно
        print("\n🔸 Тест параллельных workers:")
        start = time.time()
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(worker, case) for case in test_cases]
            results = [f.result() for f in futures]
        
        par_time = time.time() - start
        print(f"Параллельное время: {par_time:.3f}s")
        
        # Проверяем результаты
        print(f"Результаты: {[r[0] for r in results]}")
        
        if par_time < 1.0:  # Должно быть быстро
            print("✅ WORKER ФУНКЦИИ РАБОТАЮТ!")
        else:
            print("❌ WORKER ФУНКЦИИ РАБОТАЮТ МЕДЛЕННО!")
            
    except Exception as e:
        print(f"❌ Ошибка теста worker: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_threadpool_executor()
    test_chudnovsky_worker()
