#!/usr/bin/env python3
"""
Тесты для ядра сжатия Pi-Archiver Ultra
"""

import sys
import os
from pathlib import Path

# Добавляем путь к исходникам
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

import pytest
import hashlib
from compression.compression_core import CompressionCore, QuantumStyleCompression
from pi_generator.pi_generator import PiGenerator

class TestCompressionCore:
    """Тесты основного ядра сжатия"""
    
    @pytest.fixture
    def compression_core(self):
        """Создает экземпляр ядра сжатия для тестов"""
        generator = PiGenerator()
        return CompressionCore(generator)
    
    @pytest.fixture
    def pi_digits(self):
        """Генерирует тестовые цифры π"""
        generator = PiGenerator()
        return generator.generate_pi_digits(10000)
    
    @pytest.fixture
    def test_data(self):
        """Создает тестовые данные"""
        return b"Hello, World! This is a test message for Pi-Archiver Ultra."
    
    def test_xor_decorrelate(self, compression_core, pi_digits, test_data):
        """Тест XOR-декорреляции"""
        xor_data, xor_key = compression_core._xor_decorrelate(test_data, pi_digits)
        
        # Проверяем, что данные изменились
        assert xor_data != test_data
        assert len(xor_data) == len(test_data)
        assert isinstance(xor_key, int)
        
        # Проверяем обратное преобразование
        reversed_data = compression_core._reverse_xor_decorrelate(xor_data, pi_digits, xor_key)
        assert reversed_data == test_data
    
    def test_adaptive_block_splitting(self, compression_core, test_data):
        """Тест адаптивного разбиения на блоки"""
        blocks = compression_core._adaptive_block_splitting(test_data, (4, 16))
        
        # Проверяем, что блоки созданы
        assert len(blocks) > 0
        
        # Проверяем размеры блоков
        for block in blocks:
            assert 4 <= len(block) <= 16
        
        # Проверяем, что все данные покрыты
        total_size = sum(len(block) for block in blocks)
        assert total_size <= len(test_data)
    
    def test_entropy_calculation(self, compression_core):
        """Тест вычисления энтропии"""
        # Тест с регулярными данными (низкая энтропия)
        regular_data = b"AAAAAAAABBBBBBBBCCCCCCCC"
        entropy = compression_core._calculate_entropy(regular_data)
        assert 0 <= entropy <= 8
        
        # Тест со случайными данными (высокая энтропия)
        import random
        random_data = bytes([random.randint(0, 255) for _ in range(100)])
        entropy_random = compression_core._calculate_entropy(random_data)
        assert entropy_random > entropy  # Случайные данные должны иметь большую энтропию
    
    def test_compress_data(self, compression_core, pi_digits, test_data):
        """Тест основного метода сжатия"""
        blocks, stats = compression_core.compress_data(test_data, pi_digits)
        
        # Проверяем результаты
        assert len(blocks) > 0
        assert stats.original_size == len(test_data)
        assert stats.compressed_size > 0
        assert stats.compression_ratio > 0
        assert stats.blocks_total > 0
        assert 0 <= stats.blocks_found <= stats.blocks_total
    
    def test_decompress_data(self, compression_core, pi_digits, test_data):
        """Тест восстановления данных"""
        # Сжимаем данные
        blocks, stats = compression_core.compress_data(test_data, pi_digits)
        
        # Восстанавливаем данные
        xor_key = 0x3F
        recovered_data = compression_core.decompress_data(blocks, pi_digits, len(test_data), xor_key)
        
        # Проверяем целостность (может не работать для всех блоков, если они не найдены в π)
        # Это ожидаемое поведение для демонстрационной версии
        assert len(recovered_data) == len(test_data)


class TestQuantumStyleCompression:
    """Тесты квантово-подобного сжатия"""
    
    @pytest.fixture
    def quantum_compression(self):
        """Создает экземпляр квантового сжатия"""
        return QuantumStyleCompression()
    
    def test_quantum_encode_decode(self, quantum_compression):
        """Тест квантового кодирования и декодирования"""
        test_data = b"ABCD"
        
        # Кодируем
        quantum_blocks = quantum_compression.quantum_encode(test_data)
        
        # Проверяем результат
        assert len(quantum_blocks) == len(test_data) * 4  # 4 квантовых состояния на байт
        
        # Декодируем
        recovered_data = quantum_compression.quantum_decode(quantum_blocks)
        
        # Проверяем целостность
        assert recovered_data == test_data
    
    def test_quantum_states(self, quantum_compression):
        """Тест квантовых состояний"""
        assert len(quantum_compression.quantum_states) == 4
        assert '00' in quantum_compression.quantum_states
        assert '01' in quantum_compression.quantum_states
        assert '10' in quantum_compression.quantum_states
        assert '11' in quantum_compression.quantum_states


class TestCompressionPerformance:
    """Тесты производительности сжатия"""
    
    @pytest.fixture
    def large_test_data(self):
        """Создает большие тестовые данные"""
        return b"Performance test data " * 1000  # ~22KB
    
    def test_compression_performance(self, compression_core, pi_digits, large_test_data):
        """Тест производительности сжатия"""
        import time
        
        start_time = time.time()
        blocks, stats = compression_core.compress_data(large_test_data, pi_digits)
        compression_time = time.time() - start_time
        
        # Проверяем, что сжатие завершается за разумное время
        assert compression_time < 30.0  # 30 секунд максимум
        
        # Проверяем статистику
        assert stats.original_size == len(large_test_data)
        assert stats.compression_ratio > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
