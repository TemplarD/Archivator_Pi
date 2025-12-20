#!/usr/bin/env python3
"""
Основной модуль Pi-Archiver Ultra
Реализует архивацию и разархивацию файлов с использованием числа π
"""

import os
import sys
import time
import argparse
import logging
from pathlib import Path
from typing import List, Optional
import multiprocessing as mp

# Добавляем пути к модулям
sys.path.append(str(Path(__file__).parent.parent))

# Добавляем путь к index_manager (для системной установки)
index_manager_path = Path(__file__).parent.parent / "index_manager"
if index_manager_path.exists():
    sys.path.append(str(index_manager_path))

# Динамический импорт index_manager с обработкой ошибок
try:
    from index_manager.index_manager import IndexManager
except ImportError:
    # Если не найден, пробуем импортировать напрямую
    try:
        # Для системной установки
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "index_manager", 
            Path(__file__).parent.parent / "index_manager" / "index_manager.py"
        )
        index_manager_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(index_manager_module)
        IndexManager = index_manager_module.IndexManager
    except ImportError:
        # Если все еще не найден, создаем заглушку
        print("Warning: index_manager not found, using fallback")
        class IndexManager:
            def __init__(self, *args, **kwargs):
                pass
            def create_index(self, *args, **kwargs):
                return {"files": [], "pi_precision": 0}
            def save_index(self, *args, **kwargs):
                return Path("dummy.idx")

# Остальные импорты с динамической загрузкой
from pi_generator.pi_generator import PiGenerator
from search_engine.pi_search import PiSearchEngine
from compression.compression_core import CompressionCore, CompressionBlock, CompressionStats

# Динамический импорт compression_types с fallback
try:
    from compression.compression_utils import create_file_info_from_compression
    print("Используем compression_utils")
except ImportError:
    # Используем утилиты для работы с существующим CompressionBlock
    try:
        from compression.compression_types import create_file_info_from_compression
        print("Используем compression_types")
    except ImportError:
        # Альтернативный подход с AltCompressionBlock
        try:
            from compression.compression_types_alt import create_alt_file_info_from_compression as create_file_info_from_compression
            print("Используем альтернативные типы сжатия")
        except ImportError:
            # Заглушка если ничего не найдено
            print("Warning: compression_types не найден, используя fallback")
            def create_file_info_from_compression(*args, **kwargs):
                return {"original_size": 0, "compressed_size": 0}

