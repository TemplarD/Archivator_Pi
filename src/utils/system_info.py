#!/usr/bin/env python3
"""
Утилиты для определения системных ресурсов и потоков
"""

import os
import multiprocessing as mp
import platform
from typing import Dict, Any

def get_system_thread_info() -> Dict[str, Any]:
    """
    Возвращает информацию о потоках в системе
    
    Returns:
        Dict с информацией о CPU и потоках
    """
    info = {
        'platform': platform.platform(),
        'processor': platform.processor(),
        'cpu_count': mp.cpu_count(),
        'logical_cores': None,
        'physical_cores': None,
        'max_workers_recommended': None,
        'max_workers_safe': None
    }
    
    # Определяем физические и логические ядра
    try:
        if platform.system() == "Linux":
            # Для Linux читаем /proc/cpuinfo
            with open('/proc/cpuinfo', 'r') as f:
                lines = f.readlines()
            
            physical_cores = set()
            logical_cores = 0
            
            for line in lines:
                if line.strip().startswith('physical id'):
                    physical_cores.add(line.split(':')[1].strip())
                elif line.strip().startswith('processor'):
                    logical_cores += 1
            
            info['physical_cores'] = len(physical_cores) if physical_cores else mp.cpu_count()
            info['logical_cores'] = logical_cores
            
        elif platform.system() == "Darwin":  # macOS
            import subprocess
            result = subprocess.run(['sysctl', '-n', 'hw.physicalcpu'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                info['physical_cores'] = int(result.stdout.strip())
            
            result = subprocess.run(['sysctl', '-n', 'hw.logicalcpu'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                info['logical_cores'] = int(result.stdout.strip())
                
        elif platform.system() == "Windows":
            import psutil
            info['physical_cores'] = psutil.cpu_count(logical=False)
            info['logical_cores'] = psutil.cpu_count(logical=True)
            
    except Exception as e:
        print(f"Не удалось определить детальную информацию о CPU: {e}")
        # Fallback значения
        info['physical_cores'] = mp.cpu_count()
        info['logical_cores'] = mp.cpu_count()
    
    # Рекомендуемые значения для потоков
    logical = info['logical_cores'] or mp.cpu_count()
    physical = info['physical_cores'] or mp.cpu_count()
    
    # Для CPU-интенсивных задач (Chudnovsky)
    info['max_workers_recommended'] = logical  # 1 поток на логическое ядро
    
    # Для безопасности оставляем 1 ядро для системы
    info['max_workers_safe'] = max(1, logical - 1)
    
    # Абсолютный максимум (если пользователь хочет все ядра)
    info['max_workers_absolute'] = logical
    
    return info

def validate_num_workers(num_workers: int, max_workers: int = None) -> int:
    """
    Проверяет и корректирует количество потоков
    
    Args:
        num_workers: запрошенное количество потоков
        max_workers: максимально допустимое количество
        
    Returns:
        скорректированное количество потоков
    """
    if max_workers is None:
        system_info = get_system_thread_info()
        max_workers = system_info['max_workers_safe']
    
    if num_workers <= 0:
        print(f"⚠️ Количество потоков должно быть >= 1, используем 1")
        return 1
    
    if num_workers > max_workers:
        print(f"⚠️ Запрошено {num_workers} потоков, доступно: {max_workers}")
        print(f"   Используем максимум: {max_workers}")
        return max_workers
    
    return num_workers

def print_thread_info():
    """Выводит информацию о потоках системы"""
    info = get_system_thread_info()
    
    print("🖥️ ИНФОРМАЦИЯ О СИСТЕМЕ ПОТОКОВ:")
    print("=" * 50)
    print(f"Платформа: {info['platform']}")
    print(f"Процессор: {info['processor']}")
    print(f"Физические ядра: {info['physical_cores']}")
    print(f"Логические ядра: {info['logical_cores']}")
    print(f"Всего CPU: {info['cpu_count']}")
    print()
    print("🚀 РЕКОМЕНДАЦИИ ПО ПОТОКАМ:")
    print(f"Рекомендовано: {info['max_workers_recommended']} потоков")
    print(f"Безопасно: {info['max_workers_safe']} потоков")
    print(f"Абсолютный максимум: {info['max_workers_absolute']} потоков")
    print("=" * 50)

if __name__ == "__main__":
    print_thread_info()
