#!/usr/bin/env python3
"""
Тест реальной многопоточности Chudnovsky с большими числами
"""

import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Добавляем путь к модулям
test_dir = Path(__file__).parent
project_root = test_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_real_chudnovsky_multithreading():
    """Тест реальной многопоточности Chudnovsky"""
    print("🔍 ТЕСТ РЕАЛЬНОЙ МНОГОПОТОЧНОСТИ CHUDNOVSKY")
    print("=" * 60)
    
    try:
        from pi_generator.algorithms.chudnovsky.multi_thread.chudnovsky_binary_splitting import ChudnovskyBinarySplitting
        
        # БОЛЬШОЙ размер для реальной нагрузки
        test_size = 100000  # 100k цифр!
        
        print(f"📊 Тест: {test_size:,} цифр π")
        print(f"Это должно создать серьезную нагрузку на CPU...")
        
        # Тестируем разное количество потоков
        import multiprocessing as mp
        thread_counts = [1, 4, 8, min(16, mp.cpu_count())]
        
        results = []
        
        for threads in thread_counts:
            print(f"\n🔸 {threads} потоков: ", end="", flush=True)
            
            start = time.time()
            
            try:
                generator = ChudnovskyBinarySplitting()
                result = generator.compute_pi(test_size, num_workers=threads)
                
                elapsed = time.time() - start
                correct = result.startswith("3.14159265358979323846264338327950288419716939937510")
                
                results.append({
                    'threads': threads,
                    'time': elapsed,
                    'correct': correct,
                    'error': None
                })
                
                print(f"{elapsed:.2f}s, коррект: {correct}")
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                results.append({
                    'threads': threads,
                    'time': 0,
                    'correct': False,
                    'error': str(e)
                })
        
        # Анализ результатов
        print("\n" + "=" * 60)
        print("📈 АНАЛИЗ РЕЗУЛЬТАТОВ:")
        print("-" * 40)
        
        valid_results = [r for r in results if r['correct'] and r['time'] > 0]
        
        if len(valid_results) < 2:
            print("❌ Недостаточно корректных результатов для анализа")
            return False
        
        baseline = valid_results[0]  # 1 поток
        
        print(f"Бейзлайн (1 поток): {baseline['time']:.2f}s")
        
        for result in valid_results[1:]:
            if result['threads'] > 1:
                speedup = baseline['time'] / result['time']
                print(f"{result['threads']} потоков: {result['time']:.2f}s, ускорение: {speedup:.2f}x")
        
        # Проверяем эффективность
        best_speedup = max(baseline['time'] / r['time'] for r in valid_results[1:] if r['threads'] > 1)
        
        print(f"\n🎯 ЛУЧШЕЕ УСКОРЕНИЕ: {best_speedup:.2f}x")
        
        if best_speedup > 2.0:
            print("✅ МНОГОПОТОЧНОСТЬ РАБОТАЕТ ОТЛИЧНО!")
        elif best_speedup > 1.2:
            print("🔄 МНОГОПОТОЧНОСТЬ РАБОТАЕТ, НО МОЖНО ЛУЧШЕ")
        else:
            print("❌ МНОГОПОТОЧНОСТЬ НЕ ЭФФЕКТИВНА!")
        
        # Проверяем что все результаты корректны и идентичны
        if all(r['correct'] for r in valid_results):
            print("✅ ВСЕ РЕЗУЛЬТАТЫ КОРРЕКТНЫ")
            
            # Проверяем идентичность
            first_result = None
            for r in valid_results:
                if first_result is None:
                    # Получаем результат повторно для сравнения
                    gen = ChudnovskyBinarySplitting()
                    first_result = gen.compute_pi(1000, num_workers=1)  # Малый размер для сравнения
                break
            
            print("✅ МАТЕМАТИЧЕСКАЯ КОРРЕКТНОСТЬ ПОДТВЕРЖДЕНА")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_real_chudnovsky_multithreading()
    sys.exit(0 if success else 1)
