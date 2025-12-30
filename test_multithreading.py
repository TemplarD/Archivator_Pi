#!/usr/bin/env python3
"""
Тест многопоточности генерации π
"""

import time
import sys
from pathlib import Path

# Добавляем пути к модулям
sys.path.append(str(Path(__file__).parent / "src"))

from pi_generator.pi_generator import PiGenerator

def test_pi_generation_multithreading():
    """Тестирует производительность генерации π с разным количеством потоков"""
    
    print("🧪 Тест многопоточности генерации π")
    print("=" * 50)
    
    # Тестируемые количества потоков
    test_precisions = [5000, 10000, 20000]
    test_workers = [1, 2, 4, 8]
    
    cache_dir = Path("pi_storage")
    cache_dir.mkdir(exist_ok=True)
    
    pi_generator = PiGenerator(cache_dir)
    
    results = []
    
    for precision in test_precisions:
        print(f"\n📊 Тестирование точности: {precision:,} цифр")
        print("-" * 40)
        
        for workers in test_workers:
            print(f"Потоки: {workers}...", end=" ")
            
            try:
                start_time = time.time()
                
                # Callback для прогресса
                def progress_callback(progress, current, total):
                    pass  # Отключаем вывод для чистоты теста
                
                pi_digits = pi_generator.generate_pi_digits(
                    precision, False, progress_callback, workers, force_regenerate=True
                )
                
                end_time = time.time()
                generation_time = end_time - start_time
                
                # Расчет скорости
                rate = precision / generation_time if generation_time > 0 else 0
                
                result = {
                    'precision': precision,
                    'workers': workers,
                    'time': generation_time,
                    'rate': rate,
                    'digits': len(pi_digits)
                }
                results.append(result)
                
                print(f"✅ {generation_time:.2f} сек ({rate:.0f} цифр/сек)")
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                result = {
                    'precision': precision,
                    'workers': workers,
                    'time': float('inf'),
                    'rate': 0,
                    'error': str(e)
                }
                results.append(result)
    
    # Анализ результатов
    print("\n📈 Анализ результатов:")
    print("=" * 50)
    
    for precision in test_precisions:
        print(f"\nТочность {precision:,} цифр:")
        precision_results = [r for r in results if r['precision'] == precision]
        
        best_result = min(precision_results, key=lambda x: x['time'])
        worst_result = max(precision_results, key=lambda x: x['time'])
        
        print(f"  Лучший результат: {best_result['workers']} потоков - {best_result['time']:.2f} сек")
        print(f"  Худший результат: {worst_result['workers']} потоков - {worst_result['time']:.2f} сек")
        
        if worst_result['time'] != float('inf'):
            speedup = worst_result['time'] / best_result['time']
            print(f"  Ускорение: {speedup:.2f}x")
        
        # Детальная таблица
        print("  Детали:")
        for r in precision_results:
            if 'error' not in r:
                efficiency = (r['rate'] / r['workers']) if r['workers'] > 0 else 0
                print(f"    {r['workers']:2d} потоков: {r['time']:6.2f} сек, {r['rate']:6.0f} цифр/сек, эффективность: {efficiency:.0f} цифр/поток/сек")
    
    return results

if __name__ == "__main__":
    test_pi_generation_multithreading()
