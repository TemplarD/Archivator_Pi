#!/usr/bin/env python3
"""
Менеджер индексных файлов Pi-Archiver Ultra
Управляет созданием, чтением и записью индексных файлов в JSON формате
"""

import json
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class FileInfo:
    """Информация о файле в индексе"""
    original_name: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    file_hash: str
    creation_time: str
    blocks: List[Dict[str, Any]]
    xor_key: str
    encoding_type: str

@dataclass
class ArchiveIndex:
    """Структура индексного файла архива"""
    version: str
    pi_precision: int
    creation_time: str
    total_files: int
    total_original_size: int
    total_compressed_size: int
    overall_compression_ratio: float
    files: List[FileInfo]
    metadata: Dict[str, Any]

class IndexManager:
    def __init__(self, index_dir: str = "data/indexes"):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.current_version = "1.0"
        
    def create_index(self, files_info: List[Dict], pi_precision: int = 100000000,
                    metadata: Optional[Dict] = None) -> ArchiveIndex:
        """
        Создает новый индексный файл
        
        Args:
            files_info: информация о сжатых файлах
            pi_precision: количество использованных цифр π
            metadata: дополнительные метаданные
            
        Returns:
            объект ArchiveIndex
        """
        creation_time = datetime.now().isoformat()
        
        # Собираем информацию о файлах
        files = []
        total_original = 0
        total_compressed = 0
        
        for file_info in files_info:
            file_obj = FileInfo(
                original_name=file_info['original_name'],
                original_size=file_info['original_size'],
                compressed_size=file_info['compressed_size'],
                compression_ratio=file_info['compression_ratio'],
                file_hash=file_info['file_hash'],
                creation_time=creation_time,
                blocks=file_info['blocks'],
                xor_key=file_info['xor_key'],
                encoding_type=file_info.get('encoding_type', 'arithmetic')
            )
            files.append(file_obj)
            total_original += file_info['original_size']
            total_compressed += file_info['compressed_size']
        
        # Вычисляем общую статистику
        overall_ratio = total_original / total_compressed if total_compressed > 0 else 0
        
        # Создаем индекс
        index = ArchiveIndex(
            version=self.current_version,
            pi_precision=pi_precision,
            creation_time=creation_time,
            total_files=len(files),
            total_original_size=total_original,
            total_compressed_size=total_compressed,
            overall_compression_ratio=overall_ratio,
            files=files,
            metadata=metadata or {}
        )
        
        return index
    
    def save_index(self, index: ArchiveIndex, filename: str) -> str:
        """
        Сохраняет индекс в файл
        
        Args:
            index: объект индекса
            filename: имя файла индекса
            
        Returns:
            путь к сохраненному файлу
        """
        index_path = self.index_dir / filename
        
        # Конвертируем в словарь
        index_dict = asdict(index)
        
        # Добавляем контрольную сумму
        index_json = json.dumps(index_dict, indent=2, ensure_ascii=False)
        checksum = hashlib.sha256(index_json.encode()).hexdigest()
        index_dict['checksum'] = checksum
        
        # Сохраняем
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_dict, f, indent=2, ensure_ascii=False)
        
        print(f"Индекс сохранен: {index_path}")
        print(f"Файлов в архиве: {index.total_files}")
        print(f"Общий коэффициент сжатия: {index.overall_compression_ratio:.2f}x")
        
        return str(index_path)
    
    def load_index(self, filename: str) -> ArchiveIndex:
        """
        Загружает индекс из файла
        
        Args:
            filename: имя файла индекса
            
        Returns:
            объект ArchiveIndex
        """
        index_path = self.index_dir / filename
        
        if not index_path.exists():
            raise FileNotFoundError(f"Индексный файл не найден: {index_path}")
        
        with open(index_path, 'r', encoding='utf-8') as f:
            index_dict = json.load(f)
        
        # Проверяем контрольную сумму
        if 'checksum' in index_dict:
            checksum = index_dict.pop('checksum')
            index_json = json.dumps(index_dict, indent=2, ensure_ascii=False)
            calculated_checksum = hashlib.sha256(index_json.encode()).hexdigest()
            
            if checksum != calculated_checksum:
                raise ValueError("Контрольная сумма индекса не совпадает!")
        
        # Восстанавливаем объект
        files = []
        for file_dict in index_dict['files']:
            file_info = FileInfo(**file_dict)
            files.append(file_info)
        
        index_dict['files'] = files
        
        return ArchiveIndex(**index_dict)
    
    def verify_index(self, filename: str) -> Dict[str, Any]:
        """
        Проверяет целостность индексного файла
        
        Args:
            filename: имя файла индекса
            
        Returns:
            результат проверки
        """
        try:
            index = self.load_index(filename)
            
            verification = {
                'valid': True,
                'version': index.version,
                'files_count': index.total_files,
                'creation_time': index.creation_time,
                'pi_precision': index.pi_precision,
                'errors': []
            }
            
            # Проверяем структуру файлов
            for file_info in index.files:
                if not file_info.original_name:
                    verification['errors'].append("Пустое имя файла")
                
                if file_info.original_size <= 0:
                    verification['errors'].append(f"Некорректный размер файла: {file_info.original_name}")
                
                if file_info.compression_ratio <= 0:
                    verification['errors'].append(f"Некорректный коэффициент сжатия: {file_info.original_name}")
            
            if verification['errors']:
                verification['valid'] = False
            
            return verification
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'errors': [str(e)]
            }
    
    def list_indexes(self) -> List[Dict[str, Any]]:
        """
        Возвращает список всех индексных файлов
        
        Returns:
            список информации об индексах
        """
        indexes = []
        
        for index_file in self.index_dir.glob("*.json"):
            try:
                verification = self.verify_index(index_file.name)
                
                if verification['valid']:
                    index = self.load_index(index_file.name)
                    info = {
                        'filename': index_file.name,
                        'creation_time': index.creation_time,
                        'files_count': index.total_files,
                        'total_size': index.total_original_size,
                        'compressed_size': index.total_compressed_size,
                        'compression_ratio': index.overall_compression_ratio,
                        'version': index.version
                    }
                    indexes.append(info)
                else:
                    info = {
                        'filename': index_file.name,
                        'error': 'Invalid index',
                        'errors': verification['errors']
                    }
                    indexes.append(info)
                    
            except Exception as e:
                info = {
                    'filename': index_file.name,
                    'error': str(e)
                }
                indexes.append(info)
        
        return sorted(indexes, key=lambda x: x.get('creation_time', ''), reverse=True)
    
    def delete_index(self, filename: str) -> bool:
        """
        Удаляет индексный файл
        
        Args:
            filename: имя файла индекса
            
        Returns:
            True если удален успешно
        """
        index_path = self.index_dir / filename
        
        if index_path.exists():
            index_path.unlink()
            print(f"Индексный файл удален: {filename}")
            return True
        else:
            print(f"Индексный файл не найден: {filename}")
            return False
    
    def get_index_statistics(self, filename: str) -> Dict[str, Any]:
        """
        Возвращает подробную статистику об индексе
        
        Args:
            filename: имя файла индекса
            
        Returns:
            статистика индекса
        """
        index = self.load_index(filename)
        
        stats = {
            'basic_info': {
                'version': index.version,
                'creation_time': index.creation_time,
                'pi_precision': index.pi_precision,
                'total_files': index.total_files
            },
            'size_info': {
                'original_size': index.total_original_size,
                'compressed_size': index.total_compressed_size,
                'compression_ratio': index.overall_compression_ratio,
                'space_saved': index.total_original_size - index.total_compressed_size
            },
            'file_details': []
        }
        
        for file_info in index.files:
            file_detail = {
                'name': file_info.original_name,
                'original_size': file_info.original_size,
                'compressed_size': file_info.compressed_size,
                'compression_ratio': file_info.compression_ratio,
                'blocks_count': len(file_info.blocks),
                'encoding_type': file_info.encoding_type,
                'xor_key': file_info.xor_key
            }
            stats['file_details'].append(file_detail)
        
        return stats


