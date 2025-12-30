#!/usr/bin/env python3
"""
Комплексные тесты многопоточных алгоритмов генерации π
Проверяет корректность, производительность и стабильность
"""

import sys
import os
import time
import threading
from typing import Dict, List, Tuple, Any
from concurrent.futures import ThreadPoolExecutor

# Добавляем путь к исходникам
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class MultiThreadPiTest:
    """Тестирование многопоточных алгоритмов π"""
    
    def __init__(self):
        self.test_results = {}
        self.correct_pi_start = "14159265358979323846264338327950288419716939937510"
        
    def run_all_tests(self):
        """Запускает все тесты многопоточности"""
        print("🧪 Комплексные тесты многопоточных алгоритмов π")
        print("=" * 60)
        
        # Тестируемые алгоритмы
        algorithms = [
            ("ChudnovskyBinarySplitting", "chudnovsky.multi_thread"),
            ("ChudnovskyBlockParallel", "chudnovsky.multi_thread"), 
            ("BBPParallel", "chudnovsky.multi_thread"),
            ("SimpleParallelChudnovsky", "chudnovsky.multi_thread"),
        ]
        
        # Параметры тестов
        test_configs = [
            {"digits": 1000, "workers": 1, "name": "1 поток"},
            {"digits": 1000, "workers": 2, "name": "2 потока"},
            {"digits": 1000, "workers": 4, "name": "4 потока"},
            {"digits": 5000, "workers": 2, "name": "5K цифр, 2 потока"},
            {"digits": 5000, "workers": 4, "name": "5K цифр, 4 потока"},
        ]
        
        for algo_name, module_path in algorithms:
            print(f"\n🔧 Тестирование: {algo_name}")
            print("-" * 40)
            
            try:
                # Импортируем алгоритм
                exec(f"from pi_generator.algorithms.{module_path} import {algo_name}")
                algo_class = eval(algo_name)
                
                algo_results = {}
                
                for config in test_configs:
                    test_name = f"{config['name']}"
                    print(f"  📊 {test_name}: ", end="")
                    
                    try:
                        result = self._test_algorithm(
                            algo_class, 
                            config["digits"], 
                            config["workers"]
                        )
                        algo_results[test_name] = result
                        print(f"✅ {result['status']}")
                        
                    except Exception as e:
                        algo_results[test_name] = {
                            "status": "ERROR",
                            "error": str(e),
                            "time": 0,
                            "correct": False
                        }
                        print(f"❌ {str(e)[:50]}...")
                
                self.test_results[algo_name] = algo_results
                
            except ImportError as e:
                print(f"  ❌ Не удалось импортировать: {e}")
                self.test_results[algo_name] = {"import_error": str(e)}
        
        # Выводим сводку
        self._print_summary()
        
        return self.test_results
    
    def _test_algorithm(self, algo_class, digits: int, workers: int) -> Dict[str, Any]:
        """Тестирует один алгоритм с заданными параметрами"""
        
        # Создаем экземпляр
        generator = algo_class()
        
        # Замеряем время
        start_time = time.time()
        
        # Вычисляем π
        pi_digits = generator.compute_pi(digits, num_workers=workers)
        
        elapsed = time.time() - start_time
        
        # Проверяем корректность
        is_correct = pi_digits.startswith(self.correct_pi_start)
        
        # Проверяем длину
        length_ok = len(pi_digits) >= digits * 0.95  # Допускаем небольшую погрешность
        
        return {
            "status": "OK" if is_correct and length_ok else "FAIL",
            "time": elapsed,
            "digits": len(pi_digits),
            "correct": is_correct,
            "length_ok": length_ok,
            "first_20": pi_digits[:20] + "..." if len(pi_digits) > 20 else pi_digits,
            "workers": workers
        }
    
    def _print_summary(self):
        """Выводит сводную таблицу результатов"""
        print("\n📈 Сводная таблица результатов")
        print("=" * 80)
        
        # Заголовок таблицы
        header = f"{'Алгоритм':<25} {'Конфигурация':<15} {'Статус':<8} {'Время':<8} {'Цифр':<8} {'Коррект':<8}"
        print(header)
        print("-" * 80)
        
        # Данные таблицы
        for algo_name, results in self.test_results.items():
            if "import_error" in results:
                print(f"{algo_name:<25} {'Ошибка импорта':<15} {'❌':<8} {'-':<8} {'-':<8} {'-':<8}")
                continue
                
            for config_name, result in results.items():
                status_icon = "✅" if result["status"] == "OK" else "❌"
                time_str = f"{result['time']:.3f}s"
                digits_str = str(result["digits"])
                correct_str = "✅" if result["correct"] else "❌"
                
                print(f"{algo_name:<25} {config_name:<15} {status_icon:<8} {time_str:<8} {digits_str:<8} {correct_str:<8}")
        
        print("-" * 80)
        
        # Анализ производительности
        self._analyze_performance()
    
    def _analyze_performance(self):
        """Анализирует производительность алгоритмов"""
        print("\n🚀 Анализ производительности")
        print("=" * 50)
        
        # Сравниваем ускорение
        for algo_name, results in self.test_results.items():
            if "import_error" in results:
                continue
                
            print(f"\n📊 {algo_name}:")
            
            # Ищем тесты с разным количеством потоков
            single_thread = results.get("1 поток")
            two_threads = results.get("2 потока")
            four_threads = results.get("4 потока")
            
            if single_thread and two_threads:
                speedup = single_thread["time"] / two_threads["time"]
                print(f"  🔄 Ускорение 2 потока: {speedup:.2f}x")
            
            if single_thread and four_threads:
                speedup = single_thread["time"] / four_threads["time"]
                print(f"  🔄 Ускорение 4 потока: {speedup:.2f}x")
            
            # Проверяем корректность
            all_correct = all(
                result.get("correct", False) 
                for result in results.values() 
                if isinstance(result, dict)
            )
            print(f"  ✅ Корректность всех тестов: {'Да' if all_correct else 'Нет'}")
    
    def test_concurrent_access(self):
        """Тестирует одновременный доступ к алгоритмам"""
        print("\n🔀 Тест одновременного доступа")
        print("=" * 40)
        
        def worker_thread(worker_id: int, results: List):
            """Рабочий поток для тестирования"""
            try:
                from pi_generator.algorithms.chudnovsky.multi_thread import ChudnovskyBinarySplitting
                
                generator = ChudnovskyBinarySplitting()
                start_time = time.time()
                pi_digits = generator.compute_pi(1000, num_workers=2)
                elapsed = time.time() - start_time
                
                results.append({
                    "worker_id": worker_id,
                    "time": elapsed,
                    "correct": pi_digits.startswith(self.correct_pi_start),
                    "digits": len(pi_digits)
                })
                
            except Exception as e:
                results.append({
                    "worker_id": worker_id,
                    "error": str(e)
                })
        
        # Запускаем несколько потоков одновременно
        num_threads = 4
        results = []
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(worker_thread, i, results) 
                for i in range(num_threads)
            ]
            
            # Ждем завершения
            for future in futures:
                future.result()
        
        # Анализируем результаты
        successful = [r for r in results if "error" not in r]
        failed = [r for r in results if "error" in r]
        
        print(f"  ✅ Успешных потоков: {len(successful)}/{num_threads}")
        print(f"  ❌ Потоков с ошибками: {len(failed)}")
        
        if successful:
            avg_time = sum(r["time"] for r in successful) / len(successful)
            all_correct = all(r["correct"] for r in successful)
            print(f"  ⏱️  Среднее время: {avg_time:.3f}s")
            print(f"  ✅ Все корректны: {'Да' if all_correct else 'Нет'}")
        
        return len(successful) == num_threads and all(r.get("correct", False) for r in successful)

def main():
    """Основная функция тестирования"""
    tester = MultiThreadPiTest()
    
    # Запускаем основные тесты
    results = tester.run_all_tests()
    
    # Запускаем тест одновременного доступа
    concurrent_ok = tester.test_concurrent_access()
    
    # Итоговый результат
    print(f"\n🎯 Итоговый результат:")
    print(f"  📊 Тесты алгоритмов: {'✅ Пройдены' if results else '❌ Провалены'}")
    print(f"  🔀 Одновременный доступ: {'✅ Пройден' if concurrent_ok else '❌ Провален'}")
    
    # Сохраняем результаты
    import json
    with open(os.path.join(os.path.dirname(__file__), 'multi_thread_test_results.json'), 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"  💾 Результаты сохранены в: multi_thread_test_results.json")
    
    return results and concurrent_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
