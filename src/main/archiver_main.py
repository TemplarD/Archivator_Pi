import struct
#!/usr/bin/env python3
"""
Основной модуль Pi-Archiver Ultra
Реализует архивацию и разархивацию файлов с использованием числа π
"""

import os
import sys
import time
import hashlib
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
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
import multiprocessing as mp
import platform
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
            index_dir = current_dir  # Текущая директория, а не подпапка!
            
        # Создаем директории если не существуют
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        # index_dir - это текущая директория, ее создавать не нужно
        
        print(f"Кэш π: {cache_dir}")
        print(f"Индексы: {index_dir}")
        print(f"Ищем файл π: {cache_dir / 'pi_1000000_digits.txt'}")
        
        self.pi_generator = PiGenerator(cache_dir)
        self.search_engine = PiSearchEngine(self.pi_generator)
        self.compression_core = CompressionCore(self.pi_generator)
        self.index_manager = IndexManager(index_dir)
        self.pi_precision = pi_precision or self.config.get('default_precision', 1000000)
        
        # Настройка логирования
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
    
    def _get_system_info(self) -> dict:
        """Возвращает информацию о системе и потоках"""
        info = {
            'platform': f'{platform.system()} {platform.release()}',
            'processor': platform.processor(),
            'cpu_count_logical': mp.cpu_count(),
            'available_cores': mp.cpu_count()
        }
        
        # Получаем количество доступных ядер для текущего процесса
        try:
            import os
            info['available_cores'] = len(os.sched_getaffinity(0))
        except AttributeError:
            pass
        
        # Анализируем архитектуру процессоров
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                
                # Количество физических процессоров
                physical_ids = set()
                for line in cpuinfo.split('\n'):
                    if line.startswith('physical id'):
                        physical_ids.add(line.split(':')[1].strip())
                
                # Количество ядер на процессор
                cores_per_cpu = None
                for line in cpuinfo.split('\n'):
                    if line.startswith('cpu cores'):
                        cores_per_cpu = int(line.split(':')[1].strip())
                        break
                
                info['physical_processors'] = len(physical_ids)
                info['cores_per_processor'] = cores_per_cpu
                info['total_physical_cores'] = len(physical_ids) * (cores_per_cpu or 1)
                
        except Exception as e:
            # Запасной вариант
            info['physical_processors'] = 1
            info['cores_per_processor'] = info['cpu_count_logical']
            info['total_physical_cores'] = info['cpu_count_logical']
        
        return info
    
    def _print_thread_info(self, num_workers: int = None):
        """Выводит информацию о потоках и рекомендациях"""
        info = self._get_system_info()
        
        print('=== Информация о потоках и процессорах ===')
        print(f'Платформа: {info["platform"]}')
        print(f'Процессор: {info["processor"]}')
        print(f'Физических процессоров: {info["physical_processors"]}')
        print(f'Ядер на процессор: {info["cores_per_processor"]}')
        print(f'Всего физических ядер: {info["total_physical_cores"]}')
        print(f'Логических потоков: {info["cpu_count_logical"]}')
        print(f'Доступно потоков процессу: {info["available_cores"]}')
        
        if num_workers:
            print(f'Будет использоваться потоков: {num_workers}')
            efficiency = (num_workers / info['available_cores']) * 100
            print(f'Эффективность использования: {efficiency:.1f}%')
        
        # Рекомендации по количеству потоков
        if info['total_physical_cores'] >= 20:
            # Для мощных систем (2+ процессора)
            optimal_workers = min(info['total_physical_cores'], 16)
        else:
            # Для обычных систем
            optimal_workers = min(info['available_cores'], 8)
        
        print(f'Рекомендуемое количество потоков: {optimal_workers}')
        print('=' * 55)
        
        return optimal_workers
    
    def _load_config(self, config_file: str = None) -> dict:
        """Загружает конфигурацию из YAML файла"""
        if config_file is None:
            # Ищем конфигурационный файл в текущей директории и директории проекта
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
            'pi_file_path': 'pi_storage/pi_10000_digits.txt',
            'default_precision': 10000,
            'use_existing_file': True,
            'custom_pi_directory': 'custom_pi',
            'auto_generate': True
        }
        
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
    
    def archive_file(self, input_path: str, output_name: Optional[str] = None, output_dir: Optional[str] = None, use_gpu: bool = False, num_workers: int = None, no_backup: bool = False, force_regenerate: bool = False) -> str:
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
            # Сохраняем в текущую директорию по умолчанию
            output_path = Path.cwd() / output_name
        
        self.logger.info(f"Начало архивации: {input_path}")
        self.logger.info(f"Размер файла: {input_path.stat().st_size:,} байт")
        print(f"📁 Директория сохранения: {output_path.parent}")
        
        start_time = time.time()
        
        # 1. Генерируем π с реальным прогрессом
        self.logger.info("Начало генерации π")
        print("🔄 Генерация цифр π...")
        
        import time as time_module
        progress_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        
        def progress_callback(progress_percent, current_iter, total_iters):
            """Улучшенный callback для реального прогресса генерации"""
            # Расчет оставшегося времени
            elapsed = time_module.time() - start_time
            if progress_percent > 0 and progress_percent < 99.9:
                estimated_total = elapsed / (progress_percent / 100)
                remaining = estimated_total - elapsed
                if remaining > 0:
                    if remaining > 3600:
                        time_str = f" (осталось ~{remaining/3600:.1f} ч)"
                    elif remaining > 60:
                        time_str = f" (осталось ~{remaining/60:.1f} мин)"
                    else:
                        time_str = f" (осталось ~{remaining:.0f} сек)"
                else:
                    time_str = " (почти завершено)"
            elif progress_percent >= 99.9:
                time_str = " (почти завершено)"
            else:
                time_str = ""
            
            # Улучшенный прогресс-бар
            bar_length = 30
            filled_length = int(bar_length * progress_percent / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # Скорость генерации
            if elapsed > 0 and current_iter > 0:
                rate = current_iter / elapsed
                if rate > 1000:
                    rate_str = f"{rate/1000:.1f}K итер/сек"
                else:
                    rate_str = f"{rate:.0f} итер/сек"
            else:
                rate_str = ""
            
            # Детальная информация о вычислениях
            self.logger.debug(f"Итерация {current_iter}/{total_iters} ({progress_percent:.1f}%)")
            
            import sys
            # Короткий прогресс-бар
            bar_length = 20
            filled_length = int(bar_length * progress_percent / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            sys.stdout.write(f"\rπ: |{bar}| {progress_percent:3.0f}%")
            sys.stdout.flush()
        
        start_time = time_module.time()
        self.logger.info(f"Начало генерации {self.pi_precision:,} цифр π (GPU: {use_gpu})")
        
        # Передаем callback для реального прогресса
        # Определяем количество потоков для генерации π
        if num_workers is None:
            num_workers = min(mp.cpu_count(), 8)  # Ограничиваем до 8 потоков
        print(f"Используем {num_workers} потоков для генерации π\n")
        
        pi_digits = self.pi_generator.generate_pi_digits(
            self.pi_precision, use_gpu, progress_callback, num_workers, force_regenerate
        )
        
        generation_time = time_module.time() - start_time
        self.logger.info(f"Генерация π завершена, длина: {len(pi_digits):,} цифр, время: {generation_time:.2f} сек")
        print(f"\n✅ Генерация завершена! [{len(pi_digits):,} цифр за {generation_time:.2f} сек]")
        # Функция для отображения прогресса сжатия
        compression_start_time = time_module.time()
        def compression_progress_callback(progress, current, total, remaining_time=None):
            bar_length = 40
            filled_length = int(bar_length * progress / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # Скорость сжатия
            elapsed = time_module.time() - compression_start_time
            if elapsed > 0 and current > 0:
                rate = current / elapsed
                if rate > 1000:
                    rate_str = f"{rate/1000:.1f}K блок/сек"
                else:
                    rate_str = f"{rate:.0f} блок/сек"
            else:
                rate_str = ""
            
            # Время оставшееся
            if remaining_time is not None:
                if remaining_time > 3600:
                    time_str = f" (~{remaining_time/3600:.1f} ч)"
                elif remaining_time > 60:
                    time_str = f" (~{remaining_time/60:.1f} мин)"
                else:
                    time_str = f" (~{remaining_time:.0f} сек)"
            else:
                time_str = ""
            
            # Очищаем строку и выводим прогресс
            import sys
            bar_length = 20
            filled_length = int(bar_length * progress / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # Не очищаем строку полностью, только обновляем прогресс
            sys.stdout.write(f"\rСж: |{bar}| {progress:3.0f}%")
            sys.stdout.flush()
            
            if progress >= 100:
                print()  # Перенос строки после завершения сжатия

        
        # 2. Читаем файл
        with open(input_path, 'rb') as f:
            file_data = f.read()
        
        # 3. Сжимаем данные с многопоточностью
        print("Сжатие данных...")
        use_parallel = len(file_data) > 10240  # Используем параллельность для файлов > 10KB
        
        if use_parallel:
            print(f"Используем параллельное сжатие ({num_workers} потоков)...\n")
            blocks, stats = self.compression_core.compress_data_parallel(
                file_data, pi_digits, num_workers=num_workers, progress_callback=compression_progress_callback
            )
        else:
            blocks, stats = self.compression_core.compress_data(
                file_data, pi_digits, progress_callback=compression_progress_callback
            )
        
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
        if not no_backup:
            self._save_compressed_blocks(blocks, output_path.stem)
        
        total_time = time_module.time() - start_time
        
        # Оценка времени для будущих архивов
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
        
        # Подсчитываем общее количество блоков для прогресс-бара
        total_blocks = sum(len(file_info.get("blocks", [])) for file_info in index.get("files", []))
        processed_blocks = 0
        processed_files = 0
        total_files = len(index.get("files", []))
        extraction_start_time = time.time()
        
        print(f"Восстановление данных ({total_files} файлов, {total_blocks} блоков)...")
        
        def update_extraction_progress():
            """Обновляет прогресс-бар извлечения"""
            nonlocal processed_files, processed_blocks, total_files, total_blocks
            
            # Общий прогресс
            if total_blocks > 0:
                progress = (processed_blocks / total_blocks) * 100
            else:
                progress = 0
            
            # Прогресс-бар
            bar_length = 40
            filled_length = int(bar_length * progress / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # Скорость извлечения
            elapsed = time.time() - extraction_start_time
            if elapsed > 0 and processed_blocks > 0:
                rate = processed_blocks / elapsed
                if rate > 1000:
                    rate_str = f"{rate/1000:.1f}K блок/сек"
                else:
                    rate_str = f"{rate:.0f} блок/сек"
            else:
                rate_str = ""
            
            # Время
            if elapsed > 60:
                time_str = f" ({elapsed/60:.1f} мин)"
            else:
                time_str = f" ({elapsed:.0f} сек)"
            
            import sys
            bar_length = 20
            filled_length = int(bar_length * progress / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # Не очищаем строку полностью, только обновляем прогресс
            sys.stdout.write(f"\rИзв: |{bar}| {progress:3.0f}%")
            sys.stdout.flush()
        
        extracted_files = []
        
        for file_info in index.get("files", []):
            filename = file_info.get("filename")
            original_size = file_info.get("original_size")
            blocks = file_info.get("blocks", [])
            xor_key = file_info.get("xor_key", 0x3F)  # Используем ключ по умолчанию, если не сохранен
            
            if not filename or original_size is None:
                continue
            
            file_path = output_path / Path(filename).name
            print(f"\nИзвлечение: {file_path}")
            
            # Счетчик блоков для текущего файла
            file_blocks_processed = 0
            file_blocks_total = len(blocks)
            
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
                    
                    # Обновляем прогресс-бар
                    processed_blocks += 1
                    file_blocks_processed += 1
                    
                    # Обновляем прогресс реже - каждые 10 блоков или в конце
                    if file_blocks_processed % 10 == 0 or file_blocks_processed == file_blocks_total:
                        update_extraction_progress()
                
                # Счетчики для статистики восстановления
                pi_blocks = 0
                backup_blocks = 0
                for block in compression_blocks:
                    if block.found_positions():
                        pi_blocks += 1
                    else:
                        backup_blocks += 1
                
                decompressed_data = self.compression_core.decompress_data(
                    compression_blocks, pi_digits, original_size, xor_key
                )
                
                with open(file_path, "wb") as f:
                    f.write(decompressed_data)
                
                # Вывод статистики восстановления
                print(f"\n  Восстановлено: {pi_blocks} блоков из π, {backup_blocks} блоков из бэкапа")
                extracted_files.append(str(file_path))
                processed_files += 1
                
                # Финальное обновление прогресс-бара
                update_extraction_progress()
                print()  # Перенос строки после завершения файла
                
            except Exception as e:
                print(f"\nОшибка извлечения {filename}: {e}")
                continue
        
        print(f"\nИзвлечение завершено. Файлов: {len(extracted_files)}")
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
    parser = argparse.ArgumentParser(description='Pi-Archiver - Архиватор на основе числа π')
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда архивации
    archive_parser = subparsers.add_parser('archive', help='Архивировать файлы')
    archive_parser.add_argument('files', nargs='+', help='Файлы для архивации')
    archive_parser.add_argument('-o', '--output', help='Имя архива')
    archive_parser.add_argument('-d', '--directory', help='Директория для сохранения архива')
    archive_parser.add_argument('--gpu', action='store_true', help='Использовать GPU')    
    archive_parser.add_argument('--workers', type=int, default=4, help='Количество потоков')
    archive_parser.add_argument('--precision', type=int, default=10000, help='Точность генерации π')
    archive_parser.add_argument('--force-regenerate', action='store_true', help='Принудительно пересчитать π')
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
                archiver.archive_file(args.files[0], args.output, args.directory, args.gpu, args.workers, getattr(args, "no_backup", False), force_regenerate=getattr(args, "force_regenerate", False))

            else:
                output_name = args.output or f"archive_{int(time.time())}.piarc"
                archiver.archive_multiple_files(args.files, output_name, args.gpu, args.workers, getattr(args, "no_backup", False))
        
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

# Оптимизированные методы архивации
def archive_file_optimized(self, input_path: str, output_name: str = None,
                          output_dir: str = None, use_gpu: bool = False,
                          use_processes: bool = True, batch_size: int = 1000) -> str:
    """Оптимизированная архивация файла с полной многопоточностью"""
    from pathlib import Path
    import time
    
    input_path = Path(input_path)
    
    # Генерация π с многопроцессорностью
    pi_digits = self.pi_generator.generate_pi_digits_parallel(
        self.pi_precision, use_gpu=use_gpu, 
        num_workers=mp.cpu_count()
    )
    
    # Загрузка π в векторный кеш
    if hasattr(self.pi_generator.search_engine, 'load_pi_to_cache'):
        self.pi_generator.search_engine.load_pi_to_cache(pi_digits)
    
    # Чтение файла
    with open(input_path, 'rb') as f:
        file_data = f.read()
    
    # Параллельное сжатие
    blocks, stats = self.compression_core.compress_data(
        file_data, pi_digits, 
        use_processes=use_processes,
        progress_callback=self._create_progress_callback()
    )
    
    # Сохранение кеша
    if hasattr(self.pi_generator.search_engine, 'save_cache'):
        self.pi_generator.search_engine.save_cache()
    
    # Создание архива
    output_path = self._save_archive(blocks, stats, output_name, output_dir)
    
    return output_path

def extract_file_optimized(self, archive_path: str, output_path: str = None,
                          use_processes: bool = True) -> str:
    """Оптимизированное извлечение с параллельной обработкой"""
    from pathlib import Path
    
    # Загрузка архива
    archive_data = self._load_archive(archive_path)
    
    # Генерация π
    pi_digits = self.pi_generator.generate_pi_digits_parallel(
        archive_data['pi_precision'], 
        num_workers=mp.cpu_count()
    )
    
    # Параллельное восстановление
    decompressed_data = self.compression_core.decompress_data(
        archive_data['blocks'], pi_digits, 
        archive_data['original_size'],
        use_processes=use_processes
    )
    
    # Сохранение результата
    if output_path is None:
        output_path = archive_path.replace('.piarc', '_extracted')
    
    with open(output_path, 'wb') as f:
        f.write(decompressed_data)
    
    return output_path

def get_performance_stats(self) -> dict:
    """Возвращает статистику производительности"""
    stats = {
        'num_workers': mp.cpu_count(),
        'pi_precision': self.pi_precision
    }
    
    if hasattr(self.pi_generator.search_engine, 'get_cache_stats'):
        stats['cache_stats'] = self.pi_generator.search_engine.get_cache_stats()
    
    return stats

def _create_progress_callback(self):
    """Создает callback для отслеживания прогресса"""
    start_time = time.time()
    last_update = 0
    
    def callback(progress, current, total):
        nonlocal last_update
        current_time = time.time()
        
        # Ограничиваем частоту обновления до 10 раз в секунду
        if current_time - last_update < 0.1 and progress < 100:
            return
            
        last_update = current_time
        
        # Расчет оставшегося времени
        elapsed = current_time - start_time
        if progress > 0:
            total_time = elapsed * 100 / progress
            remaining = total_time - elapsed
        else:
            remaining = 0
            
        # Форматирование строки прогресса
        bar_length = 50
        filled_length = int(bar_length * progress / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Форматирование оставшегося времени
        if remaining > 3600:
            time_str = f"{remaining/3600:.1f}ч"
        elif remaining > 60:
            time_str = f"{remaining/60:.1f}м"
        else:
            time_str = f"{remaining:.0f}с"
            
        # Вывод прогресса
        sys.stdout.write(f"\rГенерация π: |{bar}| {progress:>6.2f}% ({current:>{len(str(total))}}/{total}) ~{time_str:>5} ")
        sys.stdout.flush()
        
        if progress >= 100:
            print(f"\nГотово за {elapsed:.1f} сек")
    
    return callback

# Добавляем методы в класс PiArchiverUltra
if hasattr(PiArchiverUltra, 'archive_file'):
    PiArchiverUltra.archive_file_optimized = archive_file_optimized
    PiArchiverUltra.extract_file_optimized = extract_file_optimized
    PiArchiverUltra.get_performance_stats = get_performance_stats
    PiArchiverUltra._create_progress_callback = _create_progress_callback
