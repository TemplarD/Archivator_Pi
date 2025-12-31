#!/usr/bin/env python3
"""
Логирование архивации Pi-Archiver
Детальная информация о процессе сжатия и поиска в π
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class BlockSearchInfo:
    """Информация о поиске блока"""
    block_id: int
    block_size: int
    block_hash: str
    search_attempts: List[Dict]
    found: bool
    final_position: Optional[Tuple[int, int]]
    backup_used: bool
    search_time: float

@dataclass
class CompressionSessionInfo:
    """Информация о сессии архивации"""
    session_id: str
    timestamp: str
    original_file: str
    original_size: int
    compressed_file: str
    backup_enabled: bool
    adaptive_search: bool
    block_size_range: Tuple[int, int]
    total_blocks: int
    found_blocks: int
    backup_blocks: int
    compression_ratio: float
    total_time: float
    success_rate: float
    pi_digits_used: int
    search_ranges: List[Dict]

class CompressionLogger:
    """Логгер архивации с детальной информацией"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.current_session: Optional[CompressionSessionInfo] = None
        self.block_searches: List[BlockSearchInfo] = []
        
    def start_session(self, original_file: str, compressed_file: str, 
                      original_size: int, backup_enabled: bool = True,
                      adaptive_search: bool = True, 
                      block_size_range: Tuple[int, int] = (4, 16)) -> str:
        """Начинает новую сессию архивации"""
        session_id = f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{int(time.time())}"
        
        self.current_session = CompressionSessionInfo(
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            original_file=original_file,
            original_size=original_size,
            compressed_file=compressed_file,
            backup_enabled=backup_enabled,
            adaptive_search=adaptive_search,
            block_size_range=block_size_range,
            total_blocks=0,
            found_blocks=0,
            backup_blocks=0,
            compression_ratio=0.0,
            total_time=0.0,
            success_rate=0.0,
            pi_digits_used=0,
            search_ranges=[]
        )
        
        self.block_searches = []
        return session_id
    
    def log_block_search(self, block_id: int, block_data: bytes, 
                        search_attempts: List[Dict], found: bool,
                        final_position: Optional[Tuple[int, int]] = None,
                        backup_used: bool = False, search_time: float = 0.0) -> None:
        """Логирует поиск отдельного блока"""
        block_hash = f"{hash(block_data) & 0xFFFFFFFF:08X}"
        
        search_info = BlockSearchInfo(
            block_id=block_id,
            block_size=len(block_data),
            block_hash=block_hash,
            search_attempts=search_attempts,
            found=found,
            final_position=final_position,
            backup_used=backup_used,
            search_time=search_time
        )
        
        self.block_searches.append(search_info)
    
    def log_search_range(self, block_size: int, start_pos: int, end_pos: int, 
                        success: bool, time_spent: float) -> None:
        """Логирует диапазон поиска"""
        if self.current_session:
            range_info = {
                'block_size': block_size,
                'start_pos': start_pos,
                'end_pos': end_pos,
                'range_length': end_pos - start_pos,
                'success': success,
                'time_spent': time_spent
            }
            self.current_session.search_ranges.append(range_info)
    
    def finish_session(self, compressed_size: int, pi_digits_used: int, 
                      total_time: float) -> Dict:
        """Завершает сессию и сохраняет лог"""
        if not self.current_session:
            return {}
        
        # Обновляем статистику
        self.current_session.total_blocks = len(self.block_searches)
        self.current_session.found_blocks = sum(1 for bs in self.block_searches if bs.found)
        self.current_session.backup_blocks = sum(1 for bs in self.block_searches if bs.backup_used)
        self.current_session.compression_ratio = self.current_session.original_size / compressed_size if compressed_size > 0 else 0
        self.current_session.total_time = total_time
        self.current_session.success_rate = self.current_session.found_blocks / self.current_session.total_blocks if self.current_session.total_blocks > 0 else 0
        self.current_session.pi_digits_used = pi_digits_used
        
        # Создаем полный лог
        full_log = {
            'session_info': asdict(self.current_session),
            'block_searches': [asdict(bs) for bs in self.block_searches],
            'summary': self._generate_summary()
        }
        
        # Сохраняем в файл
        log_file = self.log_dir / f"{self.current_session.session_id}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(full_log, f, indent=2, ensure_ascii=False)
        
        # Создаем удобный для чтения отчет
        self._create_readable_report(log_file)
        
        return full_log
    
    def _generate_summary(self) -> Dict:
        """Генерирует сводную информацию"""
        if not self.current_session or not self.block_searches:
            return {}
        
        # Анализируем размеры блоков
        block_sizes = [bs.block_size for bs in self.block_searches]
        search_times = [bs.search_time for bs in self.block_searches]
        
        # Анализируем попытки поиска
        total_attempts = sum(len(bs.search_attempts) for bs in self.block_searches)
        successful_adaptive_searches = 0
        
        for bs in self.block_searches:
            if len(bs.search_attempts) > 1 and bs.found:
                successful_adaptive_searches += 1
        
        return {
            'block_size_stats': {
                'min': min(block_sizes),
                'max': max(block_sizes),
                'avg': sum(block_sizes) / len(block_sizes)
            },
            'search_time_stats': {
                'total': sum(search_times),
                'avg': sum(search_times) / len(search_times),
                'max': max(search_times)
            },
            'search_efficiency': {
                'total_attempts': total_attempts,
                'avg_attempts_per_block': total_attempts / len(self.block_searches),
                'successful_adaptive_searches': successful_adaptive_searches,
                'adaptive_success_rate': successful_adaptive_searches / len(self.block_searches) if self.block_searches else 0
            },
            'overall_assessment': self._assess_compression_quality()
        }
    
    def _assess_compression_quality(self) -> Dict:
        """Оценивает качество сжатия"""
        if not self.current_session:
            return {}
        
        success_rate = self.current_session.success_rate
        compression_ratio = self.current_session.compression_ratio
        
        # Определяем качество
        if success_rate >= 0.8 and compression_ratio >= 2.0:
            quality = "Отличное"
            recommendation = "Сжатие прошло успешно, высокая эффективность"
        elif success_rate >= 0.6 and compression_ratio >= 1.5:
            quality = "Хорошее"
            recommendation = "Сжатие успешное, можно улучшить увеличив базу π"
        elif success_rate >= 0.4 and compression_ratio >= 1.2:
            quality = "Удовлетворительное"
            recommendation = "Сжатие работает, но нужна оптимизация алгоритма"
        else:
            quality = "Плохое"
            recommendation = "Сжатие неэффективно, рекомендуется изменить параметры"
        
        return {
            'quality_rating': quality,
            'success_rate': success_rate,
            'compression_ratio': compression_ratio,
            'recommendation': recommendation,
            'file_fully_found': success_rate == 1.0,
            'partial_recovery_possible': success_rate >= 0.5
        }
    
    def _create_readable_report(self, log_file: Path) -> None:
        """Создает удобный для чтения отчет"""
        report_file = log_file.with_suffix('.txt')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("📊 ОТЧЕТ ОБ АРХИВАЦИИ PI-ARCHIVER\n")
            f.write("=" * 50 + "\n\n")
            
            # Информация о сессии
            si = self.current_session
            f.write("🔍 ИНФОРМАЦИЯ О СЕССИИ:\n")
            f.write(f"ID сессии: {si.session_id}\n")
            f.write(f"Время: {si.timestamp}\n")
            f.write(f"Исходный файл: {si.original_file}\n")
            f.write(f"Сжатый файл: {si.compressed_file}\n")
            f.write(f"Размер исходного: {si.original_size:,} байт\n")
            f.write(f"Бэкап включен: {'Да' if si.backup_enabled else 'Нет'}\n")
            f.write(f"Адаптивный поиск: {'Да' if si.adaptive_search else 'Нет'}\n")
            f.write(f"Диапазон блоков: {si.block_size_range[0]}-{si.block_size_range[1]} байт\n\n")
            
            # Результаты
            f.write("📈 РЕЗУЛЬТАТЫ СЖАТИЯ:\n")
            f.write(f"Всего блоков: {si.total_blocks}\n")
            f.write(f"Найдено в π: {si.found_blocks} ({si.success_rate:.1%})\n")
            f.write(f"Использовано бэкап: {si.backup_blocks}\n")
            f.write(f"Коэффициент сжатия: {si.compression_ratio:.2f}x\n")
            f.write(f"Время обработки: {si.total_time:.2f} сек\n")
            f.write(f"Использовано цифр π: {si.pi_digits_used:,}\n\n")
            
            # Оценка качества
            summary = self._generate_summary()
            assessment = summary.get('overall_assessment', {})
            f.write("🎯 ОЦЕНКА КАЧЕСТВА:\n")
            f.write(f"Качество: {assessment.get('quality_rating', 'N/A')}\n")
            f.write(f"Файл полностью найден: {'Да' if assessment.get('file_fully_found', False) else 'Нет'}\n")
            f.write(f"Частичное восстановление: {'Да' if assessment.get('partial_recovery_possible', False) else 'Нет'}\n")
            f.write(f"Рекомендация: {assessment.get('recommendation', 'N/A')}\n\n")
            
            # Детальная информация о блоках
            f.write("🔍 ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О БЛОКАХ:\n")
            f.write("-" * 50 + "\n")
            
            for bs in self.block_searches:
                f.write(f"Блок #{bs.block_id}: ")
                f.write(f"{bs.block_size} байт, хеш {bs.block_hash}\n")
                f.write(f"  Найден: {'Да' if bs.found else 'Нет'}")
                if bs.found and bs.final_position:
                    f.write(f" (позиция {bs.final_position[0]}-{bs.final_position[1]})")
                f.write(f"\n")
                f.write(f"  Бэкап: {'Да' if bs.backup_used else 'Нет'}\n")
                f.write(f"  Попыток поиска: {len(bs.search_attempts)}\n")
                f.write(f"  Время поиска: {bs.search_time:.3f} сек\n")
                
                if bs.search_attempts:
                    f.write("  Попытки:\n")
                    for i, attempt in enumerate(bs.search_attempts):
                        f.write(f"    {i+1}. Размер: {attempt.get('block_size', 'N/A')}, "
                               f"диапазон: {attempt.get('range_start', 'N/A')}-{attempt.get('range_end', 'N/A')}, "
                               f"результат: {'Успех' if attempt.get('success', False) else 'Провал'}\n")
                f.write("\n")
            
            # Диапазоны поиска
            if si.search_ranges:
                f.write("🔍 ДИАПАЗОНЫ ПОИСКА:\n")
                f.write("-" * 30 + "\n")
                for i, range_info in enumerate(si.search_ranges):
                    f.write(f"{i+1}. Размер {range_info['block_size']}: "
                           f"{range_info['start_pos']:,}-{range_info['end_pos']:,} "
                           f"(длина: {range_info['range_length']:,}), "
                           f"успех: {'Да' if range_info['success'] else 'Нет'}, "
                           f"время: {range_info['time_spent']:.3f} сек\n")

def get_logger() -> CompressionLogger:
    """Возвращает экземпляр логгера"""
    return CompressionLogger()
