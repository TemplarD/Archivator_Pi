"""
Утилиты для работы с сжатием Pi-Archiver Ultra
Работает с существующим CompressionBlock из compression_core.py
"""

from typing import List, Dict, Any
from pathlib import Path
from .compression_core import CompressionBlock, CompressionStats

def create_file_info_from_compression(
    file_path: str, 
    blocks: List[CompressionBlock], 
    stats: CompressionStats,
    xor_key: int,
    pi_precision: int
) -> Dict[str, Any]:
    """Создает информацию о файле для индекса с использованием существующего CompressionBlock"""
    return {
        "filename": Path(file_path).name,
        "original_size": stats.original_size,
        "compressed_size": stats.compressed_size,
        "blocks_count": len(blocks),
        "compression_ratio": stats.compression_ratio,
        "xor_key": xor_key,
        "pi_precision": pi_precision,
        "blocks_found": stats.blocks_found,
        "blocks_total": stats.blocks_total,
        "blocks": [
            {
                "block_id": block.block_id,
                "start_pos": block.start_pos,
                "end_pos": block.end_pos,
                "compressed_size": block.compressed_size,
                "data_hash": block.data_hash,
                "original_size": len(block.original_data)
            }
            for block in blocks
        ]
    }

def create_compatible_block_info(block: CompressionBlock) -> Dict[str, Any]:
    """Создает совместимую информацию о блоке для индекса"""
    return {
        "position": block.start_pos or 0,
        "length": block.end_pos - block.start_pos if block.start_pos and block.end_pos else 0,
        "block_id": block.block_id,
        "compressed_size": block.compressed_size,
        "data_hash": block.data_hash,
        "original_size": len(block.original_data)
    }

def calculate_compression_ratio(original: int, compressed: int) -> float:
    """Рассчитывает коэффициент сжатия"""
    if original == 0:
        return 0.0
    return compressed / original

def format_compression_stats(stats: CompressionStats) -> str:
    """Форматирует статистику сжатия для вывода"""
    ratio = calculate_compression_ratio(stats.original_size, stats.compressed_size)
    percentage = (1 - ratio) * 100 if stats.original_size > 0 else 0
    
    return f"Коэффициент сжатия: {ratio:.2f}x ({percentage:.1f}%)"
