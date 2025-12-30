#!/usr/bin/env python3
"""
Тест интенсивной нагрузки CPU в worker функции
"""

import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Добавляем путь к модулям
test_dir = Path(__file__).parent
project_root = test_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

def cpu_intensive_task(k):
    """Интенсивная CPU задача для теста"""
    # Искусственная интенсивная нагрузка
    result = 0
    for i in range(100000):  # 100k итераций для нагрузки
        result += (i * k) ** 2 + (i + k) ** 3
    return result

def test_cpu_intensive_workers():
    """Тестируем интенсивную нагрузку CPU"""
    print("🔥 ТЕСТ ИНТЕНСИВНОЙ НАГРУЗКИ CPU")
    print("=" * 50)
    
    # Тестируем разное количество потоков
    thread_counts = [1, 4, 8]
    
    for threads in thread_counts:
        print(f"\n🔸 {threads} потоков: ", end="", flush=True)
        
        start = time.time()
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # Создаем интенсивные задачи
            tasks = range(threads * 10)  # 10 задач на поток
            futures = [executor.submit(cpu_intensive_task, i) for i in tasks]
            
            # Ждем завершения
            results = [f.result() for f in futures]
        
        elapsed = time.time() - start
        print(f"{elapsed:.2f}s")
    
    print("\n✅ Если потоки работают, время должно уменьшаться")

def test_decimal_performance():
    """Тестируем производительность Decimal операций"""
    print("\n🧪 ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ DECIMAL")
    print("=" * 50)
    
    from decimal import Decimal, getcontext
    getcontext().prec = 50
    
    # Тестируем разные операции
    test_cases = [
        ("Простое умножение", lambda: Decimal(12345) * Decimal(67890)),
        ("Цикл умножений", lambda: 
            sum(Decimal(i) * Decimal(j) for i in range(100) for j in range(100))
        ),
        ("Степени", lambda: sum(Decimal(i) ** 3 for i in range(1000))),
    ]
    
    for name, func in test_cases:
        print(f"\n🔹 {name}: ", end="", flush=True)
        
        start = time.time()
        result = func()
        elapsed = time.time() - start
        
        print(f"{elapsed:.3f}s")

def test_current_worker():
    """Тестируем текущую worker функцию на нагрузку"""
    print("\n🔍 ТЕСТ ТЕКУЩЕЙ WORKER ФУНКЦИИ")
    print("=" * 50)
    
    try:
        from pi_generator.algorithms.chudnovsky.multi_thread.chudnovsky_binary_splitting import ChudnovskyBinarySplitting
        
        # Тестируем worker функцию напрямую
        worker = ChudnovskyBinarySplitting._compute_chunk
        
        print("🔹 Тест worker с k=100:")
        start = time.time()
        result = worker((0, 0, 100, 100))  # worker_id, start, end, precision
        elapsed = time.time() - start
        print(f"Время: {elapsed:.3f}s, результат: {result[0]}")
        
        print("🔹 Тест worker с k=1000:")
        start = time.time()
        result = worker((0, 0, 1000, 100))
        elapsed = time.time() - start
        print(f"Время: {elapsed:.3f}s, результат: {result[0]}")
        
        print("🔹 Тест worker с k=5000:")
        start = time.time()
        result = worker((0, 0, 5000, 100))
        elapsed = time.time() - start
        print(f"Время: {elapsed:.3f}s, результат: {result[0]}")
        
        print("\n💡 АНАЛИЗ:")
        print("Если время растет линейно с k - worker работает")
        print("Если время почти не меняется - worker не нагружает CPU")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_cpu_intensive_workers()
    test_decimal_performance()
    test_current_worker()
