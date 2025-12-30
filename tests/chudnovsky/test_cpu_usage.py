#!/usr/bin/env python3
"""
Тест многопоточности Chudnovsky с мониторингом CPU
"""

import sys
import time
from pathlib import Path

# Добавляем путь к модулям
test_dir = Path(__file__).parent
project_root = test_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_chudnovsky_cpu_usage():
    """Тестируем загрузку CPU при многопоточности Chudnovsky"""
    print("🔍 ТЕСТ ЗАГРУЗКИ CPU: CHUDNOVSKY МНОГОПОТОЧНОСТЬ")
    print("=" * 60)
    
    try:
        from pi_generator.algorithms.chudnovsky.multi_thread.chudnovsky_binary_splitting import ChudnovskyBinarySplitting
        from pi_generator.algorithms.chudnovsky.single_thread.chudnovsky_single_thread import ChudnovskySingleThread
        from utils.cpu_monitor import CPUMonitor
        
        # Определяем количество потоков
        import multiprocessing as mp
        max_threads = min(8, max(1, mp.cpu_count() - 1))
        
        print(f"🖥️ Система: {mp.cpu_count()} логических ядер")
        print(f"🔧 Тестовое количество потоков: {max_threads}")
        print()
        
        # Тестовый размер - достаточно большой для многопоточности
        test_size = 25000
        
        results = []
        
        # Тест 1: Однопоточный
        print(f"📊 Тест 1: 1 поток, {test_size:,} цифр")
        print("-" * 40)
        
        monitor = CPUMonitor()
        monitor.start_monitoring(1)
        
        start = time.time()
        generator = ChudnovskySingleThread()
        result = generator.compute_pi(test_size)
        elapsed = time.time() - start
        
        stats = monitor.stop_monitoring()
        monitor.print_stats(stats)
        
        correct = result.startswith("3.14159265358979323846264338327950288419716939937510")
        
        results.append({
            'threads': 1,
            'time': elapsed,
            'correct': correct,
            'cpu_stats': stats
        })
        
        print(f"Результат: {elapsed:.3f}s, коррект: {correct}")
        
        # Тест 2: Многопоточный
        print(f"\n📊 Тест 2: {max_threads} потоков, {test_size:,} цифр")
        print("-" * 40)
        
        monitor = CPUMonitor()
        monitor.start_monitoring(max_threads)
        
        start = time.time()
        generator = ChudnovskyBinarySplitting()
        result = generator.compute_pi(test_size, num_workers=max_threads)
        elapsed = time.time() - start
        
        stats = monitor.stop_monitoring()
        monitor.print_stats(stats)
        
        correct = result.startswith("3.14159265358979323846264338327950288419716939937510")
        
        results.append({
            'threads': max_threads,
            'time': elapsed,
            'correct': correct,
            'cpu_stats': stats
        })
        
        print(f"Результат: {elapsed:.3f}s, коррект: {correct}")
        
        # Сравнение результатов
        print("\n" + "=" * 60)
        print("📈 СРАВНЕНИЕ РЕЗУЛЬТАТОВ:")
        print("-" * 40)
        
        for result in results:
            stats = result['cpu_stats']
            print(f"{result['threads']} потоков:")
            print(f"  Время: {result['time']:.3f}s")
            print(f"  CPU: {stats['avg_cpu_usage']:.1f}% (сред), {stats['max_cpu_usage']:.1f}% (макс)")
            print(f"  Корректность: {result['correct']}")
        
        # Анализ эффективности
        if len(results) == 2 and all(r['correct'] for r in results):
            single = results[0]
            multi = results[1]
            
            speedup = single['time'] / multi['time']
            cpu_efficiency = multi['cpu_stats']['avg_cpu_usage'] / single['cpu_stats']['avg_cpu_usage']
            
            print(f"\n🎯 АНАЛИЗ ЭФФЕКТИВНОСТИ:")
            print(f"Ускорение времени: {speedup:.2f}x")
            print(f"Эффективность CPU: {cpu_efficiency:.2f}x")
            
            if speedup > 1.2 and cpu_efficiency > 2.0:
                print("✅ МНОГОПОТОЧНОСТЬ РАБОТАЕТ ЭФФЕКТИВНО!")
            elif speedup > 1.0:
                print("🔄 МНОГОПОТОЧНОСТЬ РАБОТАЕТ, НО МОЖНО ЛУЧШЕ")
            else:
                print("❌ МНОГОПОТОЧНОСТЬ НЕ РАБОТАЕТ КОРРЕКТНО!")
                
            # Проверка загрузки CPU
            if multi['cpu_stats']['avg_cpu_usage'] < 50:
                print("⚠️ НИЗКАЯ ЗАГРУЗКА CPU - потоки не работают параллельно!")
            elif multi['cpu_stats']['avg_cpu_usage'] > 80:
                print("✅ ХОРОШАЯ ЗАГРУЗКА CPU - потоки работают параллельно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chudnovsky_cpu_usage()
    sys.exit(0 if success else 1)
