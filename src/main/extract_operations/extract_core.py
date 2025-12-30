#!/usr/bin/env python3
"""
Основные операции извлечения Pi-Archiver Ultra
Реализует восстановление файлов с использованием многопоточности
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

# Абсолютные импорты для избежания проблем с относительными импортами
sys.path.append(str(Path(__file__).parent.parent.parent))

from progress_indicators.extraction_progress.extraction_callback import ExtractionProgressCallback
from compression.compression_core import CompressionCore, CompressionBlock
from pi_generator.pi_generator import PiGenerator


class ExtractOperations:
    """Класс для операций извлечения"""
    
    def __init__(self, pi_generator: PiGenerator, compression_core: CompressionCore):
        self.pi_generator = pi_generator
        self.compression_core = compression_core
    
    def extract_files_from_index(self, index: Dict[str, Any], output_dir: str, 
                               archive_name: str) -> List[str]:
        """
        Извлекает файлы из индекса
        
        Args:
            index: индексный словарь
            output_dir: директория для извлечения
            archive_name: имя архива
            
        Returns:
            список извлеченных файлов
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Генерируем π для извлечения
        pi_precision = index.get("pi_precision", 1000000)
        print("Генерация цифр π...")
        pi_digits = self.pi_generator.generate_pi_digits(pi_precision)
        
        # Подсчитываем общее количество блоков для прогресс-бара
        total_blocks = sum(len(file_info.get("blocks", [])) for file_info in index.get("files", []))
        total_files = len(index.get("files", []))
        
        print(f"Восстановление данных ({total_files} файлов, {total_blocks} блоков)...")
        
        # Создаем callback для прогресса извлечения
        progress_callback = ExtractionProgressCallback(total_files, total_blocks)
        
        extracted_files = []
        
        for file_info in index.get("files", []):
            filename = file_info.get("filename")
            original_size = file_info.get("original_size")
            blocks = file_info.get("blocks", [])
            xor_key = file_info.get("xor_key", 0x3F)
            
            if not filename or original_size is None:
                continue
            
            file_path = output_path / Path(filename).name
            print(f"\nИзвлечение: {file_path}")
            
            try:
                # Извлекаем один файл
                success = self._extract_single_file(
                    file_info, file_path, pi_digits, xor_key, 
                    archive_name, progress_callback
                )
                
                if success:
                    extracted_files.append(str(file_path))
                    progress_callback.increment_file()
                    print()  # Перенос строки после завершения файла
                    print()  # Дополнительный перенос строки
                
            except Exception as e:
                print(f"\nОшибка извлечения {filename}: {e}")
                continue
        
        print(f"Извлечение завершено. Файлов: {len(extracted_files)}")
        print()  # Новая строка после прогресс-бара
        
        return extracted_files
    
    def _extract_single_file(self, file_info: Dict[str, Any], file_path: Path,
                           pi_digits: str, xor_key: int, archive_name: str,
                           progress_callback: ExtractionProgressCallback) -> bool:
        """
        Извлекает один файл
        
        Args:
            file_info: информация о файле из индекса
            file_path: путь для сохранения файла
            pi_digits: строка с цифрами π
            xor_key: XOR ключ
            archive_name: имя архива
            progress_callback: callback для прогресса
            
        Returns:
            True если успешно
        """
        blocks = file_info.get("blocks", [])
        original_size = file_info.get("original_size")
        
        # Счетчик блоков для текущего файла
        file_blocks_processed = 0
        file_blocks_total = len(blocks)
        
        # Загружаем сохраненные блоки данных
        saved_blocks = self._load_compressed_blocks(archive_name, file_path.name)
        
        compression_blocks = []
        for block_data in blocks:
            block_id = block_data.get("block_id", 0)
            
            # Получаем сохраненные данные для этого блока
            saved_block = saved_blocks.get(block_id, {})
            
            # Проверяем, есть ли сохраненные данные в файле .blocks
            if block_data.get("start_pos") is None:
                # Блок не найден в π, используем сохраненные данные
                compression_blocks.append(CompressionBlock(
                    block_id=block_id,
                    original_data=saved_block.get('original_data', b''),
                    xor_key=xor_key,
                    start_pos=None,
                    end_pos=None,
                    compressed_size=block_data.get("compressed_size", 0),
                    data_hash=block_data.get("data_hash", "")
                ))
            else:
                # Блок найден в π
                compression_blocks.append(CompressionBlock(
                    block_id=block_id,
                    original_data=b'',
                    xor_key=xor_key,
                    start_pos=block_data.get("start_pos"),
                    end_pos=block_data.get("end_pos"),
                    compressed_size=block_data.get("compressed_size", 0),
                    data_hash=block_data.get("data_hash", "")
                ))
            
            # Обновляем прогресс-бар
            file_blocks_processed += 1
            progress_callback.update_file_progress(file_blocks_processed, file_blocks_total)
        
        # Счетчики для статистики восстановления
        pi_blocks = 0
        backup_blocks = 0
        for block in compression_blocks:
            if block.found_positions():
                pi_blocks += 1
            else:
                backup_blocks += 1
        
        # Восстанавливаем данные
        decompressed_data = self.compression_core.decompress_data(
            compression_blocks, pi_digits, original_size, xor_key
        )
        
        # Сохраняем файл с прогресс-баром
        self._save_file_with_progress(decompressed_data, file_path, progress_callback)
        
        # Вывод статистики восстановления
        print(f"  Восстановлено: {pi_blocks} блоков из π, {backup_blocks} блоков из бэкапа")
        
        return True
    
    def _save_file_with_progress(self, decompressed_data: bytes, file_path: Path,
                               progress_callback: ExtractionProgressCallback):
        """
        Сохраняет файл с прогресс-баром
        
        Args:
            decompressed_data: восстановленные данные
            file_path: путь для сохранения
            progress_callback: callback для прогресса
        """
        file_size = len(decompressed_data)
        chunk_size = 1024  # 1KB chunks
        written = 0
        
        with open(file_path, "wb") as f:
            for i in range(0, file_size, chunk_size):
                chunk = decompressed_data[i:i+chunk_size]
                f.write(chunk)
                written += len(chunk)
                
                # Обновляем прогресс бар
                progress_callback.file_restore_progress(written, file_size)
        
        print()  # Новая строка после завершения прогресс бара
    
    def _load_compressed_blocks(self, archive_name: str, file_name: str) -> dict:
        """
        Загружает сжатые блоки из файла
        
        Args:
            archive_name: имя архива
            file_name: имя файла
            
        Returns:
            словарь с блоками
        """
        import struct
        
        # Определяем путь к файлу блоков
        blocks_file = Path.cwd() / f"{archive_name}.blocks"
        
        if not blocks_file.exists():
            print(f"Файл блоков не найден: {blocks_file}")
            return {}
        
        blocks = {}
        
        with open(blocks_file, 'rb') as f:
            while True:
                try:
                    # Читаем метаданные
                    block_id_data = f.read(4)
                    if not block_id_data:
                        break
                    
                    block_id = struct.unpack('I', block_id_data)[0]
                    data_size = struct.unpack('I', f.read(4))[0]
                    start_pos = struct.unpack('Q', f.read(8))[0]
                    end_pos = struct.unpack('Q', f.read(8))[0]
                    data_hash = f.read(8).decode().rstrip('\0')
                    
                    # Читаем данные если нужно
                    original_data = b''
                    if start_pos == 0 and end_pos == 0 and data_size > 0:
                        original_data = f.read(data_size)
                    
                    blocks[block_id] = {
                        'original_data': original_data,
                        'start_pos': start_pos if start_pos != 0 else None,
                        'end_pos': end_pos if end_pos != 0 else None,
                        'compressed_size': data_size,
                        'data_hash': data_hash
                    }
                    
                except struct.error as e:
                    print(f"Ошибка чтения структуры: {e}")
                    break
                except Exception as e:
                    print(f"Ошибка загрузки блока: {e}")
                    break
        
        print(f"Загружено {len(blocks)} блоков из файла")
        return blocks
