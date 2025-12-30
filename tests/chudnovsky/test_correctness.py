#!/usr/bin/env python3
"""
Тест корректности алгоритмов Chudnovsky
"""

import sys
import time
from pathlib import Path

# Добавляем путь к модулям
test_dir = Path(__file__).parent
project_root = test_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_chudnovsky_correctness():
    """Тестируем корректность всех алгоритмов Chudnovsky"""
    print("🧪 ТЕСТ КОРРЕКТНОСТИ ALGORITHMS CHUDNOVSKY")
    print("=" * 60)
    
    # Правильные первые 50 цифр π
    CORRECT_PI_50 = "3.14159265358979323846264338327950288419716939937510"
    
    try:
        from pi_generator.algorithms.chudnovsky.single_thread.chudnovsky_single_thread import ChudnovskySingleThread
        from pi_generator.algorithms.chudnovsky.multi_thread.chudnovsky_binary_splitting import ChudnovskyBinarySplitting
        
        # Тестовые размеры
        test_sizes = [100, 1000, 5000]
        
        all_passed = True
        
        for size in test_sizes:
            print(f"\n📊 Тест корректности: {size} цифр")
            print("-" * 40)
            
            # Однопоточный
            print("  🔹 Однопоточный: ", end="", flush=True)
            start = time.time()
            single = ChudnovskySingleThread()
            result_single = single.compute_pi(size)
            time_single = time.time() - start
            correct_single = result_single.startswith(CORRECT_PI_50)
            print(f"{time_single:.3f}s, коррект: {correct_single}")
            
            # Многопоточный (разное количество потоков)
            import multiprocessing as mp
            max_threads = min(4, max(1, mp.cpu_count() - 1))
            
            for threads in [2, max_threads]:
                print(f"  🔸 {threads} потоков: ", end="", flush=True)
                start = time.time()
                multi = ChudnovskyBinarySplitting()
                result_multi = multi.compute_pi(size, num_workers=threads)
                time_multi = time.time() - start
                correct_multi = result_multi.startswith(CORRECT_PI_50)
                print(f"{time_multi:.3f}s, коррект: {correct_multi}")
                
                # Проверяем идентичность результатов
                if correct_single and correct_multi:
                    if result_single == result_multi:
                        print(f"    ✅ Результаты идентичны")
                    else:
                        print(f"    ⚠️ Результаты отличаются!")
                        print(f"       Single: {result_single[:30]}...")
                        print(f"       Multi:  {result_multi[:30]}...")
                        all_passed = False
                else:
                    all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 ВСЕ ТЕСТЫ КОРРЕКТНОСТИ ПРОЙДЕНЫ!")
            print("✅ Однопоточный алгоритм корректен")
            print("✅ Многопоточный алгоритм корректен")
            print("✅ Результаты идентичны")
        else:
            print("❌ ОБНАРУЖЕНЫ ОШИБКИ КОРРЕКТНОСТИ!")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chudnovsky_correctness()
    sys.exit(0 if success else 1)
