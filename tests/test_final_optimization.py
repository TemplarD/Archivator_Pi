#!/usr/bin/env python3
"""
Финальный тест для проверки полной оптимизации многопоточности Pi-Archiver Ultra
"""

import pytest
import time
import os
import sys
import tempfile
from pathlib import Path

# Добавляем пути к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

def test_complete_optimization():
    """Полный тест оптимизированной системы"""
    print("=== Финальный тест оптимизации Pi-Archiver Ultra ===")
    
    # Импорт оптимизированных компонентов
    from main.archiver_main_optimized import OptimizedPiArchiverUltra
    
    # Создание архиватора
    archiver = OptimizedPiArchiverUltra(num_workers=2, cache_size=1000)
    
    # Тестовые данные
    test_content = b"Pi-Archiver Ultra optimization test data. " * 100
    
    # Временный файл
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        # Архивация
        print("1. Тест архивации...")
        start_time = time.time()
        archive_path = archiver.archive_file_optimized(
            temp_file, use_gpu=False, use_processes=False
        )
        archive_time = time.time() - start_time
        
        assert Path(archive_path).exists()
        print(f"   Архивация завершена за {archive_time:.2f} сек")
        
        # Извлечение
        print("2. Тест извлечения...")
        start_time = time.time()
        extracted_path = archiver.extract_file_optimized(
            archive_path, use_processes=False
        )
        extract_time = time.time() - start_time
        
        assert Path(extracted_path).exists()
        print(f"   Извлечение завершено за {extract_time:.2f} сек")
        
        # Проверка целостности
        print("3. Проверка целостности...")
        extracted_content = Path(extracted_path).read_bytes()
        assert extracted_content == test_content
        print("   Целостность данных подтверждена")
        
        # Статистика производительности
        print("4. Статистика производительности...")
        stats = archiver.get_performance_stats()
        print(f"   Количество работников: {stats['num_workers']}")
        print(f"   Точность π: {stats['pi_precision']}")
        print(f"   Hit rate кеша: {stats['cache_stats']['hit_rate']:.2%}")
        
        # Очистка
        os.unlink(archive_path)
        os.unlink(extracted_path)
        
        print("=== Все тесты пройдены успешно! ===")
        
    finally:
        os.unlink(temp_file)

if __name__ == "__main__":
    test_complete_optimization()
