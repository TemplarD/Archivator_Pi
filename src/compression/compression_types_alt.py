"""
Альтернативные типы данных для модуля сжатия Pi-Archiver Ultra
Независимая реализация CompressionBlock с атрибутом position
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from pathlib import Path

@dataclass
class AltCompressionBlock:
    """Альтернативный блок сжатых данных с атрибутом position"""
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
class AltCompressionStats:
    """Альтернативная статистика сжатия"""
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

def create_alt_file_info_from_compression(
    file_path: str, 
    blocks: List[AltCompressionBlock], 
    stats: AltCompressionStats,
    pi_precision: int
) -> Dict[str, Any]:
    """Создает информацию о файле для индекса с использованием AltCompressionBlock"""
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

def convert_to_alt_block(core_block) -> AltCompressionBlock:
    """Конвертирует CompressionBlock из compression_core.py в AltCompressionBlock"""
    return AltCompressionBlock(
        position=core_block.start_pos or 0,
        length=(core_block.end_pos - core_block.start_pos) if core_block.start_pos and core_block.end_pos else 0,
        data=core_block.original_data,  # Временно используем оригинальные данные
        original_data=core_block.original_data
    )

def convert_to_alt_stats(core_stats) -> AltCompressionStats:
    """Конвертирует CompressionStats из compression_core.py в AltCompressionStats"""
    return AltCompressionStats(
        original_size=core_stats.original_size,
        compressed_size=core_stats.compressed_size,
        blocks_found=getattr(core_stats, 'blocks_found', 0),
        blocks_total=getattr(core_stats, 'blocks_total', 0),
        compression_ratio=core_stats.compression_ratio
    )
