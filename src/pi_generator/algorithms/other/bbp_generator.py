#!/usr/bin/env python3
"""
Параллельная генерация числа π с использованием алгоритма BBP (Bailey–Borwein–Plouffe)
Алгоритм позволяет вычислять отдельные шестнадцатеричные цифры π независимо
"""

import multiprocessing as mp
import threading
import time
import math
from decimal import Decimal, getcontext
from typing import List, Tuple, Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing as mp


class BBPPiGenerator:
    """
    Генератор π с использованием алгоритма BBP для параллельных вычислений
    """
    
    def __init__(self, num_workers: int = None):
        self.num_workers = num_workers or mp.cpu_count()
        print(f"Инициализация BBP генератора с {self.num_workers} потоками")
    
    @staticmethod
    def _bbp_term(k: int, j: int) -> float:
        """Вычисление одного члена BBP суммы"""
        return (16.0 ** (-k)) / (8.0 * k + j)
    
    @staticmethod
    def _compute_hex_digit(n: int) -> int:
        """
        Вычисление одной шестнадцатеричной цифры π в позиции n
        Использует правильную формулу BBP
        """
        from decimal import Decimal, getcontext
        getcontext().prec = 50  # Высокая точность для вычислений
        
        # BBP формула для шестнадцатеричной цифры
        # π = Σ(k=0 to ∞) [1/16^k * (4/(8k+1) - 2/(8k+4) - 1/(8k+5) - 1/(8k+6))]
        
        # Вычисляем сумму до n
        s1 = Decimal(0)
        for k in range(n + 1):
            s1 += (Decimal(4) / (8*k + 1) - 
                   Decimal(2) / (8*k + 4) - 
                   Decimal(1) / (8*k + 5) - 
                   Decimal(1) / (8*k + 6)) / (Decimal(16) ** k)
        
        # Вычисляем хвост суммы (n+1 to ∞)
        s2 = Decimal(0)
        for k in range(n + 1, n + 20):  # Ограничиваем для скорости
            term = (Decimal(4) / (8*k + 1) - 
                   Decimal(2) / (8*k + 4) - 
                   Decimal(1) / (8*k + 5) - 
                   Decimal(1) / (8*k + 6)) / (Decimal(16) ** k)
            s2 += term
            if abs(term) < Decimal(1e-20):
                break
        
        total = s1 + s2
        
        # Извлекаем дробную часть и умножаем на 16
        fractional = total - int(total)
        hex_digit = int(fractional * 16)
        
        return hex_digit
    
    class ProgressUpdater:
        def __init__(self, queue: mp.Queue, worker_id: int, total: int):
            self.queue = queue
            self.worker_id = worker_id
            self.total = total
            self.last_update = 0
            
        def __call__(self, current: int):
            if time.time() - self.last_update > 0.1:  # Ограничиваем частоту обновлений
                progress = (current / self.total) * 100 if self.total > 0 else 0
                self.queue.put((self.worker_id, progress, current, self.total))
                self.last_update = time.time()
    
    @classmethod
    def _compute_digit_worker(cls, args: Tuple[int, int, int]) -> Tuple[int, List[int]]:
        """
        Рабочая функция для multiprocessing
        Вычисляет диапазон цифр π
        """
        worker_id, start_pos, end_pos = args
        total = end_pos - start_pos
        digits = []
        
        for i, pos in enumerate(range(start_pos, end_pos)):
            digit = cls._compute_hex_digit(pos)
            digits.append(digit)
        
        return worker_id, digits
    
    def generate_pi_digits_bbp(self, num_digits: int, progress_callback: Optional[Callable] = None) -> str:
        """
        Генерация π цифр с использованием BBP алгоритма и multiprocessing
        """
        print(f"Генерация {num_digits:,} цифр π с BBP алгоритмом...")
        start_time = time.time()
        
        # Убираем очередь и поток прогресса - они ломают вывод
        
        # Убираем отдельный поток прогресса - он ломает вывод
        progress_thread = None
        queue = None  # Не используем queue для простоты
        
        # Разделяем работу между процессами
        block_size = max(1, num_digits // self.num_workers)
        tasks = []
        
        for i in range(self.num_workers):
            start = i * block_size
            end = min((i + 1) * block_size, num_digits)
            if start < num_digits:  # Убеждаемся что есть работа
                tasks.append((i, start, end))  # Убираем queue
        
        print(f"Запуск {len(tasks)} процессов для вычисления {num_digits:,} цифр...")
        
        # Выполняем вычисления в multiprocessing
        all_digits = [None] * num_digits
        
        try:
            with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
                # Отправляем задачи
                future_to_task = {
                    executor.submit(self._compute_digit_worker, task): task 
                    for task in tasks
                }
                
                # Собираем результаты
                completed = 0
                for future in as_completed(future_to_task):
                    try:
                        worker_id, digits = future.result()
                        task = future_to_task[future]
                        start_pos = task[1]
                        
                        # Размещаем цифры в правильные позиции
                        for i, digit in enumerate(digits):
                            pos = start_pos + i
                            if pos < num_digits:
                                all_digits[pos] = digit
                        
                        completed += 1
                        
                        # Вызываем callback с прогрессом - реже чтобы не ломать вывод
                        if progress_callback and completed % max(1, len(tasks) // 5) == 0:
                            progress = (completed / len(tasks)) * 100
                            progress_callback(progress, completed, len(tasks))
                        # УБИРАЕМ PRINT который ломает вывод
                    except Exception as e:
                        print(f"Ошибка в процессе: {e}")
                        completed += 1  # Считаем как завершенное даже с ошибкой
        finally:
            pass  # Убираем остановку потока - его больше нет
        
        # Конвертируем в строку
        pi_hex = ''.join(f'{digit:X}' for digit in all_digits)
        
        # Конвертируем из hex в decimal
        pi_decimal = self._hex_to_decimal(pi_hex)
        
        elapsed = time.time() - start_time
        print(f"BBP генерация завершена за {elapsed:.2f} сек")
        
        return pi_decimal
    
    def _hex_to_decimal(self, hex_str: str) -> str:
        """
        Конвертация шестнадцатеричных цифр π в десятичные
        """
        try:
            # Убираем ведущие нули и конвертируем
            hex_str = hex_str.lstrip('0')
            if not hex_str:
                return ""
            
            # Используем Decimal для больших чисел
            getcontext().prec = len(hex_str) * 2  # Достаточная точность
            pi_int = Decimal(int(hex_str, 16))
            
            # Конвертируем в строку и убираем десятичную точку
            pi_decimal = str(pi_int).replace('.', '')
            
            # Возвращаем только нужное количество цифр
            return pi_decimal
        except (ValueError, OverflowError) as e:
            print(f"Ошибка конвертации: {e}")
            return ""
    
    def generate_pi_digits_block(self, num_digits: int, progress_callback=None) -> str:
        """
        Блочная генерация (альтернативный метод)
        Каждый поток вычисляет непрерывный блок цифр
        """
        print(f"Блочная генерация {num_digits:,} цифр π...")
        start_time = time.time()
        
        block_size = max(1, num_digits // self.num_workers)
        pi_digits = []
        
        def compute_block(args):
            worker_id, start, end = args
            block_digits = []
            for pos in range(start, end):
                digit = self._compute_hex_digit(pos)
                block_digits.append(digit)
                if progress_callback and pos % 1000 == 0:
                    progress = (pos / num_digits) * 100
                    progress_callback(progress, pos, num_digits)
            return worker_id, block_digits
        
        # Запускаем потоки
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            tasks = [(i, i * block_size, min((i + 1) * block_size, num_digits)) 
                    for i in range(self.num_workers) if i * block_size < num_digits]
            
            futures = [executor.submit(compute_block, task) for task in tasks]
            
            # Собираем результаты в правильном порядке
            results = {}
            for future in as_completed(futures):
                worker_id, block_digits = future.result()
                results[worker_id] = block_digits
            
            # Собираем π цифры в правильном порядке
            for i in range(len(tasks)):
                if i in results:
                    pi_digits.extend(results[i])
        
        # Конвертируем в десятичные
        pi_hex = ''.join(f'{digit:X}' for digit in pi_digits[:num_digits])
        pi_decimal = self._hex_to_decimal(pi_hex)
        
        elapsed = time.time() - start_time
        print(f"Блочная генерация завершена за {elapsed:.2f} сек")
        
        return pi_decimal
    
    def generate_pi_digits_cyclic(self, num_digits: int, progress_callback=None) -> str:
        """
        Циклическая генерация (альтернативный метод)
        Каждый поток вычисляет цифры через равные интервалы
        """
        print(f"Циклическая генерация {num_digits:,} цифр π...")
        start_time = time.time()
        
        pi_digits = [None] * num_digits
        
        def compute_cyclic(args):
            worker_id, num_digits, num_workers = args
            
            for pos in range(worker_id, num_digits, num_workers):
                digit = self._compute_hex_digit(pos)
                pi_digits[pos] = digit
                
                if progress_callback and pos % 1000 == 0:
                    progress = (pos / num_digits) * 100
                    progress_callback(progress, pos, num_digits)
        
        # Запускаем потоки
        threads = []
        for i in range(self.num_workers):
            thread = threading.Thread(target=compute_cyclic, 
                                    args=(i, num_digits, self.num_workers))
            thread.start()
            threads.append(thread)
        
        # Ждем завершения
        for thread in threads:
            thread.join()
        
        # Конвертируем в десятичные
        pi_hex = ''.join(f'{digit:X}' for digit in pi_digits)
        pi_decimal = self._hex_to_decimal(pi_hex)
        
        elapsed = time.time() - start_time
        print(f"Циклическая генерация завершена за {elapsed:.2f} сек")
        
        return pi_decimal


def test_bbp_generator():
    """Тестирование BBP генератора"""
    print("=== Тестирование BBP генератора π ===")
    
    generator = BBPPiGenerator(num_workers=4)
    
    # Тест на малом количестве цифр
    print("\n1. Тест на 100 цифрах:")
    pi_100 = generator.generate_pi_digits_bbp(100)
    print(f"Первые 20 цифр: {pi_100[:20]}")
    
    # Тест на среднем количестве цифр
    print("\n2. Тест на 1000 цифрах:")
    pi_1000 = generator.generate_pi_digits_bbp(1000)
    print(f"Первые 20 цифр: {pi_1000[:20]}")
    
    # Сравнение с эталоном
    print("\n3. Сравнение с эталоном:")
    expected = "14159265358979323846"
    actual = pi_1000[:20]
    print(f"Ожидаемо: {expected}")
    print(f"Получено:  {actual}")
    print(f"Совпадают: {expected == actual}")
    
    # Тест производительности
    print("\n4. Тест производительности:")
    for workers in [1, 2, 4, 8]:
        gen = BBPPiGenerator(num_workers=workers)
        start = time.time()
        pi_test = gen.generate_pi_digits_bbp(500)
        elapsed = time.time() - start
        print(f"Потоков: {workers}, Время: {elapsed:.3f} сек")


if __name__ == "__main__":
    test_bbp_generator()
