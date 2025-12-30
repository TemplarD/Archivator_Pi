#!/usr/bin/env python3
"""
Общий тестовый runner для алгоритмов Chudnovsky
"""

import sys
import time
from pathlib import Path

# Добавляем путь к модулям
test_dir = Path(__file__).parent
project_root = test_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

def run_all_chudnovsky_tests():
    """Запускаем все тесты Chudnovsky"""
    print("🧪 ОБЩИЙ ТЕСТ CHUDNOVSKY ALGORITHMS")
    print("=" * 60)
    
    tests = [
        ("Корректность", "test_correctness.py"),
        ("Многопоточность 10000+", "test_multithreading_10000.py"),
    ]
    
    results = {}
    
    for test_name, test_file in tests:
        print(f"\n🔬 Запуск теста: {test_name}")
        print("-" * 40)
        
        try:
            # Импортируем и запускаем тест
            test_module = __import__(test_file[:-3])
            
            start = time.time()
            success = test_module.main() if hasattr(test_module, 'main') else True
            
            # Если нет main, пробуем запустить напрямую
            if not hasattr(test_module, 'main'):
                if 'test_chudnovsky_correctness' in test_file:
                    success = test_module.test_chudnovsky_correctness()
                elif 'test_multithreading_10000' in test_file:
                    success = test_module.test_multithreading_10000()
            
            elapsed = time.time() - start
            results[test_name] = {
                'success': success,
                'time': elapsed
            }
            
            print(f"{'✅' if success else '❌'} {test_name}: {elapsed:.2f}s")
            
        except Exception as e:
            print(f"❌ {test_name}: Ошибка - {e}")
            results[test_name] = {
                'success': False,
                'time': 0,
                'error': str(e)
            }
    
    # Итоги
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ВСЕХ ТЕСТОВ:")
    print("-" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ ПРОЙДЕН" if result['success'] else "❌ ПАДЕНИЕ"
        time_str = f"{result['time']:.2f}s" if result['time'] > 0 else "N/A"
        print(f"{test_name:<25} {status:<12} {time_str}")
        
        if result['success']:
            passed += 1
    
    print("-" * 40)
    print(f"Пройдено: {passed}/{total} тестов")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        return True
    else:
        print("⚠️ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
        return False

if __name__ == "__main__":
    success = run_all_chudnovsky_tests()
    sys.exit(0 if success else 1)
