#!/usr/bin/env python3
"""
Адаптивная система поиска в π для Pi-Archiver
Умное уменьшение размера блоков и оптимизация диапазонов
"""

from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import time
import math

@dataclass
class SearchAttempt:
    """Информация о попытке поиска"""
    block_size: int
    range_start: int
    range_end: int
    success: bool
    time_spent: float
    found_position: Optional[Tuple[int, int]] = None

@dataclass
class AdaptiveSearchConfig:
    """Конфигурация адаптивного поиска"""
    initial_block_size_range: Tuple[int, int] = (2, 24)  # РАСШИРЕН ДИАПАЗОН
    min_block_size: int = 1  # УМЕНЬШЕНО ДО 1 БАЙТА!
    max_block_size: int = 48  # УВЕЛИЧЕНО ДО 48 БАЙТ
    max_search_attempts: int = 6  # УВЕЛИЧЕНО ДО 6 ПОПЫТОК
    range_expansion_factor: float = 2.0
    adaptive_threshold: float = 0.3  # Если найдено < 30% блоков, уменьшаем размер

class AdaptiveSearchEngine:
    """Адаптивная система поиска блоков в π"""
    
    def __init__(self, pi_generator, config: AdaptiveSearchConfig = None):
        self.pi_generator = pi_generator
        self.config = config or AdaptiveSearchConfig()
        self.search_history: List[SearchAttempt] = []
        
    def adaptive_block_search(self, block: bytes, pi_digits: str, 
                             block_id: int, max_pi_digits: int = None) -> Tuple[bool, List[SearchAttempt], Optional[Tuple[int, int]], bool]:
        """
        Адаптивный поиск блока с уменьшением размера при неудаче
        
        Returns:
            (found, attempts, position, backup_used)
        """
        attempts = []
        backup_used = False
        found_position = None
        
        # Начинаем с оптимального размера блока
        current_block_size = min(len(block), self.config.initial_block_size_range[1])
        
        # Определяем доступный диапазон π
        available_pi_digits = len(pi_digits) if max_pi_digits is None else min(len(pi_digits), max_pi_digits)
        
        for attempt_num in range(self.config.max_search_attempts):
            if current_block_size < self.config.min_block_size:
                break
                
            # Берем префикс блока текущего размера
            search_block = block[:current_block_size]
            
            # Определяем диапазон поиска
            search_start, search_end = self._calculate_search_range(
                current_block_size, available_pi_digits, attempt_num
            )
            
            # Выполняем поиск
            start_time = time.time()
            result = self._search_in_range(search_block, pi_digits, search_start, search_end)
            search_time = time.time() - start_time
            
            # Записываем попытку
            attempt = SearchAttempt(
                block_size=current_block_size,
                range_start=search_start,
                range_end=search_end,
                success=result.found,
                time_spent=search_time,
                found_position=(result.start_pos, result.end_pos) if result.found else None
            )
            attempts.append(attempt)
            
            if result.found:
                found_position = attempt.found_position
                break
            
            # Уменьшаем размер блока для следующей попытки
            current_block_size = max(self.config.min_block_size, current_block_size - 1)
        
        # Если не нашли даже минимальный блок, используем бэкап
        if not attempts[-1].success if attempts else True:
            backup_used = True
        
        return (found_position is not None, attempts, found_position, backup_used)
    
    def _calculate_search_range(self, block_size: int, available_digits: int, 
                               attempt_num: int) -> Tuple[int, int]:
        """
        Вычисляет оптимальный диапазон поиска
        
        Args:
            block_size: размер блока в байтах
            available_digits: доступное количество цифр π
            attempt_num: номер попытки
            
        Returns:
            (start_pos, end_pos) в цифрах π
        """
        # Базовый диапазон - все доступные цифры
        if attempt_num == 0:
            return (0, available_digits)
        
        # Для последующих попыток используем расширенный диапазон
        # Чем меньше блок, тем больше диапазон для поиска
        expansion = self.config.range_expansion_factor ** attempt_num
        
        # Вычисляем эффективный диапазон
        max_range = min(available_digits * expansion, available_digits)
        
        # Для маленьких блоков можно использовать весь диапазон
        if block_size <= 4:
            return (0, available_digits)
        
        # Для больших блоков ограничиваем диапазон
        range_limit = available_digits // (block_size // 4)
        effective_range = min(max_range, range_limit)
        
        return (0, effective_range)
    
    def _search_in_range(self, block: bytes, pi_digits: str, 
                        start_pos: int, end_pos: int):
        """Поиск блока в указанном диапазоне π"""
        try:
            from src.search_engine.pi_search import PiSearchEngine
        except ImportError:
            # Если не нашли, пробуем прямой импорт
            from search_engine.pi_search import PiSearchEngine
        
        search_engine = PiSearchEngine(self.pi_generator)
        
        # Ограничиваем π цифры нужным диапазоном
        limited_pi = pi_digits[start_pos:end_pos]
        
        # Выполняем поиск
        result = search_engine.search_sequence(block, limited_pi)
        
        # Корректируем позиции если найдено
        if result.found:
            result.start_pos += start_pos
            result.end_pos += start_pos
        
        return result
    
    def optimize_batch_search(self, blocks: List[bytes], pi_digits: str,
                              progress_callback=None) -> List[Tuple[bool, List[SearchAttempt], Optional[Tuple[int, int]], bool]]:
        """
        Оптимизированный пакетный поиск с адаптацией под успешность
        
        Args:
            blocks: список блоков для поиска
            pi_digits: цифры π
            progress_callback: функция прогресса
            
        Returns:
            список результатов для каждого блока
        """
        results = []
        total_blocks = len(blocks)
        
        # Анализируем первые несколько блоков для определения оптимальной стратегии
        sample_size = min(10, total_blocks)
        sample_results = []
        
        print(f"🔍 Анализ первых {sample_size} блоков для оптимизации...")
        
        for i in range(sample_size):
            block_result = self.adaptive_block_search(blocks[i], pi_digits, i)
            sample_results.append(block_result)
            
            if progress_callback:
                progress = ((i + 1) / sample_size) * 10  # 10% на анализ
                progress_callback(progress, i + 1, total_blocks, None)
        
        # Оцениваем успешность
        success_rate = sum(1 for r in sample_results if r[0]) / len(sample_results)
        
        print(f"📊 Успешность поиска: {success_rate:.1%}")
        
        # Корректируем стратегию в зависимости от успешности
        if success_rate < self.config.adaptive_threshold:
            print("🔄 Низкая успешность, переключаемся на уменьшенные блоки...")
            self.config.initial_block_size_range = (
                max(self.config.min_block_size, self.config.initial_block_size_range[0] - 2),
                max(self.config.min_block_size + 2, self.config.initial_block_size_range[1] - 4)
            )
        elif success_rate > 0.8:
            print("✅ Высокая успешность, можно использовать большие блоки...")
            self.config.initial_block_size_range = (
                min(self.config.max_block_size, self.config.initial_block_size_range[0] + 2),
                min(self.config.max_block_size, self.config.initial_block_size_range[1] + 4)
            )
        
        # Обрабатываем оставшиеся блоки с оптимизированной стратегией
        remaining_blocks = blocks[sample_size:]
        
        for i, block in enumerate(remaining_blocks):
            block_result = self.adaptive_block_search(block, pi_digits, sample_size + i)
            results.append(block_result)
            
            if progress_callback:
                progress = 10 + ((i + 1) / len(remaining_blocks)) * 90  # 90% на основную обработку
                progress_callback(progress, sample_size + i + 1, total_blocks, None)
        
        # Объединяем результаты
        all_results = sample_results + results
        
        # Статистика по адаптивному поиску
        adaptive_successes = sum(1 for r in all_results if len(r[1]) > 1 and r[0])
        print(f"🎯 Адаптивный поиск помог в {adaptive_successes} случаях из {total_blocks}")
        
        return all_results
    
    def get_search_statistics(self) -> Dict:
        """Возвращает статистику поиска"""
        if not self.search_history:
            return {}
        
        successful_searches = [s for s in self.search_history if s.success]
        
        return {
            'total_searches': len(self.search_history),
            'successful_searches': len(successful_searches),
            'success_rate': len(successful_searches) / len(self.search_history),
            'avg_search_time': sum(s.time_spent for s in self.search_history) / len(self.search_history),
            'avg_block_size': sum(s.block_size for s in self.search_history) / len(self.search_history),
            'most_successful_block_size': self._find_most_successful_size(),
            'total_search_range': sum(s.range_end - s.range_start for s in self.search_history)
        }
    
    def _find_most_successful_size(self) -> int:
        """Находит самый успешный размер блока"""
        size_success = {}
        
        for search in self.search_history:
            if search.block_size not in size_success:
                size_success[search.block_size] = {'total': 0, 'success': 0}
            
            size_success[search.block_size]['total'] += 1
            if search.success:
                size_success[search.block_size]['success'] += 1
        
        # Находим размер с лучшей успешностью
        best_size = max(size_success.keys(), 
                       key=lambda x: size_success[x]['success'] / size_success[x]['total'])
        
        return best_size

