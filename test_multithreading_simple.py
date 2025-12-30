#!/usr/bin/env python3
"""
Простой тест многопоточности с мониторингом CPU через системные утилиты
Использует универсальный прогресс-бар
"""

import sys
import time
import subprocess
import threading
import os
sys.path.append('src')

from pi_generator import UniversalPiGenerator, AlgorithmType

# Импортируем универсальный прогресс-бар
try:
    from utils.progress_bar import create_progress_bar
    PROGRESS_BAR_AVAILABLE = True
except ImportError:
    PROGRESS_BAR_AVAILABLE = False
    print("⚠️ Универсальный прогресс-бар недоступен")

class SimpleCPUMonitor:
    def __init__(self):
        self.monitoring = True
        self.cpu_samples = []
        self.thread = None
    
    def start_monitoring(self):
        """Начинает мониторинг CPU"""
        self.monitoring = True
        self.cpu_samples = []
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_monitoring(self):
        """Останавливает мониторинг"""
        self.monitoring = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Цикл мониторинга через top"""
        while self.monitoring:
            try:
                # Получаем загрузку CPU через top
                result = subprocess.run(['top', '-bn1'], capture_output=True, text=True, timeout=2)
                
                # Парсим вывод top для получения общей загрузки CPU
                lines = result.stdout.split('\n')
                for line in lines:
                    if '%Cpu(s):' in line:
                        # Extract CPU usage from line like: %Cpu(s): 25.0 us, 10.0 sy,  5.0 id, 60.0 wa,  0.0 hi,  0.0 si,  0.0 st
                        cpu_line = line.split('%Cpu(s):')[1].strip()
                        # Get user + system usage
                        parts = cpu_line.split(',')
                        user_cpu = float(parts[0].split()[0])
                        system_cpu = float(parts[1].split()[0])
                        total_cpu = user_cpu + system_cpu
                        
                        self.cpu_samples.append({
                            'time': time.time(),
                            'total_cpu': total_cpu,
                            'user_cpu': user_cpu,
                            'system_cpu': system_cpu
                        })
                        break
                
                time.sleep(1.0)  # Замеряем каждую секунду
                
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, IndexError, ValueError):
                # Если top не сработал, пробуем другой метод
                try:
                    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=2)
                    # Простая оценка по количеству процессов Python
                    python_processes = result.stdout.count('python')
                    self.cpu_samples.append({
                        'time': time.time(),
                        'total_cpu': min(100, python_processes * 25),  # Очень грубая оценка
                        'user_cpu': min(100, python_processes * 25),
                        'system_cpu': 0
                    })
                except:
                    pass
                
                time.sleep(1.0)
    
    def get_stats(self):
        """Возвращает статистику мониторинга"""
        if not self.cpu_samples:
            return {}
        
        total_cpu = [s['total_cpu'] for s in self.cpu_samples]
        user_cpu = [s['user_cpu'] for s in self.cpu_samples]
        system_cpu = [s['system_cpu'] for s in self.cpu_samples]
        
        return {
            'max_total_cpu': max(total_cpu),
            'avg_total_cpu': sum(total_cpu) / len(total_cpu),
            'max_user_cpu': max(user_cpu),
            'avg_user_cpu': sum(user_cpu) / len(user_cpu),
            'max_system_cpu': max(system_cpu),
            'avg_system_cpu': sum(system_cpu) / len(system_cpu),
            'samples': len(self.cpu_samples)
        }

def test_multithreading_simple():
    """Простой тест многопоточности с мониторингом"""
    
    print("🧪 Тест многопоточности с мониторингом CPU")
    print("=" * 60)
    
    generator = UniversalPiGenerator(cache_dir='/tmp/test_pi_simple')
    
    # Тестируем разное количество потоков
    precision = 15000  # Уменьшим для скорости
    print(f"\nТочность: {precision:,} цифр")
    
    results = []
    
    for workers in [1, 2, 4]:
        print(f"\n{'='*60}")
        print(f"📊 Тест с {workers} поток(ами)")
        print(f"{'='*60}")
        
        # Очищаем кэш
        generator.clear_cache()
        
        # Начинаем мониторинг CPU
        monitor = SimpleCPUMonitor()
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
            
            if cpu_stats:
                print(f"\n🖥️ Статистика CPU:")
                print(f"  Макс. загрузка: {cpu_stats.get('max_total_cpu', 0):.1f}%")
                print(f"  Средняя загрузка: {cpu_stats.get('avg_total_cpu', 0):.1f}%")
                print(f"  Макс. user: {cpu_stats.get('max_user_cpu', 0):.1f}%")
                print(f"  Макс. system: {cpu_stats.get('max_system_cpu', 0):.1f}%")
                print(f"  Замеров: {cpu_stats.get('samples', 0)}")
                
                # Эффективность использования CPU
                cpu_efficiency = cpu_stats.get('max_total_cpu', 0) / (workers * 100) * 100
                print(f"  Эффективность: {cpu_efficiency:.1f}%")
            else:
                print(f"\n🖥️ Не удалось получить статистику CPU")
            
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
        
        print("Потоки | Время (с) | Скорость | Max CPU | Эффект. | Правильно")
        print("-" * 55)
        
        baseline_time = results[0]['time']
        
        for result in results:
            workers = result['workers']
            time_elapsed = result['time']
            speed = result['speed']
            cpu_stats = result['cpu_stats']
            max_cpu = cpu_stats.get('max_total_cpu', 0) if cpu_stats else 0
            efficiency = max_cpu / (workers * 100) * 100 if workers > 0 and max_cpu > 0 else 0
            correct = '✅' if result['correct'] else '❌'
            
            speedup = baseline_time / time_elapsed
            
            print(f"{workers:6} | {time_elapsed:8.3f} | {speed:7.0f} | {max_cpu:6.1f}% | {efficiency:6.1f}% | {correct}")
        
        # Выводы
        print(f"\n🎯 Выводы:")
        
        # Находим лучший по скорости
        best_speed = max(results, key=lambda x: x['speed'])
        print(f"  Лучшая скорость: {best_speed['workers']} потоков ({best_speed['speed']:.0f} цифр/сек)")
        
        # Анализ эффективности
        print(f"\n🔍 Анализ эффективности:")
        for result in results:
            workers = result['workers']
            cpu_stats = result['cpu_stats']
            if cpu_stats:
                max_cpu = cpu_stats.get('max_total_cpu', 0)
                theoretical_max = workers * 100
                efficiency = max_cpu / theoretical_max * 100
                
                if efficiency < 30:
                    print(f"  {workers} потоков: Низкая эффективность ({efficiency:.1f}%)")
                elif efficiency < 60:
                    print(f"  {workers} потоков: Средняя эффективность ({efficiency:.1f}%)")
                else:
                    print(f"  {workers} потоков: Хорошая эффективность ({efficiency:.1f}%)")
            else:
                print(f"  {workers} потоков: Нет данных о CPU")

if __name__ == "__main__":
    test_multithreading_simple()
