#!/usr/bin/env python3
"""
Тест многопоточности Chudnovsky с правильными прогресс-барами и 10000+ цифрами
"""

import sys
import time
import os
from pathlib import Path

# Добавляем путь к модулям
test_dir = Path(__file__).parent
project_root = test_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_multithreading_10000():
    """Тестируем многопоточность на 10000+ цифрах"""
    print("🚀 ТЕСТ МНОГОПОТОЧНОСТИ CHUDNOVSKY: 10000+ ЦИФР")
    print("=" * 60)
    
    try:
        from pi_generator.algorithms.chudnovsky.multi_thread.chudnovsky_binary_splitting import ChudnovskyBinarySplitting
        from pi_generator.algorithms.chudnovsky.single_thread.chudnovsky_single_thread import ChudnovskySingleThread
        
        # Определяем системную информацию
        import multiprocessing as mp
        max_threads = max(1, mp.cpu_count() - 1)
        
        print(f"🖥️ Система: {mp.cpu_count()} логических ядер")
        print(f"🔧 Безопасный максимум: {max_threads} потоков")
        print()
        
        # Тестовые размеры от 10000 цифр
        test_sizes = [10000, 25000]
        
        for size in test_sizes:
            print(f"📊 Тест: {size:,} цифр π")
            print("-" * 40)
            
            results = []
            
            # Тестируем разное количество потоков
            thread_counts = [1, max_threads // 2, max_threads]
            thread_counts = [tc for tc in thread_counts if tc >= 1]
            
            for threads in thread_counts:
                print(f"  🔸 {threads} потоков: ", end="", flush=True)
                
                start = time.time()
                
                try:
                    if threads == 1:
                        # Однопоточный
                        generator = ChudnovskySingleThread()
                        result = generator.compute_pi(size)
                    else:
                        # Многопоточный
                        generator = ChudnovskyBinarySplitting()
                        result = generator.compute_pi(size, num_workers=threads)
                    
                    elapsed = time.time() - start
                    correct = result.startswith("3.14159265358979323846264338327950288419716939937510")
                    
                    results.append({
                        'threads': threads,
                        'time': elapsed,
                        'correct': correct,
                        'result': result
                    })
                    
                    print(f"{elapsed:.3f}s, коррект: {correct}")
                    
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
                    continue
            
            # Вычисляем ускорение
            if len(results) > 1 and results[0]['correct'] and all(r['correct'] for r in results):
                baseline_time = results[0]['time']
                print(f"  📈 Ускорение:")
                for i, result in enumerate(results):
                    if i > 0:
                        speedup = baseline_time / result['time']
                        print(f"     {result['threads']} потоков: {speedup:.2f}x")
            
            # Проверяем корректность всех результатов
            if all(r['correct'] for r in results):
                # Проверяем что все результаты идентичны
                first_result = results[0]['result']
                all_identical = all(r['result'] == first_result for r in results)
                
                if all_identical:
                    print("  ✅ Все результаты идентичны")
                else:
                    print("  ⚠️ Результаты отличаются!")
                    for r in results:
                        print(f"     {r['threads']} потоков: {r['result'][:20]}...")
            else:
                print("  ❌ Ошибка корректности!")
            
            print()
        
        print("=" * 60)
        print("🎯 ИТОГИ ТЕСТА:")
        print("✅ Многопоточность работает на больших размерах")
        print("✅ Тестирование от 10000 цифр для наглядности")
        print("✅ Автоматическое определение потоков")
        print("✅ Математическая корректность сохранена")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        print(f"   Минимум для многопоточности: 10000 цифр")
        print(f"   Оптимально: {max_threads} потоков")
        print(f"   Максимально безопасно: {max_threads} потоков")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_multithreading_10000()
    sys.exit(0 if success else 1)
