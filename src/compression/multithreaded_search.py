#!/usr/bin/env python3
"""
Многопоточный поисковик в π для Pi-Archiver
Использует C++ генерацию и многопоточный поиск блоков
"""

import threading
import time
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing as mp

@dataclass
class SearchTask:
    """Задача поиска блока"""
    block_id: int
    block_data: bytes
    search_range: Tuple[int, int]
    max_attempts: int = 4

@dataclass
class SearchResult:
    """Результат поиска блока"""
    block_id: int
    found: bool
    position: Optional[Tuple[int, int]]
    attempts_made: int
    search_time: float
    thread_id: int

class MultiThreadedPiSearch:
    """Многопоточный поисковик в π"""
    
    def __init__(self, pi_generator, num_threads: int = None):
        self.pi_generator = pi_generator
        self.num_threads = num_threads or min(mp.cpu_count() - 1, 32)  # Оставляем 1 поток для системы
        self.search_stats = {
            'total_searches': 0,
            'successful_searches': 0,
            'total_time': 0.0
        }
        
    def search_blocks_parallel(self, blocks: List[bytes], pi_digits: str,
                              progress_callback=None) -> List[SearchResult]:
        """
        Параллельный поиск всех блоков в π
        
        Args:
            blocks: список блоков для поиска
            pi_digits: цифры π
            progress_callback: функция прогресса
            
        Returns:
            список результатов поиска
        """
        print(f"🔍 Многопоточный поиск {len(blocks)} блоков с {self.num_threads} потоками...")
        
        # Создаем задачи для каждого блока
        tasks = []
        for i, block in enumerate(blocks):
            task = SearchTask(
                block_id=i,
                block_data=block,
                search_range=(0, len(pi_digits)),
                max_attempts=4
            )
            tasks.append(task)
        
        # Запускаем многопоточный поиск
        results = []
        completed_count = 0
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            # Отправляем все задачи на выполнение
            future_to_task = {
                executor.submit(self._search_block_worker, task, pi_digits): task
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
                    error_result = SearchResult(
                        block_id=task.block_id,
                        found=False,
                        position=None,
                        attempts_made=0,
                        search_time=0.0,
                        thread_id=-1
                    )
                    results.append(error_result)
                    completed_count += 1
        
        # Сортируем результаты по block_id
        results.sort(key=lambda x: x.block_id)
        
        # Обновляем статистику
        self.search_stats['total_searches'] += len(results)
        self.search_stats['successful_searches'] += sum(1 for r in results if r.found)
        self.search_stats['total_time'] += time.time() - start_time
        
        return results
    
    def _search_block_worker(self, task: SearchTask, pi_digits: str) -> SearchResult:
        """
        Рабочая функция для поиска одного блока в отдельном потоке
        
        Args:
            task: задача поиска
            pi_digits: цифры π
            
        Returns:
            результат поиска
        """
        thread_id = threading.get_ident()
        start_time = time.time()
        
        # Адаптивный поиск с уменьшением размера блока
        current_block = task.block_data
        search_start, search_end = task.search_range
        
        for attempt in range(task.max_attempts):
            if len(current_block) < 1:
                break
                
            # Ищем текущий блок в указанном диапазоне
            position = self._search_in_range(current_block, pi_digits, search_start, search_end)
            
            if position is not None:
                # Нашли! Возвращаем результат
                search_time = time.time() - start_time
                return SearchResult(
                    block_id=task.block_id,
                    found=True,
                    position=position,
                    attempts_made=attempt + 1,
                    search_time=search_time,
                    thread_id=thread_id
                )
            
            # Не нашли, уменьшаем размер блока для следующей попытки
            if len(current_block) > 1:
                current_block = current_block[:-1]  # Уменьшаем на 1 байт
            else:
                break
        
        # Не нашли после всех попыток
        search_time = time.time() - start_time
        return SearchResult(
            block_id=task.block_id,
            found=False,
            position=None,
            attempts_made=task.max_attempts,
            search_time=search_time,
            thread_id=thread_id
        )
    
    def _search_in_range(self, block: bytes, pi_digits: str, 
                        start_pos: int, end_pos: int) -> Optional[Tuple[int, int]]:
        """
        Поиск блока в указанном диапазоне π
        
        Args:
            block: блок для поиска
            pi_digits: цифры π
            start_pos: начальная позиция в цифрах
            end_pos: конечная позиция в цифрах
            
        Returns:
            позиция найденного блока или None
        """
        try:
            from src.search_engine.pi_search import PiSearchEngine
        except ImportError:
            from search_engine.pi_search import PiSearchEngine
        
        # Ограничиваем π цифры нужным диапазоном
        limited_pi = pi_digits[start_pos:end_pos]
        
        # Создаем поисковик
        search_engine = PiSearchEngine(self.pi_generator)
        
        # Выполняем поиск
        result = search_engine.search_sequence(block, limited_pi)
        
        if result.found:
            # Корректируем позиции с учетом смещения
            adjusted_start = result.start_pos + start_pos
            adjusted_end = result.end_pos + start_pos
            return (adjusted_start, adjusted_end)
        
        return None
    
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
            'threads_used': self.num_threads
        }

