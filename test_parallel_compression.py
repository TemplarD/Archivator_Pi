#!/usr/bin/env python3
"""
Тест многопоточного сжатия с рабочим прогресс-баром
"""

import sys
import time
import os
sys.path.append('src')

from compression.compression_core import CompressionCore
from pi_generator.algorithms.single_thread import ChudnovskySingleThread

def test_parallel_compression():
    """Тест многопоточного сжатия с готовыми π"""
    
    print("🧪 Тест многопоточного сжатия")
    print("=" * 60)
    
    # Создаем тестовые данные
    test_data = b"Hello, World! " * 10000  # ~140KB данных
    print(f"Тестовые данные: {len(test_data):,} байт")
    
    # Используем готовые π из файла
    print("\n📊 Загрузка π из файла...")
    try:
        with open('pi_storage/pi_1000000_digits.txt', 'r') as f:
            pi_digits = f.read().strip()
        pi_digits = pi_digits.replace('.', '').replace('\n', '')  # Убираем точки и переносы
        print(f"Используем {len(pi_digits):,} цифр π из файла")
    except FileNotFoundError:
        print("Файл с π не найден, используем короткие π")
        pi_digits = "1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"
        print(f"Используем {len(pi_digits)} цифр π")
    except Exception as e:
        print(f"Ошибка загрузки π: {e}")
        return
    
    # Создаем компрессор (без генератора, т.к. он не нужен для сжатия)
    compressor = CompressionCore(None)
    
    # Тестируем разное количество потоков
    results = []
    
    for workers in [1, 2, 4]:
        print(f"\n{'='*60}")
        print(f"📊 Тест сжатия с {workers} поток(ами)")
        print(f"{'='*60}")
        
        try:
            # Запускаем сжатие - здесь будет использоваться рабочий прогресс-бар
            start_time = time.time()
            compressed_blocks, stats = compressor.compress_data_parallel(
                test_data, 
                pi_digits,
                num_workers=workers
            )
            elapsed = time.time() - start_time
            
            # Сохраняем результаты
            results.append({
                'workers': workers,
                'time': elapsed,
                'blocks': len(compressed_blocks),
                'compression_ratio': len(test_data) / sum(len(block.encoded_data) for block in compressed_blocks) if compressed_blocks else 1,
                'stats': stats
            })
            
            # Выводим результаты
            print(f"\n📈 Результаты:")
            print(f"  Время: {elapsed:.3f} сек")
            print(f"  Найдено блоков: {len(compressed_blocks)}")
            if compressed_blocks:
                compressed_size = sum(len(block.encoded_data) for block in compressed_blocks)
                ratio = len(test_data) / compressed_size
                print(f"  Размер до: {len(test_data):,} байт")
                print(f"  Размер после: {compressed_size:,} байт")
                print(f"  Коэффициент сжатия: {ratio:.2f}x")
            
            if stats:
                print(f"\n📊 Статистика:")
                print(f"  Блоков найдено: {stats.get('blocks_found', 0)}")
                print(f"  Блоков пропущено: {stats.get('blocks_skipped', 0)}")
                print(f"  Средняя позиция: {stats.get('avg_position', 0):.0f}")
                print(f"  Эффективность поиска: {stats.get('search_efficiency', 0):.1f}%")
            
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            results.append({
                'workers': workers,
                'time': float('inf'),
                'blocks': 0,
                'compression_ratio': 1,
                'error': str(e)
            })
    
    # Анализ результатов
    if results:
        print(f"\n{'='*60}")
        print("📊 Сводная таблица результатов")
        print(f"{'='*60}")
        
        print("Потоки | Время (с) | Блоков | Сжатие | Статус")
        print("-" * 45)
        
        baseline_time = results[0]['time']
        
        for result in results:
            workers = result['workers']
            time_elapsed = result['time']
            blocks = result['blocks']
            ratio = result['compression_ratio']
            status = '✅' if 'error' not in result else '❌'
            
            if time_elapsed != float('inf'):
                speedup = baseline_time / time_elapsed
                print(f"{workers:6} | {time_elapsed:8.3f} | {blocks:6} | {ratio:5.2f}x | {status}")
            else:
                print(f"{workers:6} | {'ошибка':>8} | {blocks:6} | {ratio:5.2f}x | {status}")
        
        # Выводы
        print(f"\n🎯 Выводы:")
        
        # Находим лучший по скорости
        valid_results = [r for r in results if r['time'] != float('inf')]
        if valid_results:
            best_speed = min(valid_results, key=lambda x: x['time'])
            print(f"  Лучшее время: {best_speed['workers']} потоков ({best_speed['time']:.3f} сек)")
            
            # Анализ ускорения
            if len(valid_results) > 1:
                print(f"\n🔍 Анализ ускорения:")
                for result in valid_results:
                    workers = result['workers']
                    time_elapsed = result['time']
                    speedup = baseline_time / time_elapsed
                    
                    if speedup > 1.5:
                        print(f"  {workers} потоков: Отличное ускорение ({speedup:.2f}x)")
                    elif speedup > 1.1:
                        print(f"  {workers} потоков: Хорошее ускорение ({speedup:.2f}x)")
                    elif speedup > 0.9:
                        print(f"  {workers} потоков: Небольшое ускорение ({speedup:.2f}x)")
                    else:
                        print(f"  {workers} потоков: Замедление ({speedup:.2f}x)")

if __name__ == "__main__":
    test_parallel_compression()
