"""
Index Manager для Pi-Archiver Ultra
Управление созданием и сохранением индексных файлов
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class ArchiveIndex:
    """Индекс архива с метаданными"""
    files: List[Dict[str, Any]]
    pi_precision: int
    created_at: float
    total_blocks: int
    compression_ratio: float

class IndexManager:
    """Менеджер индексных файлов архива"""
    
    def __init__(self, index_dir: str = "data/indexes"):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
    
    def create_index(self, file_infos: List[Dict[str, Any]], pi_precision: int) -> ArchiveIndex:
        """Создает индекс архива"""
        total_blocks = sum(len(info.get('blocks', [])) for info in file_infos)
        
        # Рассчитываем общую степень сжатия
        original_size = sum(info.get('original_size', 0) for info in file_infos)
        compressed_size = sum(info.get('compressed_size', 0) for info in file_infos)
        compression_ratio = compressed_size / original_size if original_size > 0 else 0
        
        return ArchiveIndex(
            files=file_infos,
            pi_precision=pi_precision,
            created_at=time.time(),
            total_blocks=total_blocks,
            compression_ratio=compression_ratio
        )
    
    def save_index(self, index: ArchiveIndex, filename: str) -> Path:
        """Сохраняет индекс в файл"""
        index_path = self.index_dir / f"{filename}.idx"
        
        # Конвертируем dataclass в dict для JSON сериализации
        index_dict = asdict(index)
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_dict, f, indent=2, ensure_ascii=False)
        
        return index_path
    
    def load_index(self, filename: str) -> Optional[ArchiveIndex]:
        """Загружает индекс из файла"""
        index_path = self.index_dir / f"{filename}.idx"
        
        if not index_path.exists():
            return None
        
        with open(index_path, 'r', encoding='utf-8') as f:
            index_dict = json.load(f)
        
        # Восстанавливаем dataclass из dict
        return ArchiveIndex(**index_dict)
    
    def load_index_by_archive_name(self, archive_name: str) -> dict:
        """
        Загружает индекс архива
        
        Args:
            archive_name: имя архива (без расширения)
            
        Returns:
            словарь с данными индекса
        """
        if not archive_name.endswith('.piarc.idx'):
            archive_name = f"{archive_name}.piarc.idx"
        
        index_path = Path(self.index_dir) / archive_name
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл индекса не найден: {index_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Ошибка в формате JSON: {index_path}")
        except Exception as e:
            raise Exception(f"Ошибка загрузки индекса: {e}")
    
    def list_indexes(self) -> List[str]:
        """Возвращает список доступных индексов"""
        return [f.stem for f in self.index_dir.glob("*.idx")]
    
    def delete_index(self, filename: str) -> bool:
        """Удаляет индексный файл"""
        index_path = self.index_dir / f"{filename}.idx"
        
        if index_path.exists():
            index_path.unlink()
            return True
        return False
    
    def get_index_statistics(self, archive_name: str) -> dict:
        """
        Возвращает подробную статистику об архиве
        
        Args:
            archive_name: имя архива
            
        Returns:
            словарь со статистикой
        """
        try:
            index_data = self.load_index_by_archive_name(archive_name)
            
            # Базовая информация
            basic_info = {
                "version": "1.0",
                "total_files": len(index_data.get("files", [])),
                "pi_precision": index_data.get("pi_precision", 0),
                "created_at": index_data.get("created_at", 0),
                "total_blocks": index_data.get("total_blocks", 0)
            }
            
            # Информация о размерах
            original_size = sum(f.get("original_size", 0) for f in index_data.get("files", []))
            compressed_size = sum(f.get("compressed_size", 0) for f in index_data.get("files", []))
            compression_ratio = compressed_size / original_size if original_size > 0 else 0
            
            size_info = {
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio,
                "space_saved": max(0, original_size - compressed_size)
            }
            
            # Информация о файлах
            files_info = []
            for file_data in index_data.get("files", []):
                files_info.append({
                    "filename": file_data.get("filename", "unknown"),
                    "original_size": file_data.get("original_size", 0),
                    "compressed_size": file_data.get("compressed_size", 0),
                    "blocks_count": file_data.get("blocks_count", 0),
                    "compression_ratio": file_data.get("compression_ratio", 0)
                })
            
            return {
                "basic_info": basic_info,
                "size_info": size_info,
                "files_info": files_info,
                "archive_file": f"{archive_name}.piarc.idx"
            }
            
        except Exception as e:
            return {
                "error": f"Ошибка при получении статистики: {str(e)}",
                "basic_info": {"version": "1.0", "total_files": 0},
                "size_info": {"original_size": 0, "compressed_size": 0, "compression_ratio": 0}
            }
    
    def list_indexes(self) -> List[dict]:
        """
        Возвращает список всех архивов с подробной информацией
        
        Returns:
            список словарей с информацией об архивах
        """
        archives = []
        
        for index_file in self.index_dir.glob("*.idx"):
            try:
                archive_name = index_file.stem
                index_data = self.load_index_by_archive_name(archive_name)
                
                # Вычисляем общую статистику
                total_files = len(index_data.get("files", []))
                original_size = sum(f.get("original_size", 0) for f in index_data.get("files", []))
                compressed_size = sum(f.get("compressed_size", 0) for f in index_data.get("files", []))
                compression_ratio = compressed_size / original_size if original_size > 0 else 0
                
                archives.append({
                    "filename": archive_name,
                    "files_count": total_files,
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "compression_ratio": compression_ratio,
                    "created_at": index_data.get("created_at", 0),
                    "pi_precision": index_data.get("pi_precision", 0)
                })
                
            except Exception as e:
                archives.append({
                    "filename": index_file.stem,
                    "error": str(e)
                })
        
        return archives