class PiArchiverUltra:
    """Основной класс архиватора Pi-Archiver Ultra"""
    
    def __init__(self, cache_dir: str = "data/pi_storage", 
                 index_dir: str = "data/indexes",
                 pi_precision: int = 1000000):
        self.pi_generator = PiGenerator(cache_dir)
        self.search_engine = PiSearchEngine(self.pi_generator)
        self.compression_core = CompressionCore(self.pi_generator)
        self.index_manager = IndexManager(index_dir)
        self.pi_precision = pi_precision
        
        # Настройка логирования
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Создаем handler для файла с проверкой прав
        try:
            file_handler = logging.FileHandler('/var/log/pi-archiver/archiver.log')
        except PermissionError:
            # Если нет прав, используем домашнюю директорию
            log_file = Path.home() / '.pi-archiver' / 'archiver.log'
            log_file.parent.mkdir(exist_ok=True)
            file_handler = logging.FileHandler(log_file)
        
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        
        # Консольный вывод
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        self.logger.info("Pi-Archiver Ultra инициализирован")
        self.logger.info(f"Точность π: {pi_precision:,} цифр")
        self.logger.info(f"Кэш π: {cache_dir}")
        self.logger.info(f"Индексы: {index_dir}")
        
        print(f"Pi-Archiver Ultra инициализирован")
        print(f"Точность π: {pi_precision:,} цифр")
        print(f"Кэш π: {cache_dir}")
        print(f"Индексы: {index_dir}")
    
    def archive_file(self, input_path: str, output_name: Optional[str] = None,
                    output_dir: Optional[str] = None,
                    use_gpu: bool = False, num_workers: int = None) -> str:
        """
        Архивирует один файл
        
        Args:
            input_path: путь к исходному файлу
            output_name: имя архива (если None, используется имя файла)
            use_gpu: использовать GPU для генерации π
            num_workers: количество рабочих потоков
            
        Returns:
            имя созданного архива
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Файл не найден: {input_path}")
        
        if output_name is None:
            output_name = input_path.stem + ".piarc"
        
        # Обработка директории сохранения
        if output_dir:
            output_path = Path(output_dir) / output_name
            output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            output_path = Path(output_name)
        
        self.logger.info(f"Начало архивации: {input_path}")
        self.logger.info(f"Размер файла: {input_path.stat().st_size:,} байт")
        self.logger.info(f"Директория сохранения: {output_path.parent}")
        
        print(f"Начало архивации: {input_path}")
        print(f"Размер файла: {input_path.stat().st_size:,} байт")
        print(f"📁 Директория сохранения: {output_path.parent}")
        
        start_time = time.time()
        
        # 1. Генерируем π с реальным прогрессом
        self.logger.info("Начало генерации π")
        print("🔄 Генерация цифр π...")
        
        import time as time_module
        progress_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        
        def progress_callback(progress_percent, current_iter, total_iters):
            """Callback для реального прогресса генерации"""
            # Расчет оставшегося времени
            elapsed = time_module.time() - start_time
            if progress_percent > 0:
                estimated_total = elapsed / (progress_percent / 100)
                remaining = estimated_total - elapsed
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                time_str = f" (осталось ~{minutes}:{seconds:02d})"
            else:
                time_str = ""
            
            # Детальная информация о вычислениях
            self.logger.debug(f"Итерация {current_iter}/{total_iters} ({progress_percent:.1f}%)")
            
            print(f"\r{progress_chars[int(progress_percent) % len(progress_chars)]} Генерация π: {progress_percent:.1f}% [{current_iter:,}/{total_iters:,}]{time_str}", end="", flush=True)
        
        start_time = time_module.time()
        self.logger.info(f"Начало генерации {self.pi_precision:,} цифр π (GPU: {use_gpu})")
        
        # Передаем callback для реального прогресса
        pi_digits = self.pi_generator.generate_pi_digits(self.pi_precision, use_gpu, progress_callback)
        
        generation_time = time_module.time() - start_time
        self.logger.info(f"Генерация π завершена, длина: {len(pi_digits):,} цифр, время: {generation_time:.2f} сек")
        print(f"\r✅ Генерация завершена! [{len(pi_digits):,} цифр за {generation_time:.2f} сек] {' ' * 30}")
        # Функция для отображения прогресса сжатия
        def compression_progress_callback(progress, current, total, remaining_time=None):
            bar_length = 50
            filled_length = int(bar_length * progress / 100)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            
            if remaining_time is not None:
                if remaining_time > 3600:
                    time_str = f"{remaining_time/3600:.1f} ч"
                elif remaining_time > 60:
                    time_str = f"{remaining_time/60:.1f} мин"
                else:
                    time_str = f"{remaining_time:.0f} сек"
                print(f"\rСжатие: |{bar}| {progress:.1f}% ({current}/{total} блоков) Осталось: {time_str}", end="")
            else:
                print(f"\rСжатие: |{bar}| {progress:.1f}% ({current}/{total} блоков)", end="")
            
            if progress >= 100:
                print()

        
        # 2. Читаем файл
        with open(input_path, 'rb') as f:
            file_data = f.read()
        
        # 3. Сжимаем данные
        print("Сжатие данных...")
        blocks, stats = self.compression_core.compress_data(file_data, pi_digits, progress_callback=compression_progress_callback)
        
        # Получаем реальный XOR ключ из процесса сжатия
        xor_data, real_xor_key = self.compression_core._xor_decorrelate(file_data, pi_digits)
        print(f"Реальный XOR ключ: 0x{real_xor_key:02X}")
        
        # 4. Создаем информацию о файле
        file_info = create_file_info_from_compression(
            str(input_path), blocks, stats, real_xor_key, self.pi_precision
        )
        
        # 5. Создаем и сохраняем индекс с прогрессом
        print("📦 Создание индекса архива...")
        index = self.index_manager.create_index([file_info], self.pi_precision)
        index_path = self.index_manager.save_index(index, output_path.name)
        
        # 6. Сохраняем сжатые блоки (если нужно)
        self._save_compressed_blocks(blocks, output_path.stem)
        
        total_time = time_module.time() - start_time
        
        # Оценка времени для будущих архивов
        file_size_mb = input_path.stat().st_size / (1024 * 1024)
        time_per_mb = total_time / file_size_mb if file_size_mb > 0 else total_time
        
        print(f"Архивация завершена за {total_time:.2f} сек")
        print(f"Коэффициент сжатия: {stats.compression_ratio:.2f}x")
        print(f"Найдено блоков: {stats.blocks_found}/{stats.blocks_total}")
        print(f"⏱️  Скорость: {file_size_mb/total_time:.2f} MB/сек")
        print(f"✅ Архив сохранен: {index_path}")
        print(f"📁 Путь к архиву: {Path(index_path).absolute()}")
        print(f"📊 Размер архива: {Path(index_path).stat().st_size:,} байт")
        
        # Прогноз для похожих файлов
        if file_size_mb > 0:
            print(f"🔮 Прогноз для {file_size_mb:.1f}MB файла: ~{time_per_mb:.1f} сек")
        
        return output_name
    
    def archive_multiple_files(self, input_paths: List[str], output_name: str,
                              use_gpu: bool = False, num_workers: int = None) -> str:
        """
        Архивирует несколько файлов
        
        Args:
            input_paths: список путей к файлам
            output_name: имя архива
            use_gpu: использовать GPU
            num_workers: количество потоков
            
        Returns:
            имя созданного архива
        """
        print(f"Архивация {len(input_paths)} файлов...")
        
        all_files_info = []
        total_original_size = 0
        total_compressed_size = 0
        
        # Генерируем π один раз для всех файлов
        print("Генерация цифр π...")
        pi_digits = self.pi_generator.generate_pi_digits(self.pi_precision, use_gpu)
        
        for input_path in input_paths:
            print(f"Обработка файла: {input_path}")
            
            # Читаем файл
            with open(input_path, 'rb') as f:
                file_data = f.read()
            
            # Сжимаем
            blocks, stats = self.compression_core.compress_data(file_data, pi_digits, progress_callback=compression_progress_callback)
            
            # Создаем информацию
            xor_key = 0x3F
            file_info = create_file_info_from_compression(
                input_path, blocks, stats, xor_key
            )
            
            all_files_info.append(file_info)
            total_original_size += stats.original_size
            total_compressed_size += stats.compressed_size
        
        # Создаем общий индекс
        index = self.index_manager.create_index(all_files_info, self.pi_precision)
        index_path = self.index_manager.save_index(index, output_name)
        
        print(f"Архивация {len(input_paths)} файлов завершена")
        print(f"Общий коэффициент сжатия: {total_original_size / total_compressed_size:.2f}x")
        
        return output_name
    
    def extract_file(self, archive_name: str, output_dir: str = ".") -> List[str]:
        """
        Разархивирует архив
        
        Args:
            archive_name: имя архива
            output_dir: директория для извлечения
            
        Returns:
            список извлеченных файлов
        """
        print(f"Извлечение архива: {archive_name}...")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            index = self.index_manager.load_index_by_archive_name(archive_name)
        except Exception as e:
            print(f"Ошибка загрузки индекса: {e}")
            return []

        print("Генерация цифр π...")
        pi_digits = self.pi_generator.generate_pi_digits(
            index.get("pi_precision", self.pi_precision)
        )
        
        extracted_files = []
        
        for file_info in index.get("files", []):
            filename = file_info.get("filename")
            original_size = file_info.get("original_size")
            blocks = file_info.get("blocks", [])
            xor_key = file_info.get("xor_key", 0x3F)  # Используем ключ по умолчанию, если не сохранен
            
            if not filename or original_size is None:
                continue
            
            file_path = output_path / Path(filename).name
            print(f"Извлечение: {file_path}")
            
            try:
                # Загружаем сохраненные блоки данных
                saved_blocks = self._load_compressed_blocks(archive_name, filename)
                
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
                
                decompressed_data = self.compression_core.decompress_data(
                    compression_blocks, pi_digits, original_size, xor_key
                )
                
                with open(file_path, "wb") as f:
                    f.write(decompressed_data)
                
                extracted_files.append(str(file_path))
                print(f"Успешно извлечен: {file_path}")
                
            except Exception as e:
                print(f"Ошибка извлечения {filename}: {e}")
                continue
        
        print(f"Извлечение завершено. Файлов: {len(extracted_files)}")
        return extracted_files
    
    def _save_compressed_blocks(self, blocks: List, archive_name: str):
        """Сохраняет сжатые блоки в отдельный файл"""
        blocks_file = Path(self.index_manager.index_dir) / f"{archive_name}.blocks"
        
        with open(blocks_file, 'wb') as f:
            for block in blocks:
                # Сохраняем метаданные блока
                f.write(struct.pack('I', block.block_id))
                f.write(struct.pack('I', len(block.original_data)))
                f.write(struct.pack('Q', block.start_pos or 0))
                f.write(struct.pack('Q', block.end_pos or 0))
                f.write(block.data_hash.encode()[:8].ljust(8, b'\0'))
                
                # Если блок не найден в π, сохраняем данные
                if not block.found_positions():
                    f.write(block.original_data)
    
    def _load_compressed_blocks(self, archive_name: str, file_name: str) -> dict:
        """Загружает сжатые блоки из файла"""
        blocks_file = Path(self.index_manager.index_dir) / f"{archive_name}.blocks"
        
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
                        print(f"Загружен блок {block_id}: {len(original_data)} байт, хеш: {data_hash}")
                    
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
    
    def get_archive_info(self, archive_name: str) -> dict:
        """Возвращает информацию об архиве"""
        return self.index_manager.get_index_statistics(archive_name)
    
    def list_archives(self) -> List[dict]:
        """Возвращает список всех архивов"""
        return self.index_manager.list_indexes()


def main():
    """Точка входа для командной строки"""
    parser = argparse.ArgumentParser(description='Pi-Archiver Ultra - Архиватор на основе числа π')
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда архивации
    archive_parser = subparsers.add_parser('archive', help='Архивировать файлы')
    archive_parser.add_argument('files', nargs='+', help='Файлы для архивации')
    archive_parser.add_argument('-o', '--output', help='Имя архива')
    archive_parser.add_argument('-d', '--directory', help='Директория для сохранения архива')
    archive_parser.add_argument('--gpu', action='store_true', help='Использовать GPU')
    archive_parser.add_argument('--workers', type=int, help='Количество потоков')
    archive_parser.add_argument('--precision', type=int, default=1000000, 
                              help='Количество цифр π (по умолчанию: 1000000)')
    
    # Команда извлечения
    extract_parser = subparsers.add_parser('extract', help='Извлечь архив')
    extract_parser.add_argument('archive', help='Имя архива')
    extract_parser.add_argument('-o', '--output', default='.', help='Директория для извлечения')
    
    # Команда информации
    info_parser = subparsers.add_parser('info', help='Информация об архиве')
    info_parser.add_argument('archive', help='Имя архива')
    
    # Команда списка
    list_parser = subparsers.add_parser('list', help='Список архивов')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Создаем архиватор
    archiver = PiArchiverUltra(pi_precision=getattr(args, 'precision', 1000000))
    
    try:
        if args.command == 'archive':
            if len(args.files) == 1:
                archiver.archive_file(args.files[0], args.output, args.directory,
                                       args.gpu, args.workers)
            else:
                output_name = args.output or f"archive_{int(time.time())}.piarc"
                archiver.archive_multiple_files(args.files, output_name, args.gpu, args.workers)
        
        elif args.command == 'extract':
            archiver.extract_file(args.archive, args.output)
        
        elif args.command == 'info':
            info = archiver.get_archive_info(args.archive)
            print(f"Информация об архиве: {args.archive}")
            print(f"Версия: {info['basic_info']['version']}")
            print(f"Файлов: {info['basic_info']['total_files']}")
            print(f"Исходный размер: {info['size_info']['original_size']:,} байт")
            print(f"Сжатый размер: {info['size_info']['compressed_size']:,} байт")
            print(f"Коэффициент сжатия: {info['size_info']['compression_ratio']:.2f}x")
            print(f"Экономия места: {info['size_info']['space_saved']:,} байт")
        
        elif args.command == 'list':
            archives = archiver.list_archives()
            if archives:
                print("Доступные архивы:")
                for archive in archives:
                    if 'error' in archive:
                        print(f"- {archive['filename']}: ОШИБКА - {archive['error']}")
                    else:
                        print(f"- {archive['filename']}: {archive['files_count']} файлов, "
                              f"{archive['compression_ratio']:.2f}x сжатие")
            else:
                print("Архивы не найдены")
    
    except Exception as e:
        print(f"Ошибка: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import struct
    sys.exit(main())
