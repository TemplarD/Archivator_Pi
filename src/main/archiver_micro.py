#!/usr/bin/env python3
"""
Pi-Archiver Ultra - Микро-модульная версия
Основной модуль с максимальным разделением функционала
"""

import os
import sys
import time
import struct
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

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
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "index_manager", 
            Path(__file__).parent.parent / "index_manager" / "index_manager.py"
        )
        index_manager_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(index_manager_module)
        IndexManager = index_manager_module.IndexManager
    except ImportError:
        print("Warning: index_manager not found, using fallback")
        class IndexManager:
            def __init__(self, *args, **kwargs):
                pass
            def create_index(self, *args, **kwargs):
                return {"files": [], "pi_precision": 0}
            def save_index(self, *args, **kwargs):
                return Path("dummy.idx")

# Импорты основных модулей
from pi_generator.pi_generator import PiGenerator
from search_engine.pi_search import PiSearchEngine
from compression.compression_core import CompressionCore

# Импорты микро-модульных компонентов
from progress_indicators import PiProgressCallback, CompressionProgressCallback, ExtractionProgressCallback
from archive_operations import PiGeneratorOperations, DataCompressionOperations, SystemInfoOperations
from extract_operations import ExtractOperations

# Динамический импорт compression_types с fallback
try:
    from compression.compression_utils import create_file_info_from_compression
    print("Используем compression_utils")
except ImportError:
    try:
        from compression.compression_types import create_file_info_from_compression
        print("Используем compression_types")
    except ImportError:
        try:
            from compression.compression_types_alt import create_alt_file_info_from_compression as create_file_info_from_compression
            print("Используем альтернативные типы сжатия")
        except ImportError:
            print("Warning: compression_types не найден, используя fallback")
            def create_file_info_from_compression(*args, **kwargs):
                return {"original_size": 0, "compressed_size": 0}


