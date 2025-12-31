#!/usr/bin/env python3
"""
Многопоточный поисковик в π с использованием C++ генерации
Максимальная загрузка CPU для поиска блоков
"""

import threading
import time
import hashlib
from typing import List, Tuple, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing as mp
from dataclasses import dataclass

@dataclass
class SearchTask:
    """Задача поиска блока"""
    task_id: int
    block_data: bytes
    hex_sequence: str
    pi_digits: str
    thread_id: int = None

@dataclass
class SearchWorkerResult:
    """Результат поиска от рабочего потока"""
    task_id: int
    found: bool
    start_pos: Optional[int]
    end_pos: Optional[int]
    search_time: float
    thread_id: int
    attempts: int

class MultiThreadedPiSearcher:
    """Многопоточный поисковик в π с максимальной загрузкой CPU"""
    
    def __init__(self, num_threads: int = None):
        self.num_threads = num_threads or min(mp.cpu_count() - 1, 32)  # Оставляем 1 для системы
        self.search_stats = {
            'total_searches': 0,
            'successful_searches': 0,
            'total_time': 0.0,
            'thread_utilization': {}
        }
        
    def search_blocks_parallel(self, blocks: List[bytes], pi_digits: str,
                              progress_callback=None) -> List[SearchWorkerResult]:
        """
        Параллельный поиск всех блоков с максимальной загрузкой CPU
        
        Args:
            blocks: список блоков для поиска
            pi_digits: цифры π
            progress_callback: функция прогресса
            
        Returns:
            список результатов поиска
        """
        print(f"🔥 Многопоточный поиск {len(blocks)} блоков с {self.num_threads} потоками...")
        print(f"💪 Используем 100% CPU для поиска в π!")
        
        # Подготавливаем задачи
        tasks = []
        for i, block in enumerate(blocks):
            hex_sequence = block.hex().upper()
            task = SearchTask(
                task_id=i,
                block_data=block,
                hex_sequence=hex_sequence,
                pi_digits=pi_digits
            )
            tasks.append(task)
        
        # Запускаем многопоточный поиск
        results = []
        completed_count = 0
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            # Отправляем все задачи на выполнение
            future_to_task = {
                executor.submit(self._search_worker, task): task
                for task in tasks
            }
            
            # Собираем результаты по мере завершения
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                    completed_count += 1
                    
                    # Обновляем прогресс
                    if progress_callback:
                        progress = (completed_count / len(tasks)) * 100
                        elapsed = time.time() - start_time
                        if completed_count < len(tasks):
                            estimated_total = elapsed * len(tasks) / completed_count
                            remaining = estimated_total - elapsed
                            progress_callback(progress, completed_count, len(tasks), remaining)
                        else:
                            progress_callback(progress, completed_count, len(tasks), 0)
                            
                except Exception as e:
                    print(f"❌ Ошибка в потоке: {e}")
                    # Создаем результат с ошибкой
                    task = future_to_task[future]
                    error_result = SearchWorkerResult(
                        task_id=task.task_id,
                        found=False,
                        start_pos=None,
                        end_pos=None,
                        search_time=0.0,
                        thread_id=-1,
                        attempts=0
                    )
                    results.append(error_result)
                    completed_count += 1
        
        # Сортируем результаты по task_id
        results.sort(key=lambda x: x.task_id)
        
        # Обновляем статистику
        self.search_stats['total_searches'] += len(results)
        self.search_stats['successful_searches'] += sum(1 for r in results if r.found)
        self.search_stats['total_time'] += time.time() - start_time
        
        return results
    
    def _search_worker(self, task: SearchTask) -> SearchWorkerResult:
        """
        Рабочая функция для поиска одного блока в отдельном потоке
        
        Args:
            task: задача поиска
            
        Returns:
            результат поиска
        """
        thread_id = threading.get_ident()
        start_time = time.time()
        
        # Адаптивный поиск с уменьшением размера блока
        current_hex = task.hex_sequence
        current_block = task.block_data
        attempts = 0
        max_attempts = 6  # Увеличиваем попытки для 1-48 байт
        
        while attempts < max_attempts and len(current_hex) >= 2:  # Минимум 2 hex символа (1 байт)
            attempts += 1
            
            # Ищем текущую последовательность
            position = self._find_sequence_in_pi(current_hex, task.pi_digits)
            
            if position is not None:
                # Нашли! Возвращаем результат
                search_time = time.time() - start_time
                end_pos = position + len(current_hex) // 2  # Конвертируем hex в байты
                
                return SearchWorkerResult(
                    task_id=task.task_id,
                    found=True,
                    start_pos=position,
                    end_pos=end_pos,
                    search_time=search_time,
                    thread_id=thread_id,
                    attempts=attempts
                )
            
            # Не нашли, уменьшаем размер блока
            if len(current_hex) > 2:
                current_hex = current_hex[:-2]  # Убираем 1 байт (2 hex символа)
                current_block = current_block[:-1]
            else:
                break
        
        # Не нашли после всех попыток
        search_time = time.time() - start_time
        return SearchWorkerResult(
            task_id=task.task_id,
            found=False,
            start_pos=None,
            end_pos=None,
            search_time=search_time,
            thread_id=thread_id,
            attempts=attempts
        )
    
    def _find_sequence_in_pi(self, hex_sequence: str, pi_digits: str) -> Optional[int]:
        """
        Быстрый поиск последовательности в π
        
        Args:
            hex_sequence: hex-последовательность для поиска
            pi_digits: цифры π
            
        Returns:
            позиция первого вхождения или None
        """
        # Используем встроенный поиск Python (оптимизирован в C)
        try:
            position = pi_digits.find(hex_sequence)
            return position if position != -1 else None
        except Exception:
            return None
    
    def search_blocks_adaptive_parallel(self, blocks: List[bytes], pi_digits: str,
                                       progress_callback=None) -> List[SearchWorkerResult]:
        """
        Адаптивный параллельный поиск с группировкой по размерам
        """
        print(f"🚀 Адаптивный многопоточный поиск {len(blocks)} блоков...")
        
        # Группируем блоки по размерам для оптимизации
        size_groups = {}
        for i, block in enumerate(blocks):
            size = len(block)
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append((i, block))
        
        all_results = []
        completed_count = 0
        
        # Обрабатываем каждую группу оптимальным количеством потоков
        for size, group_blocks in size_groups.items():
            print(f"🔍 Поиск {len(group_blocks)} блоков размером {size} байт...")
            
            # Определяем оптимальное количество потоков для этого размера
            optimal_threads = min(self.num_threads, len(group_blocks))
            if size <= 2:
                optimal_threads = min(self.num_threads, len(group_blocks))
            elif size <= 4:
                optimal_threads = min(self.num_threads // 2, len(group_blocks))
            elif size <= 8:
                optimal_threads = min(self.num_threads // 4, len(group_blocks))
            else:
                optimal_threads = min(self.num_threads // 8, len(group_blocks), 8)
            
            # Создаем временный поисковик
            temp_searcher = MultiThreadedPiSearcher(optimal_threads)
            
            # Подготавливаем задачи для этой группы
            group_tasks = []
            for block_id, block in group_blocks:
                hex_sequence = block.hex().upper()
                task = SearchTask(
                    task_id=block_id,
                    block_data=block,
                    hex_sequence=hex_sequence,
                    pi_digits=pi_digits
                )
                group_tasks.append(task)
            
            # Выполняем поиск для этой группы
            group_results = temp_searcher.search_blocks_parallel(
                [task.block_data for task in group_tasks], 
                pi_digits,
                lambda p, c, t, r: self._update_group_progress(p, c, t, r, completed_count, len(blocks), progress_callback)
            )
            
            # Корректируем ID результатов
            for i, result in enumerate(group_results):
                result.task_id = group_tasks[i].task_id
                all_results.append(result)
            
            completed_count += len(group_results)
        
        # Сортируем результаты по task_id
        all_results.sort(key=lambda x: x.task_id)
        
        return all_results
    
    def _update_group_progress(self, group_progress: float, group_completed: int, 
                             group_total: int, group_remaining: float,
                             total_completed: int, total_blocks: int,
                             progress_callback):
        """Обновляет общий прогресс с учетом прогресса группы"""
        if progress_callback:
            total_progress = (total_completed / total_blocks) * 100
            progress_callback(total_progress, total_completed, total_blocks, group_remaining)
    
    def get_search_stats(self) -> Dict:
        """Возвращает статистику поиска"""
        if self.search_stats['total_searches'] > 0:
            success_rate = self.search_stats['successful_searches'] / self.search_stats['total_searches']
            avg_time = self.search_stats['total_time'] / self.search_stats['total_searches']
        else:
            success_rate = 0.0
            avg_time = 0.0
            
        return {
            'total_searches': self.search_stats['total_searches'],
            'successful_searches': self.search_stats['successful_searches'],
            'success_rate': success_rate,
            'total_time': self.search_stats['total_time'],
            'avg_time_per_search': avg_time,
            'threads_used': self.num_threads,
            'throughput': self.search_stats['total_searches'] / self.search_stats['total_time'] if self.search_stats['total_time'] > 0 else 0
        }

def create_multithreaded_searcher(num_threads: int = None) -> MultiThreadedPiSearcher:
    """Создает многопоточный поисковик"""
    return MultiThreadedPiSearcher(num_threads)