class SmartRangeOptimizer:
    """Умная оптимизация диапазонов поиска"""
    
    def __init__(self):
        self.range_performance: Dict[Tuple[int, int], float] = {}
        
    def optimize_search_ranges(self, block_sizes: List[int], available_digits: int,
                              performance_history: Dict = None) -> Dict[int, Tuple[int, int]]:
        """
        Оптимизирует диапазоны поиска для разных размеров блоков
        
        Args:
            block_sizes: размеры блоков
            available_digits: доступное количество цифр π
            performance_history: история производительности
            
        Returns:
            словарь {block_size: (start_pos, end_pos)}
        """
        optimized_ranges = {}
        
        for block_size in set(block_sizes):
            # Базовый диапазон - оптимизирован для разных размеров
            if block_size == 1:
                # 1 байт - ищем во всем диапазоне, очень высокая вероятность найти
                range_size = available_digits
            elif block_size <= 4:
                # Маленькие блоки (2-4 байта) - ищем в 90% диапазона
                range_size = int(available_digits * 0.9)
            elif block_size <= 8:
                # Средние блоки (5-8 байт) - 75% диапазона
                range_size = int(available_digits * 0.75)
            elif block_size <= 16:
                # Большие блоки (9-16 байт) - 60% диапазона
                range_size = int(available_digits * 0.6)
            else:
                # Очень большие блоки (>16 байт) - 40% диапазона
                range_size = int(available_digits * 0.4)
            
            # Корректируем на основе истории производительности
            if performance_history and block_size in performance_history:
                performance_factor = performance_history[block_size]
                if performance_factor > 0.8:  # Хорошая производительность
                    range_size = int(range_size * 1.2)
                elif performance_factor < 0.3:  # Плохая производительность
                    range_size = int(range_size * 0.8)
            
            # Ограничиваем доступными цифрами
            range_size = min(range_size, available_digits)
            
            optimized_ranges[block_size] = (0, range_size)
        
        return optimized_ranges
    
    def update_performance(self, block_size: int, range_size: int, 
                          success_rate: float, avg_time: float) -> None:
        """Обновляет информацию о производительности диапазона"""
        key = (block_size, range_size)
        performance_score = success_rate / (1 + avg_time)  # Компромисс между успешностью и временем
        
        self.range_performance[key] = performance_score

def create_adaptive_search_engine(pi_generator, **config_kwargs) -> AdaptiveSearchEngine:
    """Создает настроенный адаптивный поисковик"""
    config = AdaptiveSearchConfig(**config_kwargs)
    return AdaptiveSearchEngine(pi_generator, config)
