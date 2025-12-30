#!/usr/bin/env python3
"""
Тестирование производительности многопоточных алгоритмов
Измеряет ускорение, эффективность и масштабируемость
"""

import sys
import os
import time
import multiprocessing as mp
from typing import Dict, List, Tuple, Any
import json

# Добавляем путь к исходникам
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class MultiThreadPerformanceTest:
    """Тестирование производительности многопоточных алгоритмов"""
    
    def __init__(self):
        self.performance_results = {}
        self.cpu_count = mp.cpu_count()
        
    def run_performance_tests(self):
        """Запускает все тесты производительности"""
        print("⚡ Тестирование производительности многопоточности")
        print("=" * 60)
        print(f"🖥️  Доступно CPU ядер: {self.cpu_count}")
        print()
        
        # Алгоритмы для тестирования
        algorithms = [
            ("ChudnovskyBinarySplitting", "chudnovsky.multi_thread"),
            ("ChudnovskyBlockParallel", "chudnovsky.multi_thread"),
            ("SimpleParallelChudnovsky", "chudnovsky.multi_thread"),
        ]
        
        # Конфигурации тестов
        test_configs = [
            {"digits": 1000, "name": "1K цифр"},
            {"digits": 5000, "name": "5K цифр"},
            {"digits": 10000, "name": "10K цифр"},
        ]
        
        # Количество потоков для тестирования
        worker_counts = [1, 2, 4, min(8, self.cpu_count)]
        
        for algo_name, module_path in algorithms:
            print(f"🚀 Производительность: {algo_name}")
            print("-" * 40)
            
            try:
                # Импортируем алгоритм
                exec(f"from pi_generator.algorithms.{module_path} import {algo_name}")
                algo_class = eval(algo_name)
                
                algo_results = {}
                
                for config in test_configs:
                    print(f"  📊 {config['name']}: ", end="")
                    
                    config_results = self._test_algorithm_performance(
                        algo_class, config["digits"], worker_counts
                    )
                    algo_results[config["name"]] = config_results
                    
                    # Показываем лучший результат
                    best_speedup = max(r["speedup"] for r in config_results.values())
                    print(f"лучшее ускорение {best_speedup:.2f}x")
                
                self.performance_results[algo_name] = algo_results
                
            except ImportError as e:
                print(f"  ❌ Не удалось импортировать: {e}")
                self.performance_results[algo_name] = {"import_error": str(e)}
        
        # Анализируем результаты
        self._analyze_performance()
        
        return self.performance_results
    
    def _test_algorithm_performance(self, algo_class, digits: int, worker_counts: List[int]) -> Dict[int, Dict]:
        """Тестирует производительность алгоритма с разным количеством потоков"""
        
        results = {}
        baseline_time = None
        
        for workers in worker_counts:
            try:
                # Создаем экземпляр
                generator = algo_class()
                
                # Замеряем время
                start_time = time.time()
                pi_digits = generator.compute_pi(digits, num_workers=workers)
                elapsed = time.time() - start_time
                
                # Проверяем корректность
                correct_pi = pi_digits.startswith("14159265358979323846264338327950288419716939937510")
                
                # Вычисляем ускорение
                if baseline_time is None:
                    baseline_time = elapsed
                    speedup = 1.0
                else:
                    speedup = baseline_time / elapsed
                
                # Вычисляем эффективность
                efficiency = speedup / workers * 100
                
                results[workers] = {
                    "time": elapsed,
                    "speedup": speedup,
                    "efficiency": efficiency,
                    "correct": correct_pi,
                    "digits": len(pi_digits)
                }
                
            except Exception as e:
                results[workers] = {
                    "error": str(e),
                    "time": float('inf'),
                    "speedup": 0,
                    "efficiency": 0,
                    "correct": False
                }
        
        return results
    
    def _analyze_performance(self):
        """Анализирует результаты производительности"""
        print("\n📈 Анализ производительности")
        print("=" * 80)
        
        # Сводная таблица
        header = f"{'Алгоритм':<25} {'Размер':<8} {'1 поток':<10} {'2 потока':<12} {'4 потока':<12} {'8 потоков':<12}"
        print(header)
        print("-" * 80)
        
        for algo_name, algo_results in self.performance_results.items():
            if "import_error" in algo_results:
                continue
                
            for config_name, config_results in algo_results.items():
                if not isinstance(config_results, dict):
                    continue
                
                # Получаем времена
                time_1 = config_results.get(1, {}).get("time", 0)
                time_2 = config_results.get(2, {}).get("time", 0)
                time_4 = config_results.get(4, {}).get("time", 0)
                time_8 = config_results.get(8, {}).get("time", 0)
                
                # Форматируем вывод
                time_1_str = f"{time_1:.3f}s" if time_1 != float('inf') else "ERROR"
                time_2_str = f"{time_2:.3f}s" if time_2 != float('inf') else "ERROR"
                time_4_str = f"{time_4:.3f}s" if time_4 != float('inf') else "ERROR"
                time_8_str = f"{time_8:.3f}s" if time_8 != float('inf') else "ERROR"
                
                print(f"{algo_name:<25} {config_name:<8} {time_1_str:<10} {time_2_str:<12} {time_4_str:<12} {time_8_str:<12}")
        
        print("-" * 80)
        
        # Анализ ускорения
        self._analyze_speedup()
        
        # Анализ эффективности
        self._analyze_efficiency()
        
        # Рекомендации
        self._give_recommendations()
    
    def _analyze_speedup(self):
        """Анализирует ускорение"""
        print("\n🚀 Анализ ускорения")
        print("=" * 50)
        
        for algo_name, algo_results in self.performance_results.items():
            if "import_error" in algo_results:
                continue
                
            print(f"\n📊 {algo_name}:")
            
            for config_name, config_results in algo_results.items():
                if not isinstance(config_results, dict):
                    continue
                
                speedups = []
                workers_list = []
                
                for workers, result in config_results.items():
                    if isinstance(result, dict) and "speedup" in result:
                        speedups.append(result["speedup"])
                        workers_list.append(workers)
                
                if speedups:
                    max_speedup = max(speedups)
                    optimal_workers = workers_list[speedups.index(max_speedup)]
                    
                    print(f"  {config_name}: макс. ускорение {max_speedup:.2f}x на {optimal_workers} потоках")
    
    def _analyze_efficiency(self):
        """Анализирует эффективность"""
        print("\n📊 Анализ эффективности")
        print("=" * 50)
        
        for algo_name, algo_results in self.performance_results.items():
            if "import_error" in algo_results:
                continue
                
            print(f"\n📊 {algo_name}:")
            
            for config_name, config_results in algo_results.items():
                if not isinstance(config_results, dict):
                    continue
                
                efficiencies = []
                workers_list = []
                
                for workers, result in config_results.items():
                    if isinstance(result, dict) and "efficiency" in result and workers > 1:
                        efficiencies.append(result["efficiency"])
                        workers_list.append(workers)
                
                if efficiencies:
                    avg_efficiency = sum(efficiencies) / len(efficiencies)
                    max_efficiency = max(efficiencies)
                    
                    print(f"  {config_name}: средняя эффективность {avg_efficiency:.1f}%, макс. {max_efficiency:.1f}%")
    
    def _give_recommendations(self):
        """Дает рекомендации по оптимизации"""
        print("\n💡 Рекомендации по оптимизации")
        print("=" * 40)
        
        # Находим лучший алгоритм
        best_algorithms = {}
        
        for algo_name, algo_results in self.performance_results.items():
            if "import_error" in algo_results:
                continue
                
            max_speedup = 0
            best_config = None
            
            for config_name, config_results in algo_results.items():
                if not isinstance(config_results, dict):
                    continue
                    
                for workers, result in config_results.items():
                    if isinstance(result, dict) and "speedup" in result:
                        if result["speedup"] > max_speedup:
                            max_speedup = result["speedup"]
                            best_config = f"{config_name} на {workers} потоках"
            
            if max_speedup > 0:
                best_algorithms[algo_name] = {
                    "speedup": max_speedup,
                    "config": best_config
                }
        
        if best_algorithms:
            # Сортируем по ускорению
            sorted_algos = sorted(best_algorithms.items(), key=lambda x: x[1]["speedup"], reverse=True)
            
            print("🏆 Лучшие результаты:")
            for i, (algo_name, result) in enumerate(sorted_algos[:3], 1):
                print(f"  {i}. {algo_name}: {result['speedup']:.2f}x ({result['config']})")
        
        # Общие рекомендации
        print("\n🔧 Общие рекомендации:")
        print("  • Используйте 2-4 потока для лучших результатов")
        print("  • Для больших объемов данных увеличивайте количество потоков")
        print("  • Следите за эффективностью - не всегда больше потоков лучше")
        print("  • Выбирайте алгоритм в зависимости от размера задачи")
    
    def save_results(self, filename: str = None):
        """Сохраняет результаты в файл"""
        if filename is None:
            filename = os.path.join(os.path.dirname(__file__), 'performance_results.json')
        
        with open(filename, 'w') as f:
            json.dump(self.performance_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Результаты сохранены в: {filename}")

def main():
    """Основная функция тестирования"""
    tester = MultiThreadPerformanceTest()
    
    # Запускаем тесты производительности
    results = tester.run_performance_tests()
    
    # Сохраняем результаты
    tester.save_results()
    
    # Проверяем что есть успешные тесты
    successful_tests = any(
        isinstance(algo_results, dict) and 
        any(isinstance(config_results, dict) for config_results in algo_results.values())
        for algo_results in results.values()
    )
    
    print(f"\n🎯 Итоговый результат: {'✅ Успешно' if successful_tests else '❌ Провал'}")
    
    return successful_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
