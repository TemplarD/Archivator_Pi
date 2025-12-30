#!/usr/bin/env python3
"""
Улучшенная генерация π с правильной многопоточностью
"""

import time
import multiprocessing as mp
from pathlib import Path
from typing import Optional, Callable, Dict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import os

# Абсолютные импорты
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

import sys
import time
from typing import Callable, Optional

from progress_indicators.pi_progress.pi_generator_callback import PiProgressCallback
from archive_operations.system_info.multi_core_info import MultiCoreInfo
from pi_generator.pi_generator import PiGenerator


class BenchmarkCallback:
    """Callback для бенчмарка с чистым выводом в одной строке"""
    
    def __init__(self, workers: int):
        self.workers = workers
        self.start_time = None
        self.progress_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def create_callback(self) -> Callable:
        """Создает callback функцию для бенчмарка"""
        self.start_time = time.time()
        
        def callback(progress_percent: float, current_iter: int, total_iters: int):
            """Callback для бенчмарка с полной информацией в одной строке"""
            # Расчет времени и скорости
            elapsed = time.time() - self.start_time
            rate = current_iter / elapsed if elapsed > 0 else 0
            
            # Расчет ETA
            if rate > 0:
                remaining_iters = total_iters - current_iter
                eta = remaining_iters / rate
                eta_str = f"ETA: {eta:.0f}сек"
            else:
                eta_str = "ETA: --"
            
            # Формируем полную информацию в одной строке
            char_idx = int(progress_percent) % len(self.progress_chars)
            progress_line = (f"{self.progress_chars[char_idx]} {progress_percent:.1f}% "
                           f"[{current_iter:,}/{total_iters:,}] {rate:.0f} итер/сек "
                           f"| Потоков: {self.workers} | {eta_str}")
            
            # Полностью очищаем строку и выводим новую информацию
            sys.stdout.write('\r' + ' ' * 120 + '\r')  # Сначала очищаем
            sys.stdout.write(progress_line)  # Затем выводим
            sys.stdout.flush()
            
            # Переход на новую строку при завершении
            if progress_percent >= 100:
                print()
        
        return callback


class CleanCallback:
    """Чистый callback для бенчмарка"""
    
    def __init__(self, workers: int):
        self.workers = workers
        self.start_time = None
        self.last_progress = -1
        self.progress_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def create_callback(self) -> Callable:
        """Создает callback функцию"""
        self.start_time = time.time()
        
        def callback(progress_percent: float, current_iter: int, total_iters: int):
            # Обновляем только если прогресс изменился значительно
            if int(progress_percent) == self.last_progress:
                return
            
            self.last_progress = int(progress_percent)
            
            # Расчет времени и скорости
            elapsed = time.time() - self.start_time
            rate = current_iter / elapsed if elapsed > 0 else 0
            
            # Расчет ETA
            if rate > 0:
                remaining_iters = total_iters - current_iter
                eta = remaining_iters / rate
                eta_str = f"ETA: {eta:.0f}сек"
            else:
                eta_str = "ETA: --"
            
            # Формируем строку
            char_idx = int(progress_percent) % len(self.progress_chars)
            progress_line = (f"{self.progress_chars[char_idx]} {progress_percent:.1f}% "
                           f"[{current_iter:,}/{total_iters:,}] {rate:.0f} итер/сек "
                           f"| Потоков: {self.workers} | {eta_str}")
            
            # Очищаем всю строку и выводим новую
            sys.stdout.write('\r' + ' ' * 150 + '\r')  # Полная очистка
            sys.stdout.write(progress_line)
            sys.stdout.flush()
            
            if progress_percent >= 100:
                print()  # Переход на новую строку при завершении
        
        return callback