class PiArchiverUltra:
    """Основной класс архиватора Pi-Archiver Ultra (микро-модульная версия)"""
    
    def __init__(self, cache_dir: str = None, 
                 index_dir: str = None,
                 pi_precision: int = 1000000,
                 config_file: str = None):
        # Загружаем конфигурацию
        self.config = self._load_config(config_file)
        
        # Используем текущую директорию для работы
        current_dir = Path.cwd()
        if cache_dir is None:
            pi_file_path = Path(self.config.get('pi_file_path', 'pi_storage'))
            cache_dir = current_dir / pi_file_path.parent
        if index_dir is None:
            index_dir = current_dir
            
        # Создаем директории если не существуют
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        
        print(f"Кэш π: {cache_dir}")
        print(f"Индексы: {index_dir}")
        print(f"Ищем файл π: {cache_dir / 'pi_1000000_digits.txt'}")
        
        # Инициализируем основные компоненты
        self.pi_generator = PiGenerator(cache_dir)
        self.search_engine = PiSearchEngine(self.pi_generator)
        self.compression_core = CompressionCore(self.pi_generator)
        self.index_manager = IndexManager(index_dir)
        self.pi_precision = pi_precision or self.config.get('default_precision', 1000000)
        
        # Инициализируем микро-модульные операционные компоненты
        self.pi_ops = PiGeneratorOperations(self.pi_generator)
        self.compression_ops = DataCompressionOperations(self.compression_core)
        self.system_ops = SystemInfoOperations()
        self.extract_ops = ExtractOperations(self.pi_generator, self.compression_core)
        
        # Настройка логирования
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
    
    def archive_file(self, input_path: str, output_name: Optional[str] = None, 
                    output_dir: Optional[str] = None, use_gpu: bool = False, 
                    num_workers: int = None, no_backup: bool = False, 
                    force_regenerate: bool = False) -> str:
        """
        Архивирует один файл с использованием микро-модульной архитектуры
        
        Args:
            input_path: путь к исходному файлу
            output_name: имя архива
            output_dir: директория сохранения
            use_gpu: использовать GPU
            num_workers: количество потоков
            no_backup: отключить бэкап
            force_regenerate: принудительно перегенерировать π
            
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
            output_path = Path.cwd() / output_name
        
        self.logger.info(f"Начало архивации: {input_path}")
        self.logger.info(f"Размер файла: {input_path.stat().st_size:,} байт")
        print(f"📁 Директория сохранения: {output_path.parent}")
        
        start_time = time.time()
        
        # 1. Генерируем π с использованием PiGeneratorOperations
        pi_digits = self.pi_ops.generate_pi_for_compression(
            self.pi_precision, use_gpu, num_workers, force_regenerate
        )
        
        # 2. Читаем файл
        with open(input_path, 'rb') as f:
            file_data = f.read()
        
        # 3. Сжимаем данные с использованием DataCompressionOperations
        blocks, stats, real_xor_key = self.compression_ops.compress_file_data(
            file_data, pi_digits, num_workers
        )
        
        # 4. Создаем информацию о файле
        file_info = create_file_info_from_compression(
            str(input_path), blocks, stats, real_xor_key, self.pi_precision
        )
        
        # 5. Создаем и сохраняем индекс
        print("📦 Создание индекса архива...")
        index = self.index_manager.create_index([file_info], self.pi_precision)
        index_path = self.index_manager.save_index(index, output_path.name)
        
        # 6. Сохраняем сжатые блоки (если нужно)
        if not no_backup:
            self._save_compressed_blocks(blocks, output_path.stem)
        
        total_time = time.time() - start_time
        
        # Вывод статистики
        self._print_archive_statistics(input_path, index_path, total_time, stats)
        
        return output_name
    
    def extract_file(self, archive_name: str, output_dir: str = ".") -> List[str]:
        """
        Разархивирует архив с использованием микро-модульной архитектуры
        
        Args:
            archive_name: имя архива
            output_dir: директория для извлечения
            
        Returns:
            список извлеченных файлов
        """
        print(f"Извлечение архива: {archive_name}...")
        
        try:
            index = self.index_manager.load_index_by_archive_name(archive_name)
        except Exception as e:
            print(f"Ошибка загрузки индекса: {e}")
            return []
        
        # Используем ExtractOperations для извлечения
        extracted_files = self.extract_ops.extract_files_from_index(
            index, output_dir, archive_name
        )
        
        return extracted_files
    
    def print_system_info(self, num_workers: int = None):
        """Выводит информацию о системе с использованием SystemInfoOperations"""
        self.system_ops.print_system_info(num_workers)
    
    def get_optimal_workers(self) -> int:
        """Возвращает оптимальное количество потоков"""
        return self.system_ops.get_optimal_workers()
    
    def _save_compressed_blocks(self, blocks: List, archive_name: str):
        """Сохраняет сжатые блоки в отдельный файл"""
        blocks_file = Path.cwd() / f"{archive_name}.blocks"
        
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
    
    def _print_archive_statistics(self, input_path: Path, index_path: Path, 
                                 total_time: float, stats):
        """Выводит статистику архивации"""
        file_size_mb = input_path.stat().st_size / (1024 * 1024)
        time_per_mb = total_time / file_size_mb if file_size_mb > 0 else total_time
        
        print(f"Архивация завершена за {total_time:.2f} сек")
        
        # Используем реальный размер архива для коэффициента сжатия
        archive_size = Path(index_path).stat().st_size
        real_compression_ratio = input_path.stat().st_size / archive_size if archive_size > 0 else 1.0
        print(f"Коэффициент сжатия: {real_compression_ratio:.2f}x")
        print(f"Найдено блоков: {stats.blocks_found}/{stats.blocks_total}")
        print(f"⏱️  Скорость: {file_size_mb/total_time:.2f} MB/сек")
        print(f"✅ Архив сохранен: {index_path}")
        print(f"📁 Путь к архиву: {Path(index_path).absolute()}")
        print(f"📊 Размер архива: {Path(index_path).stat().st_size:,} байт")
        
        # Прогноз для похожих файлов
        if file_size_mb > 0:
            print(f"🔮 Прогноз для {file_size_mb:.1f}MB файла: ~{time_per_mb:.1f} сек")
    
    def _load_config(self, config_file: str = None) -> dict:
        """Загружает конфигурацию из YAML файла"""
        if config_file is None:
            current_dir = Path.cwd()
            project_dir = Path(__file__).parent.parent.parent
            
            config_paths = [
                current_dir / "pi_config.yaml",
                project_dir / "pi_config.yaml",
                current_dir / ".pi_config.yaml",
                project_dir / ".pi_config.yaml"
            ]
            
            for config_path in config_paths:
                if config_path.exists():
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            return yaml.safe_load(f) or {}
                    except Exception as e:
                        print(f"Ошибка загрузки конфигурации из {config_path}: {e}")
        
        # Конфигурация по умолчанию
        return {
            'pi_file_path': 'pi_storage/pi_1000000_digits.txt',
            'default_precision': 1000000,
            'use_existing_file': True,
            'custom_pi_directory': 'custom_pi',
            'auto_generate': True
        }


def main():
    """Точка входа для командной строки"""
    parser = argparse.ArgumentParser(description='Pi-Archiver Ultra - Архиватор на основе числа π (микро-модульная версия)')
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда архивации
    archive_parser = subparsers.add_parser('archive', help='Архивировать файлы')
    archive_parser.add_argument('files', nargs='+', help='Файлы для архивации')
    archive_parser.add_argument('-o', '--output', help='Имя архива')
    archive_parser.add_argument('-d', '--directory', help='Директория для сохранения архива')
    archive_parser.add_argument('--gpu', action='store_true', help='Использовать GPU')    
    archive_parser.add_argument("--workers", type=int, help="Количество потоков")
    archive_parser.add_argument("--no-backup", action="store_true", help="Отключить сохранение бэкапа блоков")
    archive_parser.add_argument("--force-regenerate", action="store_true", help="Принудительно перегенерировать π")
    
    # Команда извлечения
    extract_parser = subparsers.add_parser('extract', help='Извлечь архив')
    extract_parser.add_argument('archive', help='Имя архива')
    extract_parser.add_argument('-o', '--output', default='.', help='Директория для извлечения')
    
    # Команда информации
    info_parser = subparsers.add_parser('info', help='Информация об архиве')
    info_parser.add_argument('archive', help='Имя архива')
    
    # Команда системной информации
    sysinfo_parser = subparsers.add_parser('sysinfo', help='Системная информация')
    sysinfo_parser.add_argument("--workers", type=int, help="Проверить количество потоков")
    
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return
    
    # Создаем архиватор
    archiver = PiArchiverUltra(pi_precision=getattr(args, 'precision', 1000000))
    
    try:
        if args.command == 'archive':
            if len(args.files) == 1:
                archiver.archive_file(
                    args.files[0], args.output, args.directory, args.gpu, 
                    args.workers, getattr(args, "no_backup", False), 
                    getattr(args, "force_regenerate", False)
                )
            else:
                output_name = args.output or f"archive_{int(time.time())}.piarc"
                # TODO: Реализовать archive_multiple_files в микро-модульной архитектуре
                print("Мультиархивация в микро-модульной версии пока не реализована")
        
        elif args.command == 'extract':
            archiver.extract_file(args.archive, args.output)
        
        elif args.command == 'info':
            info = archiver.index_manager.get_index_statistics(args.archive)
            print(f"Информация об архиве: {args.archive}")
            print(f"Версия: {info['basic_info']['version']}")
            print(f"Файлов: {info['basic_info']['total_files']}")
            print(f"Исходный размер: {info['size_info']['original_size']:,} байт")
            print(f"Сжатый размер: {info['size_info']['compressed_size']:,} байт")
            print(f"Коэффициент сжатия: {info['size_info']['compression_ratio']:.2f}x")
        
        elif args.command == 'sysinfo':
            archiver.print_system_info(args.workers)
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
