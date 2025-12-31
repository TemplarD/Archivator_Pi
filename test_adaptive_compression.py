#!/usr/bin/env python3
"""
Тест новой системы сжатия с адаптивным поиском и резервным копированием
ИСПОЛЬЗУЕТ НОВУЮ C++ СИСТЕМУ ГЕНЕРАЦИИ π
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

def get_pi_generator():
    """Возвращает генератор π (C++ или Python)"""
    if CPP_AVAILABLE:
        return PiCalculator()
    else:
        return PiGenerator()

def generate_pi_digits(generator, count: int) -> str:
    """Генерирует цифры π с использованием C++ или Python"""
    if CPP_AVAILABLE:
        # Используем C++ систему с адаптивным выбором потоков
        print(f"📊 Генерация {count:,} цифр π с помощью C++...")
        result = generator.compute_pi_adaptive(0)  # Автоматический выбор потоков
        # Возвращаем только цифры без "3."
        return result[2:] if result.startswith("3.") else result
    else:
        # Fallback к Python системе
        print(f"📊 Генерация {count:,} цифр π с помощью Python...")
        return generator.generate_pi_digits(count)

def test_adaptive_compression():
    """Тестируем адаптивную систему сжатия"""
    print("🧪 ТЕСТ АДАПТИВНОЙ СИСТЕМЫ СЖАТИЯ")
    print("=" * 50)
    
    # Создаем генератор π (C++ или Python)
    pi_gen = get_pi_generator()
    
    # Генерируем π для тестов
    pi_digits = generate_pi_digits(pi_gen, 100000)  # 100K цифр
    print(f"📊 Получено {len(pi_digits):,} цифр π")
    
    # Создаем компрессор с новыми функциями
    compressor = CompressionCore(
        pi_generator=pi_gen,
        backup_enabled=True,
        adaptive_search=True,
        enable_logging=True,
        multithreaded_search=True,  # ВКЛЮЧАЕМ МНОГОПОТОЧНЫЙ ПОИСК!
        search_threads=31  # 39-1=31 потоков для поиска
    )
    
    # Тестовые данные разного типа
    test_cases = [
        {
            'name': 'Текстовый файл',
            'data': b"This is a test message for Pi-Archiver compression system. " * 20,
            'file': 'test_text.txt'
        },
        {
            'name': 'Бинарные данные',
            'data': bytes(range(256)) * 10,  # Повторяющийся паттерн
            'file': 'test_binary.bin'
        },
        {
            'name': 'Случайные данные',
            'data': os.urandom(500),  # Случайные данные
            'file': 'test_random.dat'
        },
        {
            'name': 'Смешанные данные',
            'data': b"Header: " + bytes(range(100)) + b"Middle:" + os.urandom(200) + b"End",
            'file': 'test_mixed.mix'
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🔸 Тест {i+1}: {test_case['name']}")
        print(f"   Размер: {len(test_case['data']):,} байт")
        
        # Сжимаем данные с НОВЫМ ДИАПАЗОНОМ (1-48 байт)
        start_time = time.time()
        blocks, stats = compressor.compress_data(
            data=test_case['data'],
            pi_digits=pi_digits,
            block_size_range=(1, 48),  # НОВЫЙ ДИАПАЗОН: 1-48 байт!
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
            'adaptive_searches': stats.adaptive_searches,
            'avg_search_attempts': stats.avg_search_attempts,
            'compress_time': compress_time,
            'recover_time': recover_time,
            'integrity': integrity_ok,
            'session_id': stats.session_id
        }
        results.append(result)
        
        # Выводим результаты
        print(f"   📈 Коэффициент сжатия: {stats.compression_ratio:.2f}x")
        print(f"   🔍 Найдено блоков: {stats.blocks_found}/{stats.blocks_total} ({stats.blocks_found/stats.blocks_total:.1%})")
        print(f"   💾 Бэкапов использовано: {stats.backup_blocks_used}")
        print(f"   🔄 Адаптивных поисков: {stats.adaptive_searches}")
        print(f"   ⏱️ Время сжатия: {compress_time:.2f} сек")
        print(f"   ⏱️ Время восстановления: {recover_time:.2f} сек")
        print(f"   ✅ Целостность: {'OK' if integrity_ok else 'FAILED'}")
        
        if stats.session_id:
            print(f"   📝 Лог сохранен: logs/{stats.session_id}.json")
    
    # Общая статистика
    print(f"\n📊 ОБЩАЯ СТАТИСТИКА ТЕСТОВ")
    print("=" * 30)
    
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
    
    # Проверка целостности всех тестов
    all_integrity_ok = all(r['integrity'] for r in results)
    print(f"✅ Целостность всех данных: {'OK' if all_integrity_ok else 'FAILED'}")
    
    return results

def test_adaptive_search_features():
    """Тестируем особенности адаптивного поиска"""
    print("\n🔍 ТЕСТ АДАПТИВНОГО ПОИСКА")
    print("=" * 30)
    
    # Создаем компрессор с адаптивным поиском
    pi_gen = get_pi_generator()
    pi_digits = generate_pi_digits(pi_gen, 50000)
    print(f"📊 Получено {len(pi_digits):,} цифр π для теста адаптивного поиска")
    
    compressor = CompressionCore(
        pi_generator=pi_gen,
        backup_enabled=True,
        adaptive_search=True,
        enable_logging=True,
        multithreaded_search=True,  # ВКЛЮЧАЕМ МНОГОПОТОЧНЫЙ ПОИСК!
        search_threads=31
    )
    
    # Специальные тестовые данные
    test_data = b"1234567890" * 10  # Повторяющийся паттерн, который должен быть в π
    
    print(f"📊 Тестовые данные: {len(test_data)} байт")
    print("🔍 Поиск паттерна '1234567890' в π...")
    
    # Сжимаем с НОВЫМ ДИАПАЗОНОМ (1-48 байт)
    blocks, stats = compressor.compress_data(
        data=test_data,
        pi_digits=pi_digits,
        block_size_range=(1, 48),  # НОВЫЙ ДИАПАЗОН: 1-48 байт!
        output_file="adaptive_test"
    )
    
    print(f"📈 Результаты:")
    print(f"   Коэффициент сжатия: {stats.compression_ratio:.2f}x")
    print(f"   Успешность поиска: {stats.blocks_found/stats.blocks_total:.1%}")
    print(f"   Средних попыток на блок: {stats.avg_search_attempts:.1f}")
    print(f"   Адаптивных поисков: {stats.adaptive_searches}")
    
    # Анализируем блоки
    print(f"\n🔍 АНАЛИЗ БЛОКОВ:")
    for block in blocks[:5]:  # Первые 5 блоков
        print(f"   Блок #{block.block_id}: {len(block.original_data)} байт")
        print(f"      Найден: {'Да' if block.found_positions() else 'Нет'}")
        print(f"      Попыток: {block.search_attempts}")
        print(f"      Адаптивный: {'Да' if block.adaptive_search else 'Нет'}")
        print(f"      Бэкап: {'Да' if block.backup_used else 'Нет'}")
        if block.found_positions():
            print(f"      Позиция: {block.start_pos}-{block.end_pos}")

if __name__ == "__main__":
    try:
        # Создаем директорию для логов
        Path("logs").mkdir(exist_ok=True)
        
        # Запускаем тесты
        results = test_adaptive_compression()
        test_adaptive_search_features()
        
        print(f"\n🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