class EnhancedPiGenerator:
    """Улучшенный генератор π с правильной многопоточностью"""
    
    def __init__(self, pi_generator: PiGenerator):
        self.pi_generator = pi_generator
        self.multi_core_info = MultiCoreInfo()
    
    def generate_pi_enhanced(self, pi_precision: int, use_gpu: bool = False, 
                           progress_callback: Optional[Callable] = None,
                           force_regenerate: bool = False,
                           auto_optimize: bool = True) -> str:
        """
        Генерирует π с улучшенной многопоточностью
        
        Args:
            pi_precision: количество цифр π
            use_gpu: использовать GPU
            progress_callback: callback для прогресса
            force_regenerate: принудительно перегенерировать
            auto_optimize: автоматически оптимизировать потоки
            
        Returns:
            строка с цифрами π
        """
        print("🚀 Улучшенная генерация π с автоматической оптимизацией...")
        
        # Определяем оптимальное количество потоков
        if auto_optimize:
            optimal_workers = self.multi_core_info.get_optimal_workers("pi_generation")
            available_cores = self.multi_core_info.get_available_cores_for_task(reserve_cores=1)
            
            # Выбираем между оптимальным и доступным
            num_workers = min(optimal_workers, available_cores)
            
            print(f"🖥️  Анализ системы:")
            print(f"   • Физических ядер: {self.multi_core_info.system_info['total_physical_cores']}")
            print(f"   • Доступно потоков: {self.multi_core_info.system_info['available_cores']}")
            print(f"   • Текущая загрузка: {self.multi_core_info.get_cpu_usage():.1f}%")
            print(f"   • Оптимально для π: {optimal_workers}")
            print(f"   • Будет использовано: {num_workers}")
        else:
            num_workers = mp.cpu_count()
            print(f"Используем {num_workers} потоков")
        
        # Создаем callback для прогресса с информацией о потоках
        if progress_callback is None:
            progress_callback = PiProgressCallback()
        
        start_time = time.time()
        extra_info = f"| Потоков: {num_workers} | CPU: {self.multi_core_info.get_cpu_usage():.1f}%"
        callback = progress_callback.create_callback(start_time, extra_info)
        
        try:
            # Генерируем π с улучшенными параметрами
            pi_digits = self.pi_generator.generate_pi_digits(
                pi_precision, use_gpu, callback, num_workers, force_regenerate
            )
            
            generation_time = time.time() - start_time
            
            # Выводим детальную статистику
            self._print_generation_statistics(pi_digits, generation_time, num_workers)
            
            return pi_digits
            
        except Exception as e:
            print(f"❌ Ошибка генерации π: {e}")
            # Fallback к однопоточной генерации
            print("🔄 Переход к однопоточной генерации...")
            return self.pi_generator.generate_pi_digits(
                pi_precision, use_gpu, progress_callback, 1, force_regenerate
            )
    
    def _print_generation_statistics(self, pi_digits: str, generation_time: float, 
                                   num_workers: int):
        """Выводит детальную статистику генерации"""
        digits_count = len(pi_digits)
        digits_per_sec = digits_count / generation_time if generation_time > 0 else 0
        
        print(f"\n✅ Генерация π завершена!")
        print(f"📈 СТАТИСТИКА:")
        print(f"   • Цифр сгенерировано: {digits_count:,}")
        print(f"   • Время: {generation_time:.2f} сек")
        print(f"   • Скорость: {digits_per_sec:.0f} цифр/сек")
        print(f"   • Потоков использовано: {num_workers}")
        
        # Эффективность
        theoretical_max = digits_per_sec * num_workers
        efficiency = (digits_per_sec / theoretical_max) * 100 if theoretical_max > 0 else 0
        print(f"   • Эффективность многопоточности: {efficiency:.1f}%")
        
        # Сравнение с однопоточным режимом
        single_thread_time = generation_time * num_workers  # Приблизительно
        speedup = single_thread_time / generation_time if generation_time > 0 else 1
        print(f"   • Ускорение: {speedup:.1f}x")
        
        # Рекомендации
        if efficiency < 50:
            print(f"⚠️  Низкая эффективность многопоточности")
            print(f"   💡 Рекомендуется: проверить настройки или использовать меньше потоков")
        elif efficiency > 80:
            print(f"🎉 Отличная эффективность многопоточности!")
        
        print(f"🎯 Прогноз для {digits_count//1000}K цифр: ~{generation_time:.1f} сек")
    
    def benchmark_threading(self, pi_precision: int = 100000) -> Dict:
        """
        Тестирует производительность с разным количеством потоков
        БОЛЬШИЕ объемы для реального тестирования многопоточности
        """
        print(f"🧪 Бенчмарк многопоточности для {pi_precision:,} цифр...")
        
        results = {}
        max_workers = self.multi_core_info.system_info['available_cores']
        
        # Для малых объемов тестируем меньше потоков
        if pi_precision < 10000:
            test_workers = [1, 2, 4, min(8, max_workers)]
        else:
            test_workers = [1, 2, 4, min(8, max_workers), min(16, max_workers), max_workers]
        
        test_workers = list(set(test_workers))  # Убираем дубликаты
        test_workers.sort()
        
        for i, workers in enumerate(test_workers):
            print(f"\n🔄 [{i+1}/{len(test_workers)}] Тест {workers} потоков...")
            
            try:
                print(f"   Запуск генерации π с {workers} потоками...")
                start_time = time.time()
                
                # Используем УНИВЕРСАЛЬНЫЙ callback
                progress_callback = PiProgressCallback()
                extra_info = f"{workers}thr"
                callback = progress_callback.create_callback(start_time, extra_info)
                
                pi_digits = self.pi_generator.generate_pi_digits(
                    pi_precision, False, callback, workers, True
                )
                test_time = time.time() - start_time
                
                results[workers] = {
                    'time': test_time,
                    'digits_per_sec': pi_precision / test_time,
                    'success': True
                }
                
                print(f"✅ Тест {workers} потоков завершен:")
                print(f"   • Время: {test_time:.2f} сек")
                print(f"   • Скорость: {pi_precision/test_time:.0f} цифр/сек")
                
            except Exception as e:
                print(f"❌ Тест {workers} потоков провален:")
                print(f"   • Ошибка: {e}")
                results[workers] = {
                    'time': float('inf'),
                    'digits_per_sec': 0,
                    'success': False,
                    'error': str(e)
                }
        
        # Анализ результатов
        self._analyze_benchmark_results(results)
        
        return results
    
    def _analyze_benchmark_results(self, results: Dict):
        """Анализирует результаты бенчмарка с объяснением производительности"""
        print(f"\n📊 АНАЛИЗ БЕНЧМАРКА:")
        print("=" * 60)
        
        successful_results = {k: v for k, v in results.items() if v['success']}
        
        if not successful_results:
            print("❌ Все тесты провалены")
            return
        
        # Находим лучший результат
        best_workers = max(successful_results.keys(), 
                          key=lambda k: successful_results[k]['digits_per_sec'])
        best_result = successful_results[best_workers]
        
        print(f"🏆 Лучший результат: {best_workers} потоков")
        print(f"   • Скорость: {best_result['digits_per_sec']:.0f} цифр/сек")
        print(f"   • Время: {best_result['time']:.2f} сек")
        
        # Сравнение с однопоточным
        if 1 in successful_results:
            single_speed = successful_results[1]['digits_per_sec']
            speedup = best_result['digits_per_sec'] / single_speed
            print(f"   • Ускорение: {speedup:.1f}x по сравнению с 1 потоком")
        
        # Детальный анализ каждого теста
        print(f"\n📈 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        for workers in sorted(successful_results.keys()):
            result = successful_results[workers]
            if 1 in successful_results:
                speedup = result['digits_per_sec'] / successful_results[1]['digits_per_sec']
                efficiency = (speedup / workers) * 100
                print(f"   {workers:2d} потоков: {result['time']:6.2f}сек, "
                      f"{result['digits_per_sec']:6.0f} цифр/сек, "
                      f"ускорение {speedup:.2f}x, эффективность {efficiency:.1f}%")
            else:
                print(f"   {workers:2d} потоков: {result['time']:6.2f}сек, "
                      f"{result['digits_per_sec']:6.0f} цифр/сек")
        
        # Анализ эффективности
        print(f"\n🔍 АНАЛИЗ ЭФФЕКТИВНОСТИ:")
        if 1 in successful_results and len(successful_results) > 1:
            single_speed = successful_results[1]['digits_per_sec']
            
            print(f"   • Однопоточный режим: {single_speed:.0f} цифр/сек (базовый)")
            
            for workers in sorted(successful_results.keys()):
                if workers > 1:
                    result = successful_results[workers]
                    speedup = result['digits_per_sec'] / single_speed
                    efficiency = (speedup / workers) * 100
                    
                    if efficiency > 80:
                        status = "🟢 Отлично"
                    elif efficiency > 50:
                        status = "🟡 Хорошо"
                    elif efficiency > 25:
                        status = "🟠 Удовлетворительно"
                    else:
                        status = "🔴 Плохо"
                    
                    print(f"   • {workers} потоков: {efficiency:.1f}% эффективности {status}")
        
        # Объяснение почему многопоточность может быть медленнее
        print(f"\n💡 АНАЛИЗ ПРОИЗВОДИТЕЛЬНОСТИ:")
        
        if len(successful_results) >= 2:
            # Проверяем есть ли проблема с многопоточностью
            two_thread_result = successful_results.get(2)
            single_thread_result = successful_results.get(1)
            
            if two_thread_result and single_thread_result:
                two_thread_speedup = two_thread_result['digits_per_sec'] / single_thread_result['digits_per_sec']
                
                if two_thread_speedup < 1.0:
                    print(f"   ⚠️  2 потока медленнее 1 ({two_thread_speedup:.2f}x)")
                    print(f"   📝 Возможные причины:")
                    print(f"      • Накладные расходы на создание процессов")
                    print(f"      • GIL (Global Interpreter Lock) в Python")
                    print(f"      • Недостаточный объем вычислений для распараллеливания")
                    print(f"      • Конкуренция за ресурсы памяти/CPU")
                    print(f"      • Проблемы с синхронизацией процессов")
                else:
                    print(f"   ✅ 2 потока быстрее 1 ({two_thread_speedup:.2f}x)")
        
        # Рекомендации по оптимизации
        print(f"\n🎯 РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ:")
        
        if 1 in successful_results:
            best_speedup = best_result['digits_per_sec'] / successful_results[1]['digits_per_sec']
            theoretical_best = best_workers
            actual_efficiency = (best_speedup / theoretical_best) * 100
            
            if actual_efficiency > 80:
                print(f"   • Используйте {best_workers} потоков - отличная эффективность!")
            elif actual_efficiency > 50:
                print(f"   • {best_workers} потоков дают хороший результат")
            elif actual_efficiency > 25:
                print(f"   • Рассмотрите {best_workers//2} потоков для лучшей эффективности")
            else:
                print(f"   • Многопоточность неэффективна - используйте 1 поток")
                print(f"   • Попробуйте увеличить объем вычислений для лучшего распараллеливания")
        
        # Технические рекомендации
        print(f"\n🔧 ТЕХНИЧЕСКИЕ СОВЕТЫ:")
        print(f"   • Для алгоритма Chudnovsky многопоточность сложна из-за зависимостей")
        print(f"   • BBP алгоритм лучше подходит для параллельных вычислений")
        print(f"   • Увеличьте precision до 1M+ цифр для лучшего распараллеливания")
        print(f"   • Проверьте использование памяти - может быть узким местом")
        
        print("=" * 60)
