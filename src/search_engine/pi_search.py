#!/usr/bin/env python3
"""
Поисковый движок для поиска последовательностей данных в цифрах π
Поддерживает различные алгоритмы поиска и оптимизации
"""

import hashlib
import time
from typing import List, Tuple, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from dataclasses import dataclass

@dataclass
class SearchResult:
    """Результат поиска последовательности в π"""
    found: bool
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None
    data_hash: str = ""
    search_time: float = 0.0

class PiSearchEngine:
    def __init__(self, pi_generator):
        self.pi_generator = pi_generator
        self.cache = {}
        
    def search_sequence(self, data: bytes, pi_digits: str, 
                       algorithm: str = "auto") -> SearchResult:
        """
        Ищет последовательность данных в цифрах π
        
        Args:
            data: последовательность байт для поиска
            pi_digits: строка с цифрами π
            algorithm: алгоритм поиска (naive, rabin_karp, bloom, auto)
            
        Returns:
            SearchResult с информацией о найденной позиции
        """
        start_time = time.time()
        
        # Преобразуем данные в hex-представление
        hex_sequence = data.hex().upper()
        data_hash = hashlib.sha256(data).hexdigest()
        
        # Выбираем алгоритм
        if algorithm == "auto":
            algorithm = self._choose_algorithm(len(hex_sequence))
        
        # Ищем последовательность
        if algorithm == "naive":
            result = self._naive_search(hex_sequence, pi_digits)
        elif algorithm == "rabin_karp":
            result = self._rabin_karp_search(hex_sequence, pi_digits)
        elif algorithm == "bloom":
            result = self._bloom_filter_search(hex_sequence, pi_digits)
        else:
            raise ValueError(f"Неизвестный алгоритм: {algorithm}")
        
        search_time = time.time() - start_time
        
        return SearchResult(
            found=result[0],
            start_pos=result[1] if result[0] else None,
            end_pos=result[2] if result[0] else None,
            data_hash=data_hash,
            search_time=search_time
        )
    
    def _choose_algorithm(self, sequence_length: int) -> str:
        """Выбирает оптимальный алгоритм на основе длины последовательности"""
        if sequence_length <= 16:  # 8 байт
            return "naive"
        elif sequence_length <= 2048:  # 1 КБ
            return "rabin_karp"
        else:
            return "bloom"
    
    def _naive_search(self, pattern: str, text: str) -> Tuple[bool, int, int]:
        """Наивный поиск подстроки"""
        pos = text.find(pattern)
        if pos != -1:
            return True, pos, pos + len(pattern) - 1
        return False, -1, -1
    
    def _rabin_karp_search(self, pattern: str, text: str) -> Tuple[bool, int, int]:
        """Поиск Рабина-Карпа с хешированием"""
        if len(pattern) > len(text):
            return False, -1, -1
        
        # Простое число для хеширования
        prime = 101
        base = 16  # hex система
        
        pattern_hash = 0
        text_hash = 0
        h = 1
        
        # Предварительное вычисление h = base^(m-1) % prime
        for i in range(len(pattern) - 1):
            h = (h * base) % prime
        
        # Вычисляем хеши для первого окна
        for i in range(len(pattern)):
            pattern_hash = (base * pattern_hash + int(pattern[i], 16)) % prime
            text_hash = (base * text_hash + int(text[i], 16)) % prime
        
        # Скользим по тексту
        for i in range(len(text) - len(pattern) + 1):
            if pattern_hash == text_hash:
                # Проверяем точное совпадение
                if text[i:i+len(pattern)] == pattern:
                    return True, i, i + len(pattern) - 1
            
            # Вычисляем хеш для следующего окна
            if i < len(text) - len(pattern):
                text_hash = (base * (text_hash - int(text[i], 16) * h) + 
                           int(text[i + len(pattern)], 16)) % prime
                if text_hash < 0:
                    text_hash += prime
        
        return False, -1, -1
    
    def _bloom_filter_search(self, pattern: str, text: str) -> Tuple[bool, int, int]:
        """
        Поиск с использованием Bloom фильтра для предварительной фильтрации
        """
        # Упрощенная реализация - в реальном проекте здесь был бы полноценный Bloom filter
        return self._rabin_karp_search(pattern, text)
    
    def search_blocks_parallel(self, blocks: List[bytes], pi_digits: str,
                              num_workers: int = None) -> List[SearchResult]:
        """
        Параллельный поиск нескольких блоков
        
        Args:
            blocks: список блоков данных для поиска
            pi_digits: строка с цифрами π
            num_workers: количество рабочих потоков
            
        Returns:
            список SearchResult для каждого блока
        """
        if num_workers is None:
            num_workers = mp.cpu_count()
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for block in blocks:
                future = executor.submit(self.search_sequence, block, pi_digits)
                futures.append(future)
            
            results = []
            for future in futures:
                results.append(future.result())
        
        return results
    
    def adaptive_block_search(self, data: bytes, pi_digits: str,
                            min_block_size: int = 4, max_block_size: int = 16) -> List[SearchResult]:
        """
        Адаптивный поиск с автоматическим подбором размера блока
        
        Args:
            data: исходные данные
            pi_digits: строка с цифрами π
            min_block_size: минимальный размер блока в байтах
            max_block_size: максимальный размер блока в байтах
            
        Returns:
            список SearchResult для найденных блоков
        """
        results = []
        data_hex = data.hex().upper()
        
        # Пробуем разные размеры блоков
        for block_size in range(min_block_size, max_block_size + 1):
            block_hex_size = block_size * 2  # hex символы
            
            if len(data_hex) < block_hex_size:
                continue
            
            # Разбиваем на блоки
            blocks = []
            for i in range(0, len(data_hex), block_hex_size):
                if i + block_hex_size <= len(data_hex):
                    block_hex = data_hex[i:i+block_hex_size]
                    blocks.append(bytes.fromhex(block_hex))
            
            # Ищем блоки
            block_results = self.search_blocks_parallel(blocks, pi_digits)
            
            # Добавляем найденные блоки
            for i, result in enumerate(block_results):
                if result.found:
                    # Сохраняем информацию о позиции в исходных данных
                    original_pos = i * block_size
                    result.data_hash = f"block_{original_pos}_{block_size}"
                    results.append(result)
        
        return results
    
    def get_search_statistics(self, results: List[SearchResult]) -> Dict:
        """
        Возвращает статистику поиска
        
        Args:
            results: список результатов поиска
            
        Returns:
            словарь со статистикой
        """
        total_blocks = len(results)
        found_blocks = sum(1 for r in results if r.found)
        total_time = sum(r.search_time for r in results)
        
        if found_blocks > 0:
            avg_time = total_time / found_blocks
        else:
            avg_time = 0
        
        return {
            'total_blocks': total_blocks,
            'found_blocks': found_blocks,
            'success_rate': found_blocks / total_blocks if total_blocks > 0 else 0,
            'total_search_time': total_time,
            'average_search_time': avg_time
        }


