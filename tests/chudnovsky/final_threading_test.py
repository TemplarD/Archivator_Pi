#!/usr/bin/env python3
"""
Финальный тест многопоточности с правильным размером
"""

import sys
import time
import threading
from pathlib import Path

# Добавляем путь к модулям
test_dir = Path(__file__).parent
project_root = test_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

def final_threading_test():
    """Финальный тест многопоточности"""
    print("🎯 ФИНАЛЬНЫЙ ТЕСТ МНОГОПОТОЧНОСТИ")
    print("=" * 60)
    
    try:
        from pi_generator.algorithms.chudnovsky.multi_thread.chudnovsky_binary_splitting import ChudnovskyBinarySplitting
        from pi_generator.algorithms.chudnovsky.single_thread.chudnovsky_single_thread import ChudnovskySingleThread
        
        # ПРАВИЛЬНЫЙ размер для многопоточности
        test_size = 15000  # > 10000 для включения многопоточности
        
        print(f"📊 Тест: {test_size:,} цифр π")
        print(f"🔧 Размер > 10000, многопоточность должна работать")
        print()
        
        # Мониторинг потоков
        active_threads = []
        
        def thread_monitor():
            while True:
                active_threads.append(threading.active_count())
                time.sleep(0.1)
        
        monitor_thread = threading.Thread(target=thread_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Тестируем 1 поток
        print("🔹 1 поток: ", end="", flush=True)
        start = time.time()
        active_threads.clear()
        
        generator = ChudnovskySingleThread()
        result = generator.compute_pi(test_size)
        
        elapsed_single = time.time() - start
        max_threads_single = max(active_threads) if active_threads else 0
        correct_single = result.startswith("3.14159265358979323846264338327950288419716939937510")
        
        print(f"{elapsed_single:.2f}s, потоки: {max_threads_single}, коррект: {correct_single}")
        
        # Тестируем 8 потоков
        print("🔸 8 потоков: ", end="", flush=True)
        start = time.time()
        active_threads.clear()
        
        generator = ChudnovskyBinarySplitting()
        result = generator.compute_pi(test_size, num_workers=8)
        
        elapsed_multi = time.time() - start
        max_threads_multi = max(active_threads) if active_threads else 0
        correct_multi = result.startswith("3.14159265358979323846264338327950288419716939937510")
        
        print(f"{elapsed_multi:.2f}s, потоки: {max_threads_multi}, коррект: {correct_multi}")
        
        # Анализ
        print("\n" + "=" * 60)
        print("📈 АНАЛИЗ РЕЗУЛЬТАТОВ:")
        print("-" * 40)
        
        print(f"1 поток:  {elapsed_single:.2f}s, активных потоков: {max_threads_single}")
        print(f"8 потоков: {elapsed_multi:.2f}s, активных потоков: {max_threads_multi}")
        
        if correct_single and correct_multi:
            speedup = elapsed_single / elapsed_multi
            print(f"Ускорение: {speedup:.2f}x")
            
            # Анализ потоков
            print(f"\n🔍 АНАЛИЗ ПОТОКОВ:")
            if max_threads_multi >= 8:
                print("✅ Многопоточность РАБОТАЕТ!")
                print("   8+ потоков создаются и работают")
            elif max_threads_multi >= 4:
                print("🔄 Многопоточность ЧАСТИЧНО работает")
                print("   Создаются потоки, но не все 8")
            else:
                print("❌ Многопоточность НЕ работает!")
                print("   Потоки не создаются или не работают")
            
            # Анализ ускорения
            if speedup > 2.0:
                print("✅ ОТЛИЧНОЕ УСКОРЕНИЕ!")
            elif speedup > 1.2:
                print("🔄 ХОРОШЕЕ УСКОРЕНИЕ!")
            elif speedup > 1.0:
                print("📊 МИНИМАЛЬНОЕ УСКОРЕНИЕ!")
            else:
                print("❌ НЕТ УСКОРЕНИЯ!")
        
        else:
            print("❌ ОШИБКА КОРРЕКТНОСТИ!")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = final_threading_test()
    sys.exit(0 if success else 1)
