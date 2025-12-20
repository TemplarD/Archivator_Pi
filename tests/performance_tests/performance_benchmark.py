#!/usr/bin/env python3
"""
Тесты производительности Pi-Archiver Ultra
Бенчмарки для всех компонентов системы
"""

import sys
import os
import time
import psutil
import threading
from pathlib import Path
from typing import Dict, List, Tuple
import json

# Добавляем путь к исходникам
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from pi_generator.pi_generator import PiGenerator
from pi_generator.gpu_pi_generator import GPUChudnovskyGenerator
from search_engine.pi_search import PiSearchEngine
from compression.compression_core import CompressionCore
from main.index_manager import IndexManager

class PerformanceBenchmark:
    """Класс для проведения бенчмарков производительности"""
    
    def __init__(self):
        self.results = {}
        self.system_info = self._get_system_info()
        
    def _get_system_info(self) -> Dict:
        """Собирает информацию о системе"""
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'python_version': sys.version,
            'platform': sys.platform
        }
    
    def benchmark_pi_generation(self, digits_list: List[int] = [1000, 10000, 100000]) -> Dict:
        """Бенчмарк генерации π"""
        print("=== Бенчмарк генерации π ===")
        
        generator = PiGenerator()
        results = {'cpu': {}, 'gpu': {}}
        
        # CPU бенчмарк
        print("CPU генерация:")
        for digits in digits_list:
            print(f"  Генерация {digits:,} цифр...")
            
            start_time = time.time()
            memory_before = psutil.Process().memory_info().rss
            
            try:
                pi_digits = generator.generate_pi_digits(digits)
                generation_time = time.time() - start_time
                memory_after = psutil.Process().memory_info().rss
                memory_used = memory_after - memory_before
                
                results['cpu'][digits] = {
                    'time': generation_time,
                    'speed': digits / generation_time,
                    'memory_mb': memory_used / 1024 / 1024,
                    'success': True,
                    'digits_generated': len(pi_digits)
                }
                
                print(f"    Время: {generation_time:.2f} сек")
                print(f"    Скорость: {digits / generation_time:.0f} цифр/сек")
                print(f"    Память: {memory_used / 1024 / 1024:.1f} MB")
                
            except Exception as e:
                results['cpu'][digits] = {
                    'time': 0,
                    'speed': 0,
                    'memory_mb': 0,
                    'success': False,
                    'error': str(e)
                }
                print(f"    Ошибка: {e}")
        
        # GPU бенчмарк (если доступен)
        try:
            gpu_generator = GPUChudnovskyGenerator()
            if gpu_generator.ctx:
                print("\nGPU генерация:")
                for digits in digits_list:
                    print(f"  Генерация {digits:,} цифр...")
                    
                    start_time = time.time()
                    try:
                        pi_digits = gpu_generator.generate_pi_digits_gpu(digits)
                        generation_time = time.time() - start_time
                        
                        results['gpu'][digits] = {
                            'time': generation_time,
                            'speed': digits / generation_time,
                            'success': True,
                            'digits_generated': len(pi_digits),
                            'device_info': gpu_generator.get_device_info()
                        }
                        
                        print(f"    Время: {generation_time:.2f} сек")
                        print(f"    Скорость: {digits / generation_time:.0f} цифр/сек")
                        
                    except Exception as e:
                        results['gpu'][digits] = {
                            'time': 0,
                            'speed': 0,
                            'success': False,
                            'error': str(e)
                        }
                        print(f"    Ошибка: {e}")
            else:
                print("GPU недоступен")
        except Exception as e:
            print(f"Ошибка инициализации GPU: {e}")
        
        return results
    
    def benchmark_search_algorithms(self, test_patterns: List[str], 
                                 pi_digits: str) -> Dict:
        """Бенчмарк алгоритмов поиска"""
        print("\n=== Бенчмарк алгоритмов поиска ===")
        
        generator = PiGenerator()
        search_engine = PiSearchEngine(generator)
        results = {}
        
        for pattern in test_patterns:
            print(f"\nПаттерн: {pattern[:20]}...")
            pattern_bytes = bytes.fromhex(pattern)
            results[pattern] = {}
            
            for algorithm in ['naive', 'rabin_karp', 'bloom']:
                print(f"  Алгоритм: {algorithm}")
                
                start_time = time.time()
                try:
                    result = search_engine.search_sequence(
                        pattern_bytes, pi_digits, algorithm
                    )
                    search_time = time.time() - start_time
                    
                    results[pattern][algorithm] = {
                        'time': search_time,
                        'found': result.found,
                        'position': result.start_pos,
                        'success': True
                    }
                    
                    print(f"    Время: {search_time:.4f} сек")
                    print(f"    Найдено: {result.found}")
                    if result.found:
                        print(f"    Позиция: {result.start_pos}")
                        
                except Exception as e:
                    results[pattern][algorithm] = {
                        'time': 0,
                        'found': False,
                        'success': False,
                        'error': str(e)
                    }
                    print(f"    Ошибка: {e}")
        
        return results
    
    def benchmark_compression(self, test_files: List[str], pi_digits: str) -> Dict:
        """Бенчмарк сжатия"""
        print("\n=== Бенчмарк сжатия ===")
        
        generator = PiGenerator()
        compressor = CompressionCore(generator)
        results = {}
        
        for file_path in test_files:
            print(f"\nФайл: {file_path}")
            
            try:
                # Читаем файл
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                print(f"  Размер: {len(file_data):,} байт")
                
                # Сжимаем
                start_time = time.time()
                memory_before = psutil.Process().memory_info().rss
                
                blocks, stats = compressor.compress_data(file_data, pi_digits)
                
                compression_time = time.time() - start_time
                memory_after = psutil.Process().memory_info().rss
                memory_used = memory_after - memory_before
                
                results[file_path] = {
                    'original_size': stats.original_size,
                    'compressed_size': stats.compressed_size,
                    'compression_ratio': stats.compression_ratio,
                    'compression_time': compression_time,
                    'compression_speed': stats.original_size / compression_time,
                    'memory_mb': memory_used / 1024 / 1024,
                    'blocks_found': stats.blocks_found,
                    'blocks_total': stats.blocks_total,
                    'success_rate': stats.blocks_found / stats.blocks_total if stats.blocks_total > 0 else 0,
                    'success': True
                }
                
                print(f"    Сжатый размер: {stats.compressed_size:,} байт")
                print(f"    Коэффициент: {stats.compression_ratio:.2f}x")
                print(f"    Время: {compression_time:.2f} сек")
                print(f"    Скорость: {stats.original_size / compression_time / 1024:.1f} KB/сек")
                print(f"    Найдено блоков: {stats.blocks_found}/{stats.blocks_total}")
                
                # Тест восстановления
                try:
                    xor_key = 0x3F
                    start_recovery = time.time()
                    recovered_data = compressor.decompress_data(
                        blocks, pi_digits, len(file_data), xor_key
                    )
                    recovery_time = time.time() - start_recovery
                    
                    integrity_ok = recovered_data == file_data
                    results[file_path]['recovery_time'] = recovery_time
                    results[file_path]['recovery_speed'] = len(file_data) / recovery_time
                    results[file_path]['integrity_ok'] = integrity_ok
                    
                    print(f"    Восстановление: {recovery_time:.2f} сек")
                    print(f"    Целостность: {'OK' if integrity_ok else 'FAILED'}")
                    
                except Exception as e:
                    results[file_path]['recovery_error'] = str(e)
                    print(f"    Ошибка восстановления: {e}")
                
            except Exception as e:
                results[file_path] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  Ошибка: {e}")
        
        return results
    
    def benchmark_parallel_processing(self, data_size: int = 1000000) -> Dict:
        """Бенчмарк параллельной обработки"""
        print("\n=== Бенчмарк параллельной обработки ===")
        
        generator = PiGenerator()
        search_engine = PiSearchEngine(generator)
        
        # Создаем тестовые блоки
        import random
        blocks = []
        for i in range(100):
            block_size = random.randint(4, 16)
            block_data = bytes([random.randint(0, 255) for _ in range(block_size)])
            blocks.append(block_data)
        
        print(f"Создано {len(blocks)} тестовых блоков")
        
        # Генерируем π
        pi_digits = generator.generate_pi_digits(100000)
        
        results = {}
        
        # Последовательная обработка
        print("Последовательная обработка:")
        start_time = time.time()
        sequential_results = []
        for block in blocks:
            result = search_engine.search_sequence(block, pi_digits)
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        results['sequential'] = {
            'time': sequential_time,
            'blocks_processed': len(sequential_results),
            'blocks_found': sum(1 for r in sequential_results if r.found),
            'success': True
        }
        
        print(f"  Время: {sequential_time:.2f} сек")
        print(f"  Найдено: {results['sequential']['blocks_found']}/{len(blocks)}")
        
        # Параллельная обработка
        print("\nПараллельная обработка:")
        import multiprocessing as mp
        
        for num_workers in [2, 4, 8]:
            if num_workers > mp.cpu_count():
                continue
                
            print(f"  Рабочих потоков: {num_workers}")
            start_time = time.time()
            
            try:
                parallel_results = search_engine.search_blocks_parallel(
                    blocks, pi_digits, num_workers
                )
                parallel_time = time.time() - start_time
                
                speedup = sequential_time / parallel_time
                
                results[f'parallel_{num_workers}'] = {
                    'time': parallel_time,
                    'blocks_processed': len(parallel_results),
                    'blocks_found': sum(1 for r in parallel_results if r.found),
                    'speedup': speedup,
                    'success': True
                }
                
                print(f"    Время: {parallel_time:.2f} сек")
                print(f"    Ускорение: {speedup:.2f}x")
                print(f"    Найдено: {results[f'parallel_{num_workers}']['blocks_found']}/{len(blocks)}")
                
            except Exception as e:
                results[f'parallel_{num_workers}'] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"    Ошибка: {e}")
        
        return results
    
    def run_full_benchmark(self) -> Dict:
        """Запускает полный бенчмарк системы"""
        print("=== Полный бенчмарк Pi-Archiver Ultra ===")
        print(f"Система: {self.system_info['platform']}")
        print(f"CPU: {self.system_info['cpu_count']} ядер")
        print(f"Память: {self.system_info['memory_total'] / 1024**3:.1f} GB")
        print()
        
        full_results = {
            'system_info': self.system_info,
            'timestamp': time.time(),
            'benchmarks': {}
        }
        
        # 1. Генерация π
        try:
            full_results['benchmarks']['pi_generation'] = self.benchmark_pi_generation()
        except Exception as e:
            full_results['benchmarks']['pi_generation'] = {'error': str(e)}
        
        # 2. Поиск
        try:
            generator = PiGenerator()
            pi_digits = generator.generate_pi_digits(50000)
            
            test_patterns = [
                "41424344",  # "ABCD"
                "48656C6C6F",  # "Hello"
                "50694172636869766572",  # "PiArchiver"
            ]
            
            full_results['benchmarks']['search'] = self.benchmark_search_algorithms(
                test_patterns, pi_digits
            )
        except Exception as e:
            full_results['benchmarks']['search'] = {'error': str(e)}
        
        # 3. Сжатие
        try:
            # Создаем тестовые файлы
            test_files = []
            test_data_dir = Path(__file__).parent / "test_data"
            test_data_dir.mkdir(exist_ok=True)
            
            # Текстовый файл
            text_file = test_data_dir / "test_text.txt"
            with open(text_file, 'wb') as f:
                f.write(b"Test text data for compression benchmark. " * 1000)
            test_files.append(str(text_file))
            
            # Бинарный файл
            binary_file = test_data_dir / "test_binary.bin"
            with open(binary_file, 'wb') as f:
                import random
                f.write(bytes([random.randint(0, 255) for _ in range(10000)]))
            test_files.append(str(binary_file))
            
            full_results['benchmarks']['compression'] = self.benchmark_compression(
                test_files, pi_digits
            )
        except Exception as e:
            full_results['benchmarks']['compression'] = {'error': str(e)}
        
        # 4. Параллельная обработка
        try:
            full_results['benchmarks']['parallel'] = self.benchmark_parallel_processing()
        except Exception as e:
            full_results['benchmarks']['parallel'] = {'error': str(e)}
        
        return full_results
    
    def save_results(self, results: Dict, filename: str = "benchmark_results.json"):
        """Сохраняет результаты бенчмарка"""
        results_file = Path(__file__).parent / filename
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nРезультаты сохранены: {results_file}")
    
    def print_summary(self, results: Dict):
        """Выводит сводку результатов"""
        print("\n=== СВОДКА РЕЗУЛЬТАТОВ ===")
        
        # Генерация π
        if 'pi_generation' in results['benchmarks']:
            pi_gen = results['benchmarks']['pi_generation']
            if 'cpu' in pi_gen and pi_gen['cpu']:
                print(f"Генерация π (CPU):")
                for digits, result in pi_gen['cpu'].items():
                    if result.get('success'):
                        print(f"  {digits:,} цифр: {result['speed']:.0f} цифр/сек")
        
        # Сжатие
        if 'compression' in results['benchmarks']:
            comp = results['benchmarks']['compression']
            successful_compressions = [r for r in comp.values() if r.get('success')]
            
            if successful_compressions:
                avg_ratio = sum(r['compression_ratio'] for r in successful_compressions) / len(successful_compressions)
                avg_speed = sum(r['compression_speed'] for r in successful_compressions) / len(successful_compressions)
                
                print(f"\nСжатие:")
                print(f"  Средний коэффициент: {avg_ratio:.2f}x")
                print(f"  Средняя скорость: {avg_speed / 1024:.1f} KB/сек")
        
        # Параллельная обработка
        if 'parallel' in results['benchmarks']:
            parallel = results['benchmarks']['parallel']
            if 'sequential' in parallel and 'parallel_4' in parallel:
                seq_time = parallel['sequential']['time']
                par_time = parallel['parallel_4']['time']
                speedup = seq_time / par_time
                
                print(f"\nПараллельная обработка:")
                print(f"  Ускорение (4 потока): {speedup:.2f}x")


if __name__ == "__main__":
    benchmark = PerformanceBenchmark()
    
    try:
        results = benchmark.run_full_benchmark()
        benchmark.save_results(results)
        benchmark.print_summary(results)
    except KeyboardInterrupt:
        print("\nБенчмарк прерван")
    except Exception as e:
        print(f"\nОшибка бенчмарка: {e}")