def create_file_info_from_compression(original_path: str, blocks: List, 
                                    stats, xor_key: int) -> Dict[str, Any]:
    """
    Создает информацию о файле из результатов сжатия
    
    Args:
        original_path: путь к оригинальному файлу
        blocks: сжатые блоки
        stats: статистика сжатия
        xor_key: XOR ключ
        
    Returns:
        словарь с информацией о файле
    """
    from pathlib import Path
    
    original_name = Path(original_path).name
    
    # Конвертируем блоки в словари
    blocks_dict = []
    for block in blocks:
        block_info = {
            'block_id': block.block_id,
            'start_pos': block.start_pos,
            'end_pos': block.end_pos,
            'data_hash': block.data_hash,
            'compressed_size': block.compressed_size
        }
        blocks_dict.append(block_info)
    
    # Вычисляем хеш файла
    file_hash = hashlib.sha256(original_name.encode()).hexdigest()[:16]
    
    return {
        'original_name': original_name,
        'original_size': stats.original_size,
        'compressed_size': stats.compressed_size,
        'compression_ratio': stats.compression_ratio,
        'file_hash': file_hash,
        'blocks': blocks_dict,
        'xor_key': hex(xor_key),
        'encoding_type': 'arithmetic'
    }


if __name__ == "__main__":
    # Тестирование менеджера индексов
    manager = IndexManager()
    
    # Создаем тестовый индекс
    test_files = [
        {
            'original_name': 'test1.txt',
            'original_size': 1024,
            'compressed_size': 256,
            'compression_ratio': 4.0,
            'file_hash': 'abc123',
            'blocks': [
                {
                    'block_id': 0,
                    'start_pos': 12345,
                    'end_pos': 12350,
                    'data_hash': 'def456',
                    'compressed_size': 8
                }
            ],
            'xor_key': '0x3F',
            'encoding_type': 'arithmetic'
        }
    ]
    
    # Создаем и сохраняем индекс
    index = manager.create_index(test_files, pi_precision=1000000)
    index_path = manager.save_index(index, 'test_archive.json')
    
    # Загружаем и проверяем
    loaded_index = manager.load_index('test_archive.json')
    print(f"Загружен индекс с {loaded_index.total_files} файлами")
    
    # Выводим список всех индексов
    indexes = manager.list_indexes()
    print(f"Всего индексов: {len(indexes)}")
    for idx in indexes:
        print(f"- {idx['filename']}: {idx.get('files_count', 0)} файлов")
