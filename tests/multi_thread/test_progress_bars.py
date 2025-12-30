#!/usr/bin/env python3
"""
Тестирование прогресс-баров в многопоточных алгоритмах
Проверяет корректность отображения прогресса и отсутствие конфликтов
"""

import sys
import os
import time
import threading
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor

# Добавляем путь к исходникам
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class ProgressBarController:
    """Контроллер для отслеживания прогресс-баров"""
    
    def __init__(self):
        self.progress_events = []
        self.lock = threading.Lock()
    
    def callback(self, progress: int, current: int, total: int, thread_id: str = "main"):
        """Callback для отслеживания прогресса"""
        with self.lock:
            self.progress_events.append({
                "timestamp": time.time(),
                "progress": progress,
                "current": current,
                "total": total,
                "thread_id": thread_id
            })
    
    def get_events(self, thread_id: str = None) -> List[Dict]:
        """Получает события прогресса"""
        with self.lock:
            if thread_id:
                return [e for e in self.progress_events if e["thread_id"] == thread_id]
            return self.progress_events.copy()

class MultiThreadProgressTest:
    """Тестирование прогресс-баров в многопоточности"""
    
    def __init__(self):
        self.controller = ProgressBarController()
        self.test_results = {}
    
    def test_progress_bars(self):
        """Тестирует прогресс-бары во всех многопоточных алгоритмах"""
        print("📊 Тестирование прогресс-баров в многопоточности")
        print("=" * 60)
        
        algorithms = [
            ("ChudnovskyBinarySplitting", "chudnovsky.multi_thread"),
            ("ChudnovskyBlockParallel", "chudnovsky.multi_thread"),
            ("SimpleParallelChudnovsky", "chudnovsky.multi_thread"),
        ]
        
        for algo_name, module_path in algorithms:
            print(f"\n🔧 Тест прогресс-бара: {algo_name}")
            print("-" * 40)
            
            try:
                # Импортируем алгоритм
                exec(f"from pi_generator.algorithms.{module_path} import {algo_name}")
                algo_class = eval(algo_name)
                
                # Очищаем предыдущие события
                self.controller.progress_events.clear()
                
                # Тестируем с разным количеством потоков
                for workers in [1, 2, 4]:
                    test_name = f"{workers} поток(ов)"
                    print(f"  📊 {test_name}: ", end="")
                    
                    try:
                        result = self._test_algorithm_progress(
                            algo_class, workers, test_name
                        )
                        self.test_results[f"{algo_name}_{workers}"] = result
                        print(f"✅ {result['status']}")
                        
                    except Exception as e:
                        print(f"❌ {str(e)[:50]}...")
                        self.test_results[f"{algo_name}_{workers}"] = {
                            "status": "ERROR",
                            "error": str(e)
                        }
                
            except ImportError as e:
                print(f"  ❌ Не удалось импортировать: {e}")
        
        # Анализируем результаты
        self._analyze_progress_results()
        
        return self.test_results
    
    def _test_algorithm_progress(self, algo_class, workers: int, test_name: str) -> Dict[str, Any]:
        """Тестирует прогресс-бар одного алгоритма"""
        
        # Создаем экземпляр
        generator = algo_class()
        
        # Запускаем вычисление с callback
        start_time = time.time()
        
        def progress_callback(progress, current, total):
            self.controller.callback(progress, current, total, test_name)
        
        pi_digits = generator.compute_pi(2000, num_workers=workers, progress_callback=progress_callback)
        
        elapsed = time.time() - start_time
        
        # Анализируем события прогресса
        events = self.controller.get_events(test_name)
        
        # Проверяем корректность прогресса
        progress_values = [e["progress"] for e in events]
        
        # Проверяем что прогресс дошел до 100%
        reached_100 = any(p >= 100 for p in progress_values)
        
        # Проверяем монотонность (необязательно, но желательно)
        is_monotonic = all(progress_values[i] <= progress_values[i+1] 
                          for i in range(len(progress_values)-1) 
                          if progress_values[i] > 0 and progress_values[i+1] > 0)
        
        # Проверяем количество событий
        enough_events = len(events) >= 5  # Минимум 5 событий прогресса
        
        # Проверяем корректность результата
        correct_pi = pi_digits.startswith("14159265358979323846264338327950288419716939937510")
        
        return {
            "status": "OK" if reached_100 and correct_pi else "FAIL",
            "time": elapsed,
            "events_count": len(events),
            "reached_100": reached_100,
            "is_monotonic": is_monotonic,
            "enough_events": enough_events,
            "correct_pi": correct_pi,
            "max_progress": max(progress_values) if progress_values else 0,
            "min_progress": min(progress_values) if progress_values else 0,
            "workers": workers
        }
    
    def _analyze_progress_results(self):
        """Анализирует результаты тестов прогресс-баров"""
        print("\n📈 Анализ прогресс-баров")
        print("=" * 60)
        
        # Заголовок таблицы
        header = f"{'Алгоритм':<25} {'Потоки':<8} {'События':<8} {'100%':<6} {'Монотон':<8} {'Статус':<8}"
        print(header)
        print("-" * 60)
        
        ok_count = 0
        total_count = 0
        
        for test_name, result in self.test_results.items():
            if "error" in result:
                continue
                
            total_count += 1
            
            algo_name = test_name.rsplit('_', 1)[0]
            workers = result.get("workers", 0)
            events = result.get("events_count", 0)
            reached_100 = "✅" if result.get("reached_100", False) else "❌"
            monotonic = "✅" if result.get("is_monotonic", False) else "❌"
            status = "✅" if result.get("status") == "OK" else "❌"
            
            if result.get("status") == "OK":
                ok_count += 1
            
            print(f"{algo_name:<25} {workers:<8} {events:<8} {reached_100:<6} {monotonic:<8} {status:<8}")
        
        print("-" * 60)
        print(f"📊 Успешных тестов: {ok_count}/{total_count}")
        
        # Детальный анализ проблем
        self._analyze_progress_issues()
    
    def _analyze_progress_issues(self):
        """Анализирует проблемы с прогресс-барами"""
        print("\n🔍 Детальный анализ проблем")
        print("=" * 40)
        
        issues = {
            "no_100_percent": [],
            "not_monotonic": [],
            "few_events": [],
            "incorrect_pi": []
        }
        
        for test_name, result in self.test_results.items():
            if "error" in result:
                continue
                
            if not result.get("reached_100", False):
                issues["no_100_percent"].append(test_name)
            
            if not result.get("is_monotonic", False):
                issues["not_monotonic"].append(test_name)
            
            if not result.get("enough_events", False):
                issues["few_events"].append(test_name)
            
            if not result.get("correct_pi", False):
                issues["incorrect_pi"].append(test_name)
        
        for issue_type, problematic_tests in issues.items():
            if problematic_tests:
                issue_names = {
                    "no_100_percent": "Не дошли до 100%",
                    "not_monotonic": "Немонотонный прогресс",
                    "few_events": "Мало событий",
                    "incorrect_pi": "Неверный результат"
                }
                
                print(f"\n❌ {issue_names[issue_type]}:")
                for test in problematic_tests:
                    print(f"  - {test}")
    
    def test_concurrent_progress(self):
        """Тестирует одновременную работу нескольких прогресс-баров"""
        print("\n🔀 Тест одновременных прогресс-баров")
        print("=" * 45)
        
        def worker_with_progress(worker_id: int, results: List):
            """Рабочий поток с прогресс-баром"""
            try:
                from pi_generator.algorithms.chudnovsky.multi_thread import ChudnovskyBinarySplitting
                
                def progress_callback(progress, current, total):
                    self.controller.callback(progress, current, total, f"worker_{worker_id}")
                
                generator = ChudnovskyBinarySplitting()
                pi_digits = generator.compute_pi(1500, num_workers=2, progress_callback=progress_callback)
                
                results.append({
                    "worker_id": worker_id,
                    "correct": pi_digits.startswith("14159265358979323846264338327950288419716939937510"),
                    "events": len(self.controller.get_events(f"worker_{worker_id}"))
                })
                
            except Exception as e:
                results.append({
                    "worker_id": worker_id,
                    "error": str(e)
                })
        
        # Запускаем несколько потоков одновременно
        num_threads = 3
        results = []
        self.controller.progress_events.clear()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(worker_with_progress, i, results) 
                for i in range(num_threads)
            ]
            
            for future in futures:
                future.result()
        
        # Анализируем результаты
        successful = [r for r in results if "error" not in r]
        failed = [r for r in results if "error" in r]
        
        print(f"  ✅ Успешных потоков: {len(successful)}/{num_threads}")
        print(f"  ❌ Потоков с ошибками: {len(failed)}")
        
        if successful:
            total_events = sum(r["events"] for r in successful)
            all_correct = all(r["correct"] for r in successful)
            print(f"  📊 Всего событий прогресса: {total_events}")
            print(f"  ✅ Все корректны: {'Да' if all_correct else 'Нет'}")
            
            # Проверяем что у каждого потока свои события
            unique_threads = set(e["thread_id"] for e in self.controller.progress_events)
            print(f"  🔀 Уникальных потоков: {len(unique_threads)}")
        
        return len(successful) == num_threads and all(r.get("correct", False) for r in successful)

def main():
    """Основная функция тестирования"""
    tester = MultiThreadProgressTest()
    
    # Тестируем прогресс-бары
    progress_results = tester.test_progress_bars()
    
    # Тестируем одновременную работу
    concurrent_ok = tester.test_concurrent_progress()
    
    # Итоговый результат
    print(f"\n🎯 Итоговый результат прогресс-баров:")
    
    ok_tests = sum(1 for r in progress_results.values() if r.get("status") == "OK")
    total_tests = len([r for r in progress_results.values() if "error" not in r])
    
    print(f"  📊 Тесты прогресс-баров: {ok_tests}/{total_tests} ✅")
    print(f"  🔀 Одновременная работа: {'✅' if concurrent_ok else '❌'}")
    
    return ok_tests == total_tests and concurrent_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
