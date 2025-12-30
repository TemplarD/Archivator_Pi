#!/usr/bin/env python3
"""
Расширенная системная информация для многопроцессорных систем
"""

import multiprocessing as mp
import os
from pathlib import Path
from typing import Dict, List, Tuple
import platform

# Опциональный импорт psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class MultiCoreInfo:
    """Класс для анализа многопроцессорных систем"""
    
    def __init__(self):
        self.system_info = self._get_detailed_system_info()
    
    def get_optimal_workers(self, task_type: str = "general") -> int:
        """
        Определяет оптимальное количество потоков для разных типов задач
        
        Args:
            task_type: тип задачи (general, cpu_intensive, io_intensive, pi_generation)
            
        Returns:
            оптимальное количество потоков
        """
        available_cores = self.system_info['available_cores']
        total_physical_cores = self.system_info['total_physical_cores']
        physical_processors = self.system_info['physical_processors']
        
        if task_type == "pi_generation":
            # Для генерации π - используем все доступные ядра
            return min(available_cores, total_physical_cores * 2)
        elif task_type == "cpu_intensive":
            # CPU интенсивные задачи - количество физических ядер
            return total_physical_cores
        elif task_type == "io_intensive":
            # IO интенсивные задачи - можно больше потоков
            return min(available_cores * 2, total_physical_cores * 4)
        else:  # general
            # Общие задачи - баланс
            if total_physical_cores >= 20:
                return min(total_physical_cores, 16)
            else:
                return min(available_cores, 8)
    
    def get_cpu_usage(self) -> float:
        """Возвращает текущую загрузку CPU"""
        if PSUTIL_AVAILABLE:
            return psutil.cpu_percent(interval=1)
        else:
            # Запасной вариант без psutil
            try:
                with open('/proc/loadavg', 'r') as f:
                    load_avg = float(f.read().split()[0])
                    return (load_avg / self.system_info['total_physical_cores']) * 100
            except:
                return 0.0  # Не можем определить
    
    def get_available_cores_for_task(self, reserve_cores: int = 1) -> int:
        """
        Возвращает количество ядер доступных для задачи с резервом
        
        Args:
            reserve_cores: сколько ядер зарезервировать
            
        Returns:
            доступные ядра
        """
        available = self.system_info['available_cores']
        return max(1, available - reserve_cores)
    
    def print_detailed_system_info(self, current_workers: int = None):
        """
        Выводит подробную информацию о системе
        
        Args:
            current_workers: текущее количество используемых потоков
        """
        info = self.system_info
        
        print('🖥️  ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О СИСТЕМЕ')
        print('=' * 60)
        print(f'Платформа: {info["platform"]}')
        print(f'Процессор: {info["processor"]}')
        print(f'Архитектура: {info["architecture"]}')
        print(f'Физических процессоров: {info["physical_processors"]}')
        print(f'Ядер на процессор: {info["cores_per_processor"]}')
        print(f'Всего физических ядер: {info["total_physical_cores"]}')
        print(f'Логических потоков: {info["cpu_count_logical"]}')
        print(f'Доступно потоков процессу: {info["available_cores"]}')
        print(f'Текущая загрузка CPU: {self.get_cpu_usage():.1f}%')
        
        if current_workers:
            efficiency = (current_workers / info['available_cores']) * 100
            utilization = (current_workers / info['total_physical_cores']) * 100
            print(f'Используется потоков: {current_workers}')
            print(f'Эффективность использования доступных: {efficiency:.1f}%')
            print(f'Утилизация физических ядер: {utilization:.1f}%')
        
        print('\n🎯 ОПТИМАЛЬНОЕ КОЛИЧЕСТВО ПОТОКОВ:')
        print(f'  • Общие задачи: {self.get_optimal_workers("general")}')
        print(f'  • Генерация π: {self.get_optimal_workers("pi_generation")}')
        print(f'  • CPU интенсивные: {self.get_optimal_workers("cpu_intensive")}')
        print(f'  • IO интенсивные: {self.get_optimal_workers("io_intensive")}')
        
        print('\n💡 РЕКОМЕНДАЦИИ:')
        if info['total_physical_cores'] >= 20:
            print('  • Мощная многопроцессорная система detected')
            print('  • Рекомендуется использовать все физические ядра для π')
        elif info['total_physical_cores'] >= 8:
            print('  • Высокопроизводительная система')
            print('  • Можно использовать 6-8 потоков')
        else:
            print('  • Обичная система')
            print('  • Рекомендуется 4 потока или меньше')
        
        print('=' * 60)
    
    def _get_detailed_system_info(self) -> Dict:
        """Возвращает подробную информацию о системе"""
        info = {
            'platform': f'{platform.system()} {platform.release()}',
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'cpu_count_logical': mp.cpu_count(),
            'available_cores': mp.cpu_count()
        }
        
        # Получаем количество доступных ядер для текущего процесса
        try:
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
                
                # Дополнительная информация
                info['cpu_model'] = self._get_cpu_model(cpuinfo)
                info['cpu_freq'] = self._get_cpu_frequency(cpuinfo)
                
        except Exception:
            # Запасной вариант
            info['physical_processors'] = 1
            info['cores_per_processor'] = info['cpu_count_logical']
            info['total_physical_cores'] = info['cpu_count_logical']
            info['cpu_model'] = 'Unknown'
            info['cpu_freq'] = 'Unknown'
        
        return info
    
    def _get_cpu_model(self, cpuinfo: str) -> str:
        """Получает модель процессора"""
        for line in cpuinfo.split('\n'):
            if line.startswith('model name'):
                return line.split(':')[1].strip()
        return 'Unknown'
    
    def _get_cpu_frequency(self, cpuinfo: str) -> str:
        """Получает частоту процессора"""
        for line in cpuinfo.split('\n'):
            if line.startswith('cpu MHz'):
                return f"{float(line.split(':')[1].strip()):.0f} MHz"
        return 'Unknown'
    
    def get_core_topology(self) -> List[Dict]:
        """
        Возвращает топологию ядер процессора
        
        Returns:
            список информации о каждом ядре
        """
        cores = []
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                
                # Разбираем информацию о каждом процессоре
                processors = cpuinfo.split('\n\n')
                for proc in processors:
                    if 'processor' in proc:
                        core_info = {}
                        for line in proc.split('\n'):
                            if ':' in line:
                                key, value = line.split(':', 1)
                                core_info[key.strip()] = value.strip()
                        cores.append(core_info)
        except Exception:
            pass
        
        return cores
