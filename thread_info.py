#!/usr/bin/env python3
"""
Модуль для проверки информации о потоках и процессорах
"""

import multiprocessing as mp
import platform
import os

def get_system_info():
    """Возвращает детальную информацию о системе"""
    info = {
        'platform': f'{platform.system()} {platform.release()}',
        'processor': platform.processor(),
        'cpu_count_logical': mp.cpu_count(),
        'cpu_count_physical': None,
        'available_cores': None
    }
    
    # Получаем количество доступных ядер для текущего процесса
    try:
        info['available_cores'] = len(os.sched_getaffinity(0))
    except AttributeError:
        info['available_cores'] = info['cpu_count_logical']
    
    # Пытаемся получить количество физических ядер
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            physical_ids = set()
            for line in cpuinfo.split('\n'):
                if line.startswith('physical id'):
                    physical_ids.add(line.split(':')[1].strip())
            info['cpu_count_physical'] = len(physical_ids)
    except:
        info['cpu_count_physical'] = info['cpu_count_logical']
    
    return info

def print_thread_info():
    """Выводит информацию о потоках"""
    info = get_system_info()
    
    print('=== Информация о потоках и процессорах ===')
    print(f'Платформа: {info["platform"]}')
    print(f'Процессор: {info["processor"]}')
    print(f'Логических ядер (multiprocessing): {info["cpu_count_logical"]}')
    print(f'Физических ядер: {info["cpu_count_physical"]}')
    print(f'Доступно ядер процессу: {info["available_cores"]}')
    
    # Рекомендации по количеству потоков
    optimal_workers = min(info['available_cores'], 8)  # Ограничиваем до 8 для стабильности
    print(f'Рекомендуемое количество потоков: {optimal_workers}')
    print('=' * 50)

if __name__ == '__main__':
    print_thread_info()