class BloomFilter:
    """Упрощенная реализация Bloom фильтра"""
    
    def __init__(self, size: int = 1000000, hash_count: int = 7):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [False] * size
        self.hash_functions = self._generate_hash_functions()
    
    def _generate_hash_functions(self):
        """Генерирует несколько хеш-функций"""
        functions = []
        for i in range(self.hash_count):
            def hash_func(item, seed=i):
                return (hash(item) + seed) % self.size
            functions.append(hash_func)
        return functions
    
    def add(self, item: str):
        """Добавляет элемент в фильтр"""
        for hash_func in self.hash_functions:
            index = hash_func(item)
            self.bit_array[index] = True
    
    def __contains__(self, item: str) -> bool:
        """Проверяет наличие элемента (может давать ложноположительные результаты)"""
        for hash_func in self.hash_functions:
            index = hash_func(item)
            if not self.bit_array[index]:
                return False
        return True


if __name__ == "__main__":
    # Тестирование поискового движка
    from pi_generator import PiGenerator
    
    generator = PiGenerator()
    search_engine = PiSearchEngine(generator)
    
    # Генерируем π для тестов
    pi_digits = generator.generate_pi_digits(100000)
    
    # Тестовые данные
    test_data = b"Hello, World!"
    
    # Ищем последовательность
    result = search_engine.search_sequence(test_data, pi_digits)
    
    print(f"Результат поиска:")
    print(f"Найдено: {result.found}")
    if result.found:
        print(f"Позиция: {result.start_pos}-{result.end_pos}")
    print(f"Время поиска: {result.search_time:.4f} сек")
    print(f"Хеш данных: {result.data_hash}")
