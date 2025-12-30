#!/usr/bin/env python3
"""
Виртуальный векторный кеш для ускорения поиска в π
Использует numpy arrays и хеширование для быстрого доступа
"""

import numpy as np
import hashlib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import pickle
import os

@dataclass
class CacheEntry:
    """Элемент кеша"""
    positions: np.ndarray
    pattern_hash: str
    access_count: int = 0
    last_access: float = 0.0

class VectorCache:
    def __init__(self, max_size: int = 1000000, cache_file: str = "vector_cache.pkl"):
        self.max_size = max_size
        self.cache_file = cache_file
        self.cache: Dict[str, CacheEntry] = {}
        self.pi_digits_array: Optional[np.ndarray] = None
        self.hit_count = 0
        self.miss_count = 0
        
    def load_pi_digits(self, pi_digits: str) -> None:
        """Загружает π цифры в numpy array для векторных операций"""
        self.pi_digits_array = np.array(list(pi_digits), dtype=np.uint8)
        
    def get_positions(self, pattern: bytes) -> Optional[np.ndarray]:
        """Получает позиции паттерна из кеша"""
        pattern_hash = hashlib.sha256(pattern).hexdigest()
        
        if pattern_hash in self.cache:
            self.hit_count += 1
            entry = self.cache[pattern_hash]
            entry.access_count += 1
            return entry.positions
        
        self.miss_count += 1
        return None
        
    def cache_positions(self, pattern: bytes, positions: np.ndarray) -> None:
        """Сохраняет позиции паттерна в кеш"""
        pattern_hash = hashlib.sha256(pattern).hexdigest()
        
        # Проверяем размер кеша
        if len(self.cache) >= self.max_size:
            self._evict_lru()
            
        self.cache[pattern_hash] = CacheEntry(
            positions=positions,
            pattern_hash=pattern_hash,
            access_count=1
        )
        
    def vector_search(self, pattern: bytes) -> np.ndarray:
        """Векторизованный поиск паттерна в π"""
        if self.pi_digits_array is None:
            raise ValueError("π цифры не загружены")
            
        pattern_array = np.array(list(pattern.hex().upper()), dtype=np.uint8)
        pattern_len = len(pattern_array)
        pi_len = len(self.pi_digits_array)
        
        if pattern_len > pi_len:
            return np.array([])
            
        # Создаем sliding window view
        windows = np.lib.stride_tricks.sliding_window_view(
            self.pi_digits_array, pattern_len
        )
        
        # Векторизованное сравнение
        matches = np.all(windows == pattern_array, axis=1)
        positions = np.where(matches)[0]
        
        return positions
        
    def _evict_lru(self) -> None:
        """Удаляет наименее используемые элементы из кеша"""
        if not self.cache:
            return
            
        # Находим элемент с наименьшим количеством доступов
        lru_key = min(self.cache.keys(), 
                     key=lambda k: self.cache[k].access_count)
        del self.cache[lru_key]
        
    def get_stats(self) -> Dict[str, float]:
        """Возвращает статистику кеша"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'cache_size': len(self.cache),
            'max_size': self.max_size
        }
        
    def save_cache(self) -> None:
        """Сохраняет кеш в файл"""
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)
            
    def load_cache(self) -> None:
        """Загружает кеш из файла"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as f:
                self.cache = pickle.load(f)
                
    def clear_cache(self) -> None:
        """Очищает кеш"""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0
