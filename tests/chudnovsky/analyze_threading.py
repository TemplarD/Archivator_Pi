#!/usr/bin/env python3
"""
Анализ проблемы с потоками
"""

import sys
import threading
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Добавляем путь к модулям
test_dir = Path(__file__).parent
project_root = test_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

def analyze_threading_issue():
    """Анализируем проблему с потоками"""
    print("🔍 АНАЛИЗ ПРОБЛЕМЫ С ПОТОКАМИ")
    print("=" * 60)
    
    # Тестируем количество потоков
    active_threads = []
    
    def thread_monitor():
        """Монитор активных потоков"""
        while True:
            count = threading.active_count()
            active_threads.append(count)
            time.sleep(0.1)
    
    # Запускаем монитор
    monitor_thread = threading.Thread(target=thread_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    print("🔹 Тест 1: ThreadPoolExecutor с 8 потоками")
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        # Создаем задачи которые нагружают CPU
        def cpu_task():
            end = time.time() + 1
            result = 0
            while time.time() < end:
                result += sum(i**2 for i in range(1000))
            return result
        
        # Отправляем задачи
        futures = [executor.submit(cpu_task) for _ in range(16)]  # 16 задач для 8 потоков
        
        # Ждем завершения
        results = [f.result() for f in futures]
    
    elapsed = time.time() - start
    max_threads = max(active_threads) if active_threads else 0
    
    print(f"Время: {elapsed:.2f}s")
    print(f"Максимум потоков: {max_threads}")
    print(f"Ожидаемое: 8 (worker) + 1 (main) + 1 (monitor) = 10")
    
    # Анализ
    if max_threads < 8:
        print("❌ НЕДОСТАТОЧНО ПОТОКОВ СОЗДАЕТСЯ!")
    elif max_threads > 15:
        print("⚠️ СЛИШКОМ МНОГО ПОТОКОВ СОЗДАЕТСЯ!")
    else:
        print("✅ КОЛИЧЕСТВО ПОТОКОВ КОРРЕКТНОЕ")
    
    print("\n🔸 Тест 2: Прямая проверка Chudnovsky")
    
    try:
        from pi_generator.algorithms.chudnovsky.multi_thread.chudnovsky_binary_splitting import ChudnovskyBinarySplitting
        
        # Сбрасываем монитор
        active_threads.clear()
        
        print("Запускаем Chudnovsky с 8 потоками...")
        start = time.time()
        
        generator = ChudnovskyBinarySplitting()
        result = generator.compute_pi(5000, num_workers=8)  # Малый размер для быстрого теста
        
        elapsed = time.time() - start
        max_threads = max(active_threads) if active_threads else 0
        
        print(f"Время: {elapsed:.2f}s")
        print(f"Максимум потоков: {max_threads}")
        print(f"Корректность: {result.startswith('3.14159265358979323846264338327950288419716939937510')}")
        
        # Выводы
        print(f"\n💡 ВЫВОДЫ:")
        if max_threads < 8:
            print("❌ ПРОБЛЕМА: ThreadPoolExecutor создает недостаточно потоков")
            print("   Возможная причина: GIL или неправильная конфигурация")
        elif max_threads == 8:
            print("✅ ThreadPoolExecutor создает правильное количество потоков")
            print("   Проблема может быть в worker функции или GIL")
        else:
            print("⚠️ ThreadPoolExecutor создает больше потоков чем нужно")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    analyze_threading_issue()
