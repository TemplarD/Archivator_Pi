#!/usr/bin/env python3
"""
Мониторинг загрузки процессора и потоков
"""

import time
import threading
import multiprocessing as mp
from typing import Dict, List, Optional
import psutil

class CPUMonitor:
    """Монитор загрузки процессора"""
    
    def __init__(self):
        self.monitoring = False
        self.cpu_usage = []
        self.thread_count = 0
        self.start_time = None
        
    def start_monitoring(self, thread_count: int = None):
        """Начать мониторинг"""
        self.monitoring = True
        self.cpu_usage = []
        self.thread_count = thread_count or mp.cpu_count()
        self.start_time = time.time()
        
        # Запускаем мониторинг в отдельном потоке
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print(f"🔍 Начат мониторинг CPU (потоки: {self.thread_count})")
    
    def stop_monitoring(self) -> Dict:
        """Остановить мониторинг и вернуть статистику"""
        self.monitoring = False
        
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=1)
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        stats = {
            'thread_count': self.thread_count,
            'elapsed_time': elapsed,
            'cpu_samples': len(self.cpu_usage),
            'avg_cpu_usage': sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0,
            'max_cpu_usage': max(self.cpu_usage) if self.cpu_usage else 0,
            'min_cpu_usage': min(self.cpu_usage) if self.cpu_usage else 0,
            'cpu_usage_samples': self.cpu_usage
        }
        
        return stats
    
    def _monitor_loop(self):
        """Цикл мониторинга"""
        while self.monitoring:
            try:
                # Общая загрузка CPU
                cpu_percent = psutil.cpu_percent(interval=0.1)
                self.cpu_usage.append(cpu_percent)
                
                # Небольшая задержка
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Ошибка мониторинга CPU: {e}")
                break
    
    def print_stats(self, stats: Dict):
        """Вывод статистики"""
        print(f"\n📊 СТАТИСТИКА ЗАГРУЗКИ CPU:")
        print(f"Потоки: {stats['thread_count']}")
        print(f"Время: {stats['elapsed_time']:.2f}s")
        print(f"Замеров: {stats['cpu_samples']}")
        print(f"Средняя загрузка: {stats['avg_cpu_usage']:.1f}%")
        print(f"Максимальная: {stats['max_cpu_usage']:.1f}%")
        print(f"Минимальная: {stats['min_cpu_usage']:.1f}%")
        
        # Анализ эффективности
        expected_max = min(100.0, stats['thread_count'] * 100.0 / mp.cpu_count())
        efficiency = stats['avg_cpu_usage'] / expected_max * 100 if expected_max > 0 else 0
        
        print(f"Эффективность многопоточности: {efficiency:.1f}%")
        
        if stats['avg_cpu_usage'] < 50 and stats['thread_count'] > 1:
            print("⚠️ НИЗКАЯ ЗАГРУЗКА CPU - потоки могут не работать параллельно!")
        elif stats['avg_cpu_usage'] > 80:
            print("✅ ХОРОШАЯ ЗАГРУЗКА CPU - потоки работают эффективно")
        else:
            print("🔄 СРЕДНЯЯ ЗАГРУЗКА CPU - проверьте конфигурацию")

def test_cpu_usage():
    """Тест загрузки CPU"""
    print("🧪 ТЕСТ ЗАГРУЗКИ CPU")
    print("=" * 50)
    
    # Тест 1: Однопоточный
    print("\n🔹 Тест 1: Однопоточная нагрузка")
    monitor = CPUMonitor()
    monitor.start_monitoring(1)
    
    # Создаем интенсивную однопоточную нагрузку
    def cpu_burn():
        end = time.time() + 3
        while time.time() < end:
            _ = [i**2 for i in range(1000)]
    
    cpu_burn()
    
    stats1 = monitor.stop_monitoring()
    monitor.print_stats(stats1)
    
    # Тест 2: Многопоточный
    print("\n🔸 Тест 2: Многопоточная нагрузка")
    monitor = CPUMonitor()
    monitor.start_monitoring(4)
    
    # Создаем интенсивную многопоточную нагрузку
    threads = []
    for i in range(4):
        t = threading.Thread(target=cpu_burn)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    stats2 = monitor.stop_monitoring()
    monitor.print_stats(stats2)
    
    # Сравнение
    print(f"\n📈 СРАВНЕНИЕ:")
    print(f"1 поток: {stats1['avg_cpu_usage']:.1f}%")
    print(f"4 потока: {stats2['avg_cpu_usage']:.1f}%")
    print(f"Ускорение: {stats2['avg_cpu_usage'] / stats1['avg_cpu_usage']:.2f}x")

if __name__ == "__main__":
    test_cpu_usage()
