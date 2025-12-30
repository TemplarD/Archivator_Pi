#!/usr/bin/env python3
"""
Тест многопоточности с мониторингом CPU и прогресс-барами
"""

import sys
import time
import psutil
import threading
import os
sys.path.append('src')

from pi_generator import UniversalPiGenerator, AlgorithmType

class CPUMonitor:
    def __init__(self):
        self.monitoring = True
        self.cpu_usage = []
        self.thread = None
    
    def start_monitoring(self):
        """Начинает мониторинг CPU"""
        self.monitoring = True
        self.cpu_usage = []
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_monitoring(self):
        """Останавливает мониторинг"""
        self.monitoring = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Цикл мониторинга"""
        while self.monitoring:
            # Общая загрузка CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Загрузка по каждому ядру
            cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # Количество процессов
            process_count = len(psutil.pids())
            
            self.cpu_usage.append({
                'time': time.time(),
                'total': cpu_percent,
                'cores': cpu_per_core,
                'processes': process_count
            })
            
            time.sleep(0.5)
    
    def get_stats(self):
        """Возвращает статистику мониторинга"""
        if not self.cpu_usage:
            return {}
        
        total_cpu = [entry['total'] for entry in self.cpu_usage]
        max_cpu = max(total_cpu)
        avg_cpu = sum(total_cpu) / len(total_cpu)
        
        # Максимальная загрузка ядер
        max_core_usage = max(max(entry['cores']) for entry in self.cpu_usage)
        
        # Среднее количество процессов
        avg_processes = sum(entry['processes'] for entry in self.cpu_usage) / len(self.cpu_usage)
        
        return {
            'max_total_cpu': max_cpu,
            'avg_total_cpu': avg_cpu,
            'max_core_cpu': max_core_usage,
            'avg_processes': avg_processes,
            'samples': len(self.cpu_usage)
        }

def test_multithreading_with_monitoring():
    """Тест многопоточности с мониторингом CPU"""
    
    print("🧪 Тест многопоточности с мониторингом CPU")
    print("=" * 60)
    
    generator = UniversalPiGenerator(cache_dir='/tmp/test_pi_monitoring')
    
    # Тестируем разное количество потоков
    precision = 20000  # Уменьшим для скорости теста
    print(f"\nТочность: {precision:,} цифр")
    
    results = []
    
    for workers in [1, 2, 4, 8]:
        print(f"\n{'='*60}")
        print(f"📊 Тест с {workers} поток(ами)")
        print(f"{'='*60}")
        
        # Очищаем кэш
        generator.clear_cache()
        
        # Начинаем мониторинг CPU
        monitor = CPUMonitor()
        monitor.start_monitoring()
        
        try:
            # Запускаем генерацию
            start_time = time.time()
            pi_digits = generator.generate_pi(
                precision, 
                algorithm_type=AlgorithmType.MULTI_THREAD, 
                num_workers=workers
            )
            elapsed = time.time() - start_time
            
            # Останавливаем мониторинг
            monitor.stop_monitoring()
            cpu_stats = monitor.get_stats()
            
            # Сохраняем результаты
            results.append({
                'workers': workers,
                'time': elapsed,
                'speed': precision / elapsed,
                'cpu_stats': cpu_stats,
                'correct': pi_digits.startswith('14159265358979323846')
            })
            
            # Выводим результаты
            print(f"\n📈 Результаты:")
            print(f"  Время: {elapsed:.3f} сек")
            print(f"  Скорость: {precision/elapsed:.0f} цифр/сек")
            print(f"  Правильно: {'✅' if pi_digits.startswith('14159265358979323846') else '❌'}")
            
            print(f"\n🖥️ Статистика CPU:")
            print(f"  Макс. загрузка CPU: {cpu_stats.get('max_total_cpu', 0):.1f}%")
            print(f"  Средняя загрузка CPU: {cpu_stats.get('avg_total_cpu', 0):.1f}%")
            print(f"  Макс. загрузка ядра: {cpu_stats.get('max_core_cpu', 0):.1f}%")
            print(f"  Среднее процессов: {cpu_stats.get('avg_processes', 0):.0f}")
            print(f"  Замеров: {cpu_stats.get('samples', 0)}")
            
            # Эффективность использования CPU
            cpu_efficiency = cpu_stats.get('max_total_cpu', 0) / (workers * 100) * 100
            print(f"  Эффективность CPU: {cpu_efficiency:.1f}%")
            
        except KeyboardInterrupt:
            print(f"\n⚠️ Тест прерван")
            monitor.stop_monitoring()
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            monitor.stop_monitoring()
    
    # Анализ результатов
    if results:
        print(f"\n{'='*60}")
        print("📊 Сводная таблица результатов")
        print(f"{'='*60}")
        
        print("Потоки | Время (с) | Скорость | Max CPU | Max Core | Эффект. | Правильно")
        print("-" * 70)
        
        baseline_time = results[0]['time']
        
        for result in results:
            workers = result['workers']
            time_elapsed = result['time']
            speed = result['speed']
            max_cpu = result['cpu_stats'].get('max_total_cpu', 0)
            max_core = result['cpu_stats'].get('max_core_cpu', 0)
            efficiency = max_cpu / (workers * 100) * 100 if workers > 0 else 0
            correct = '✅' if result['correct'] else '❌'
            
            speedup = baseline_time / time_elapsed
            
            print(f"{workers:6} | {time_elapsed:8.3f} | {speed:7.0f} | {max_cpu:6.1f}% | {max_core:8.1f}% | {efficiency:6.1f}% | {correct}")
        
        # Выводы
        print(f"\n🎯 Выводы:")
        
        # Находим лучший по скорости
        best_speed = max(results, key=lambda x: x['speed'])
        print(f"  Лучшая скорость: {best_speed['workers']} потоков ({best_speed['speed']:.0f} цифр/сек)")
        
        # Находим лучший по эффективности CPU
        best_efficiency = max(results, key=lambda x: x['cpu_stats'].get('max_total_cpu', 0))
        print(f"  Макс. загрузка CPU: {best_efficiency['workers']} потоков ({best_efficiency['cpu_stats'].get('max_total_cpu', 0):.1f}%)")
        
        # Анализ эффективности
        print(f"\n🔍 Анализ эффективности:")
        for result in results:
            workers = result['workers']
            max_cpu = result['cpu_stats'].get('max_total_cpu', 0)
            theoretical_max = workers * 100
            efficiency = max_cpu / theoretical_max * 100
            
            if efficiency < 50:
                print(f"  {workers} потоков: Низкая эффективность ({efficiency:.1f}%) - возможно,瓶颈 в I/O или GIL")
            elif efficiency < 80:
                print(f"  {workers} потоков: Средняя эффективность ({efficiency:.1f}%)")
            else:
                print(f"  {workers} потоков: Хорошая эффективность ({efficiency:.1f}%)")

if __name__ == "__main__":
    test_multithreading_with_monitoring()
