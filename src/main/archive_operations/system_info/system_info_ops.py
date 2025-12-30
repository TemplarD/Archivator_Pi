#!/usr/bin/env python3
"""
Операции системной информации для Pi-Archiver Ultra
"""

import multiprocessing as mp
from pathlib import Path
from typing import Dict


class SystemInfoOperations:
    """Класс для операций системной информации"""
    
    def get_optimal_workers(self) -> int:
        """
        Определяет оптимальное количество потоков для системы
        
        Returns:
            оптимальное количество потоков
        """
        try:
            import os
            available_cores = len(os.sched_getaffinity(0))
        except AttributeError:
            available_cores = mp.cpu_count()
        
        # Анализируем архитектуру процессоров
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                
                # Количество физических процессоров
                physical_ids = set()
                for line in cpuinfo.split('\n'):
                    if line.startswith('physical id'):
                        physical_ids.add(line.split(':')[1].strip())
                
                # Количество ядер на процессор
                cores_per_cpu = None
                for line in cpuinfo.split('\n'):
                    if line.startswith('cpu cores'):
                        cores_per_cpu = int(line.split(':')[1].strip())
                        break
                
                physical_processors = len(physical_ids)
                total_physical_cores = len(physical_ids) * (cores_per_cpu or 1)
                
        except Exception:
            # Запасной вариант
            physical_processors = 1
            total_physical_cores = available_cores
        
        # Рекомендации по количеству потоков
        if total_physical_cores >= 20:
            # Для мощных систем (2+ процессора)
            optimal_workers = min(total_physical_cores, 16)
        else:
            # Для обычных систем
            optimal_workers = min(available_cores, 8)
        
        return optimal_workers
    
    def print_system_info(self, num_workers: int = None):
        """
        Выводит информацию о системе и потоках
        
        Args:
            num_workers: используемое количество потоков
        """
        info = self._get_system_info()
        
        print('=== Информация о потоках и процессорах ===')
        print(f'Платформа: {info["platform"]}')
        print(f'Процессор: {info["processor"]}')
        print(f'Физических процессоров: {info["physical_processors"]}')
        print(f'Ядер на процессор: {info["cores_per_processor"]}')
        print(f'Всего физических ядер: {info["total_physical_cores"]}')
        print(f'Логических потоков: {info["cpu_count_logical"]}')
        print(f'Доступно потоков процессу: {info["available_cores"]}')
        
        if num_workers:
            print(f'Будет использоваться потоков: {num_workers}')
            efficiency = (num_workers / info['available_cores']) * 100
            print(f'Эффективность использования: {efficiency:.1f}%')
        
        optimal_workers = self.get_optimal_workers()
        print(f'Рекомендуемое количество потоков: {optimal_workers}')
        print('=' * 55)
    
    def _get_system_info(self) -> Dict:
        """Возвращает информацию о системе и потоках"""
        import platform
        
        info = {
            'platform': f'{platform.system()} {platform.release()}',
            'processor': platform.processor(),
            'cpu_count_logical': mp.cpu_count(),
            'available_cores': mp.cpu_count()
        }
        
        # Получаем количество доступных ядер для текущего процесса
        try:
            import os
            info['available_cores'] = len(os.sched_getaffinity(0))
        except AttributeError:
            pass
        
        # Анализируем архитектуру процессоров
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                
                # Количество физических процессоров
                physical_ids = set()
                for line in cpuinfo.split('\n'):
                    if line.startswith('physical id'):
                        physical_ids.add(line.split(':')[1].strip())
                
                # Количество ядер на процессор
                cores_per_cpu = None
                for line in cpuinfo.split('\n'):
                    if line.startswith('cpu cores'):
                        cores_per_cpu = int(line.split(':')[1].strip())
                        break
                
                info['physical_processors'] = len(physical_ids)
                info['cores_per_processor'] = cores_per_cpu
                info['total_physical_cores'] = len(physical_ids) * (cores_per_cpu or 1)
                
        except Exception:
            # Запасной вариант
            info['physical_processors'] = 1
            info['cores_per_processor'] = info['cpu_count_logical']
            info['total_physical_cores'] = info['cpu_count_logical']
        
        return info
