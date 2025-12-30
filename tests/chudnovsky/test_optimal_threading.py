#!/usr/bin/env python3
"""
Оптимальный тест многопоточности Chudnovsky
"""

import sys
import time
from pathlib import Path

# Добавляем путь к модулям
test_dir = Path(__file__).parent
project_root = test_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_optimal_threading():
    """Тестируем оптимальное количество потоков"""
    print("🎯 ОПТИМАЛЬНЫЙ ТЕСТ МНОГОПОТОЧНОСТИ")
    print("=" * 60)
    
    try:
        from pi_generator.algorithms.chudnovsky.multi_thread.chudnovsky_binary_splitting import ChudnovskyBinarySplitting
        from pi_generator.algorithms.chudnovsky.single_thread.chudnovsky_single_thread import ChudnovskySingleThread
        
        # Определяем оптимальное количество потоков
        import multiprocessing as mp
        cpu_cores = mp.cpu_count()
        optimal_threads = min(cpu_cores // 2, 8)  # Половина ядер или 8
        
        print(f"🖥️ Система: {cpu_cores} логических ядер")
        print(f"🎯 Оптимально: {optimal_threads} потоков")
        print()
        
        # Тестовый размер
        test_size = 15000
        
        results = []
        
        # Тестируем оптимальные количества потоков
        thread_counts = [1, 2, 4, optimal_threads]
        
        for threads in thread_counts:
            print(f"🔸 {threads} потоков: ", end="", flush=True)
            
            start = time.time()
            
            try:
                if threads == 1:
                    generator = ChudnovskySingleThread()
                    result = generator.compute_pi(test_size)
                else:
                    generator = ChudnovskyBinarySplitting()
                    result = generator.compute_pi(test_size, num_workers=threads)
                
                elapsed = time.time() - start
                correct = result.startswith("3.14159265358979323846264338327950288419716939937510")
                
                results.append({
                    'threads': threads,
                    'time': elapsed,
                    'correct': correct
                })
                
                print(f"{elapsed:.2f}s, коррект: {correct}")
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                continue
        
        # Анализ результатов
        print("\n" + "=" * 60)
        print("📈 АНАЛИЗ ОПТИМАЛЬНОГО КОЛИЧЕСТВА ПОТОКОВ:")
        print("-" * 50)
        
        if len(results) < 2:
            print("❌ Недостаточно результатов для анализа")
            return False
        
        baseline = results[0]  # 1 поток
        best_result = min(results[1:], key=lambda x: x['time'])  # Лучший многопоточный
        
        print(f"Бейзлайн (1 поток): {baseline['time']:.2f}s")
        
        for result in results[1:]:
            if result['correct']:
                speedup = baseline['time'] / result['time']
                efficiency = speedup / result['threads'] * 100
                
                print(f"{result['threads']} потоков: {result['time']:.2f}s, "
                      f"ускорение: {speedup:.2f}x, эффективность: {efficiency:.1f}%")
        
        # Находим оптимальное количество потоков
        best_speedup = baseline['time'] / best_result['time']
        best_efficiency = best_speedup / best_result['threads'] * 100
        
        print(f"\n🎯 ОПТИМАЛЬНО: {best_result['threads']} потоков")
        print(f"Ускорение: {best_speedup:.2f}x")
        print(f"Эффективность: {best_efficiency:.1f}%")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        if best_speedup > 1.5:
            print("✅ Многопоточность ЭФФЕКТИВНА!")
            print(f"   Используйте {best_result['threads']} потоков для максимальной производительности")
        elif best_speedup > 1.1:
            print("🔄 Многопоточность РАБОТАЕТ")
            print(f"   Используйте {best_result['threads']} потоков для умеренного ускорения")
        else:
            print("⚠️ Многопоточность НЕ ЭФФЕКТИВНА")
            print("   Используйте однопоточный режим для данной задачи")
        
        # Общие рекомендации
        print(f"\n📊 ОБЩИЕ РЕКОМЕНДАЦИИ:")
        print(f"   Для {cpu_cores} ядер: оптимально {optimal_threads} потоков")
        print(f"   Минимальный размер для многопоточности: 10000+ цифр")
        print(f"   Максимальное ускорение: ~{optimal_threads:.0f}x (теоретически)")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_optimal_threading()
    sys.exit(0 if success else 1)
