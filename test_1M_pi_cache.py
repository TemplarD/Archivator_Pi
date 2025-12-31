#!/usr/bin/env python3
"""
Тест сжатия на 1,000,000 цифр π из кеша
Максимальная производительность с C++ и многопоточным поиском
"""

import sys
import os
import time
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.compression.compression_core import CompressionCore

# Импортируем новую C++ систему
try:
    # Добавляем путь к скомпилированному модулю
    sys.path.append(str(Path(__file__).parent / "src" / "cpp_core" / "build"))
    from pi_core import PiCalculator
    CPP_AVAILABLE = True
    print("🚀 Используется C++ система генерации π")
except ImportError as e:
    print(f"⚠️ Ошибка импорта C++ модуля: {e}")
    # Fallback к старой системе
    from src.pi_generator import PiGenerator
    CPP_AVAILABLE = False
    print("⚠️ Fallback к Python системе генерации π")

def test_compression_1M_pi():
    """Тест сжатия с 1M цифр π из кеша"""
    print("🧪 ТЕСТ СЖАТИЯ НА 1,000,000 ЦИФР π ИЗ КЕША")
    print("=" * 60)
    
    # Загружаем π из кеша
    pi_cache_file = Path(__file__).parent / "src" / "cpp_core" / "build" / "pi_1M_digits.txt"
    
    if not pi_cache_file.exists():
        print(f"❌ Файл с 1M цифр π не найден: {pi_cache_file}")
        return None
    
    print(f"📁 Загружаем π из кеша: {pi_cache_file}")
    print(f"📊 Размер файла: {pi_cache_file.stat().st_size:,} байт")
    
    with open(pi_cache_file, 'r', encoding='utf-8') as f:
        pi_digits = f.read().strip()
    
    # Убираем "3." в начале если есть
    if pi_digits.startswith("3."):
        pi_digits = pi_digits[2:]  # Пропускаем "3."
        print(f"🔧 Убрали '3.', осталось {len(pi_digits):,} цифр")
    
    print(f"📈 Получено {len(pi_digits):,} цифр π")
    
    # Создаем компрессор с максимальной производительностью
    compressor = CompressionCore(
        pi_generator=None,  # Не нужен генератор, используем кеш
        backup_enabled=True,
        adaptive_search=False,  # Отключаем адаптивный поиск, используем многопоточный
        enable_logging=True,
        multithreaded_search=True,
        search_threads=31  # 39-1=31 потоков для поиска
    )
    
    # Тестовые данные разного размера для проверки на 1M π
    test_cases = [
        {
            'name': 'Маленький текстовый файл',
            'data': b"This is a test message for Pi-Archiver compression system with 1M digits of pi. " * 5,
            'file': 'test_small_1M.txt'
        },
        {
            'name': 'Средний текстовый файл',
            'data': b"Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 20,
            'file': 'test_medium_1M.txt'
        },
        {
            'name': 'Большой текстовый файл',
            'data': b"Pi-Archiver Ultra compression test with large text data. " * 50,
            'file': 'test_large_1M.txt'
        },
        {
            'name': 'Бинарные данные с паттернами',
            'data': bytes(range(256)) * 20 + b"Pattern data for testing compression efficiency. " * 10,
            'file': 'test_binary_1M.bin'
        },
        {
            'name': 'Смешанные данные',
            'data': b"Header: " + bytes(range(100)) + b"Middle:" + os.urandom(500) + b"End: " + b"Footer data",
            'file': 'test_mixed_1M.mix'
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🔸 Тест {i+1}: {test_case['name']}")
        print(f"   Размер: {len(test_case['data']):,} байт")
        
        # Сжимаем данные с диапазоном 1-48 байт
        start_time = time.time()
        blocks, stats = compressor.compress_data(
            data=test_case['data'],
            pi_digits=pi_digits,
            block_size_range=(1, 48),  # Максимальный диапазон
            output_file=test_case['file']
        )
        compress_time = time.time() - start_time
        
        # Восстанавливаем данные
        start_time = time.time()
        recovered_data = compressor.decompress_data(
            blocks=blocks,
            pi_digits=pi_digits,
            original_size=len(test_case['data']),
            xor_key=0x3F
        )
        recover_time = time.time() - start_time
        
        # Проверяем целостность
        integrity_ok = recovered_data == test_case['data']
        
        # Сохраняем результаты
        result = {
            'name': test_case['name'],
            'original_size': len(test_case['data']),
            'compressed_size': stats.compressed_size,
            'compression_ratio': stats.compression_ratio,
            'blocks_found': stats.blocks_found,
            'blocks_total': stats.blocks_total,
            'backup_blocks_used': stats.backup_blocks_used,
            'compress_time': compress_time,
            'recover_time': recover_time,
            'integrity': integrity_ok,
            'session_id': stats.session_id,
            'pi_digits_used': len(pi_digits)
        }
        results.append(result)
        
        # Выводим результаты
        print(f"   📈 Коэффициент сжатия: {stats.compression_ratio:.2f}x")
        print(f"   🔍 Найдено блоков: {stats.blocks_found}/{stats.blocks_total} ({stats.blocks_found/stats.blocks_total:.1%})")
        print(f"   💾 Бэкапов использовано: {stats.backup_blocks_used}")
        print(f"   ⏱️ Время сжатия: {compress_time:.3f} сек")
        print(f"   ⏱️ Время восстановления: {recover_time:.3f} сек")
        print(f"   ✅ Целостность: {'OK' if integrity_ok else 'FAILED'}")
        
        if stats.session_id:
            print(f"   📝 Лог сохранен: logs/{stats.session_id}.json")
    
    # Общая статистика
    print(f"\n📊 ОБЩАЯ СТАТИСТИКА ТЕСТОВ НА 1M ЦИФР π")
    print("=" * 50)
    
    total_original = sum(r['original_size'] for r in results)
    total_compressed = sum(r['compressed_size'] for r in results)
    total_blocks_found = sum(r['blocks_found'] for r in results)
    total_blocks = sum(r['blocks_total'] for r in results)
    total_backups = sum(r['backup_blocks_used'] for r in results)
    
    avg_compression = total_original / total_compressed if total_compressed > 0 else 0
    avg_success_rate = total_blocks_found / total_blocks if total_blocks > 0 else 0
    
    print(f"📦 Общий исходный размер: {total_original:,} байт")
    print(f"📦 Общий сжатый размер: {total_compressed:,} байт")
    print(f"📈 Средний коэффициент сжатия: {avg_compression:.2f}x")
    print(f"🔍 Общая успешность поиска: {avg_success_rate:.1%}")
    print(f"💾 Всего бэкапов использовано: {total_backups}")
    print(f"📊 Использовано цифр π: {results[0]['pi_digits_used']:,}")
    
    # Проверка целостности всех тестов
    all_integrity_ok = all(r['integrity'] for r in results)
    print(f"✅ Целостность всех данных: {'OK' if all_integrity_ok else 'FAILED'}")
    
    # Производительность
    total_time = sum(r['compress_time'] for r in results)
    throughput = total_original / total_time if total_time > 0 else 0
    print(f"⚡ Общая производительность: {throughput:.0f} байт/сек")
    
    return results

if __name__ == "__main__":
    try:
        # Создаем директорию для логов
        Path("logs").mkdir(exist_ok=True)
        
        # Запускаем тест
        results = test_compression_1M_pi()
        
        print(f"\n🎉 ТЕСТ НА 1M ЦИФР π ЗАВЕРШЕН!")
        
        # Дополнительная статистика
        if results:
            print(f"\n📈 ДЕТАЛЬНАЯ СТАТИСТИКА:")
            for result in results:
                print(f"   {result['name']}: {result['compression_ratio']:.2f}x сжатие, "
                      f"{result['blocks_found']}/{result['blocks_total']} блоков найдено")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
