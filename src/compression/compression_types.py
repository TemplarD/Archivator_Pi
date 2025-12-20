"""
Типы данных для модуля сжатия Pi-Archiver Ultra
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from pathlib import Path

@dataclass
class CompressionBlock:
    """Блок сжатых данных"""
    position: int
    length: int
    data: bytes
    original_data: bytes
    
    def __post_init__(self):
        """Валидация после инициализации"""
        if self.position < 0:
            raise ValueError("Position must be non-negative")
        if self.length <= 0:
            raise ValueError("Length must be positive")
        if not isinstance(self.data, bytes):
            raise TypeError("Data must be bytes")
        if not isinstance(self.original_data, bytes):
            raise TypeError("Original data must be bytes")

@dataclass
class CompressionStats:
    """Статистика сжатия"""
    original_size: int
    compressed_size: int
    blocks_found: int
    blocks_total: int
    compression_ratio: float
    
    def __post_init__(self):
        """Валидация после инициализации"""
        if self.original_size < 0:
            raise ValueError("Original size must be non-negative")
        if self.compressed_size < 0:
            raise ValueError("Compressed size must be non-negative")
        if self.blocks_found < 0:
            raise ValueError("Blocks found must be non-negative")
        if self.blocks_total < 0:
            raise ValueError("Blocks total must be non-negative")
        if self.compression_ratio < 0:
            raise ValueError("Compression ratio must be non-negative")
    
    @property
    def compression_percentage(self) -> float:
        """Процент сжатия"""
        if self.original_size == 0:
            return 0.0
        return (1 - self.compressed_size / self.original_size) * 100

def create_file_info_from_compression(
    file_path: str, 
    blocks: List[CompressionBlock], 
    stats: CompressionStats,
    pi_precision: int
) -> Dict[str, Any]:
    """Создает информацию о файле для индекса"""
    return {
        "filename": Path(file_path).name,
        "original_size": stats.original_size,
        "compressed_size": stats.compressed_size,
        "blocks_count": len(blocks),
        "compression_ratio": stats.compression_ratio,
        "pi_precision": pi_precision,
        "blocks": [
            {
                "position": block.position,
                "length": block.length,
                "data_size": len(block.data),
                "original_size": len(block.original_data)
            }
            for block in blocks
        ]
    }