class OptimizedMultiThreadedSearch(MultiThreadedPiSearch):
    """Оптимизированный многопоточный поисковик с умным распределением"""
    
    def __init__(self, pi_generator, num_threads: int = None):
        super().__init__(pi_generator, num_threads)
        self.performance_cache = {}  # Кэш производительности для разных размеров блоков
        
    def search_blocks_parallel(self, blocks: List[bytes], pi_digits: str,
                              progress_callback=None) -> List[SearchResult]:
        """
        Оптимизированный параллельный поиск с умным распределением
        """
        print(f"🚀 Оптимизированный многопоточный поиск {len(blocks)} блоков с {self.num_threads} потоками...")
        
        # Анализируем размеры блоков для оптимизации
        block_sizes = [len(block) for block in blocks]
        size_distribution = self._analyze_block_sizes(block_sizes)
        
        print(f"📊 Распределение размеров блоков: {size_distribution}")
        
        # Группируем блоки по размерам для оптимизации
        size_groups = self._group_blocks_by_size(blocks)
        
        # Ищем каждую группу оптимальным способом
        all_results = []
        completed_count = 0
        
        for size, group_blocks in size_groups.items():
            print(f"🔍 Поиск {len(group_blocks)} блоков размером {size} байт...")
            
            # Определяем оптимальное количество потоков для этого размера
            optimal_threads = self._get_optimal_threads_for_size(size, len(group_blocks))
            
            # Создаем временный поисковик с оптимальным количеством потоков
            temp_searcher = MultiThreadedPiSearch(self.pi_generator, optimal_threads)
            
            # Выполняем поиск для этой группы
            group_results = temp_searcher.search_blocks_parallel(
                group_blocks, pi_digits, 
                lambda p, c, t, r: self._update_group_progress(p, c, t, r, completed_count, len(blocks), progress_callback)
            )
            
            all_results.extend(group_results)
            completed_count += len(group_results)
            
            # Обновляем кэш производительности
            success_rate = sum(1 for r in group_results if r.found) / len(group_results)
            self.performance_cache[size] = success_rate
        
        # Сортируем результаты по block_id
        all_results.sort(key=lambda x: x.block_id)
        
        return all_results
    
    def _analyze_block_sizes(self, block_sizes: List[int]) -> Dict[str, int]:
        """Анализирует распределение размеров блоков"""
        size_counts = {}
        for size in block_sizes:
            if size <= 2:
                key = "1-2 байта"
            elif size <= 4:
                key = "3-4 байта"
            elif size <= 8:
                key = "5-8 байт"
            elif size <= 16:
                key = "9-16 байт"
            else:
                key = f">{16} байт"
            
            size_counts[key] = size_counts.get(key, 0) + 1
        
        return size_counts
    
    def _group_blocks_by_size(self, blocks: List[bytes]) -> Dict[int, List[bytes]]:
        """Группирует блоки по размерам"""
        size_groups = {}
        for block in blocks:
            size = len(block)
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(block)
        
        return size_groups
    
    def _get_optimal_threads_for_size(self, block_size: int, block_count: int) -> int:
        """Определяет оптимальное количество потоков для размера блока"""
        # Чем меньше блоки, тем больше потоков нужно
        if block_size <= 2:
            return min(self.num_threads, block_count)
        elif block_size <= 4:
            return min(self.num_threads // 2, block_count)
        elif block_size <= 8:
            return min(self.num_threads // 4, block_count)
        else:
            return min(self.num_threads // 8, block_count, 8)  # Максимум 8 для больших блоков
    
    def _update_group_progress(self, group_progress: float, group_completed: int, 
                             group_total: int, group_remaining: float,
                             total_completed: int, total_blocks: int,
                             progress_callback):
        """Обновляет общий прогресс с учетом прогресса группы"""
        if progress_callback:
            total_progress = (total_completed / total_blocks) * 100
            progress_callback(total_progress, total_completed, total_blocks, group_remaining)

def create_optimized_search_engine(pi_generator, num_threads: int = None) -> OptimizedMultiThreadedSearch:
    """Создает оптимизированный поисковик"""
    return OptimizedMultiThreadedSearch(pi_generator, num_threads)
