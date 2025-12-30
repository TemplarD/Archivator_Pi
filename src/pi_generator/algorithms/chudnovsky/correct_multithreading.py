#!/usr/bin/env python3
"""
Исправленная многопоточная реализация Chudnovsky с правильным разделением диапазонов
"""

import os
import time
import threading
from decimal import Decimal, getcontext
from typing import Optional, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

class CorrectChudnovskyBinarySplitting:
    """Исправленная реализация многопоточного Chudnovsky"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
    
    def get_algorithm_name(self) -> str:
        return "Chudnovsky (Correct Binary Splitting)"
    
    def compute_pi(self, digits: int, num_workers: int = 4, progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Исправленная многопоточная реализация Chudnovsky
        
        Ключевое исправление: каждый worker вычисляет независимую часть ряда
        с правильными начальными значениями для своего диапазона
        """
        start_time = time.time()
        print(f"Вычисление {digits:,} цифр π с {num_workers} потоками...")
        
        # Установка точности
        precision = digits + 100
        getcontext().prec = precision
        
        # Проверяем кэш
        if self.cache_dir:
            cache_file = os.path.join(self.cache_dir, f"chudnovsky_mt_{digits}_{num_workers}.txt")
            if os.path.exists(cache_file):
                if progress_callback:
                    for i in range(0, 101, 10):
                        progress_callback(i, i, 100)
                        time.sleep(0.001)
                    progress_callback(100, 100, 100)
                
                with open(cache_file, 'r') as f:
                    result = f.read().strip()[:digits]
                    print(f"Загружено из кэша за {time.time() - start_time:.2f} сек")
                    return result
        
        # Вычисляем количество итераций
        n = int(digits / 14.18) + 3
        
        # Создаем задачи для потоков
        chunk_size = n // num_workers
        tasks = []
        
        for i in range(num_workers):
            start = i * chunk_size
            end = start + chunk_size if i < num_workers - 1 else n
            tasks.append((i, start, end, precision))
        
        print(f"Разделение на {num_workers} потоков по ~{chunk_size:,} итераций")
        
        # Запускаем многопоточные вычисления
        results = []
        completed = 0
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_task = {executor.submit(self._compute_chunk_correct, task): task for task in tasks}
            
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    # Вызываем основной callback
                    if progress_callback:
                        progress = (completed / num_workers) * 100
                        progress_callback(progress, completed, num_workers)
                        
                except Exception as e:
                    print(f"Ошибка в потоке: {e}")
        
        # Комбинируем результаты
        total_S = Decimal(0)
        
        for i, result in enumerate(results):
            S_part, P_part, Q_part = result
            total_S += S_part
        
        # Вычисляем π
        sqrt_10005 = Decimal(10005).sqrt()
        pi = (Decimal(426880) * sqrt_10005) / total_S
        
        # Обрезаем до нужной длины
        pi_str = str(pi)[:digits]
        
        # Сохраняем в кэш
        if self.cache_dir:
            with open(cache_file, 'w') as f:
                f.write(pi_str)
        
        elapsed = time.time() - start_time
        print(f"Вычисление завершено за {elapsed:.2f} сек")
        
        if progress_callback:
            progress_callback(100, num_workers, num_workers)
        
        return pi_str
    
    @staticmethod
    def _compute_chunk_correct(args: Tuple[int, int, int, int]) -> Tuple[Decimal, Decimal, Decimal]:
        """
        ИСПРАВЛЕННАЯ worker функция
        
        Ключевое исправление: вычисляем каждый член ряда независимо,
        а не пытаемся продолжать рекуррентные соотношения через границы диапазонов
        """
        worker_id, start, end, precision = args
        getcontext().prec = precision
        
        # Константы
        A = Decimal(13591409)
        B = Decimal(545140134)
        C = Decimal(640320)
        C3_OVER_24 = C**3 / Decimal(24)
        
        # Частичная сумма
        S = Decimal(0)
        
        # Вычисляем свою часть ряда
        for k in range(start, end):
            if k == 0:
                # Для k=0: T_0 = A
                term = A
            else:
                # Вычисляем множитель для P_k
                M = (6*k - 5) * (2*k - 1) * (6*k - 1)
                
                # Вычисляем P_k и Q_k напрямую (без рекурсии через границы)
                # Это менее эффективно, но математически корректно
                P = Decimal(1)
                Q = Decimal(1)
                
                # Вычисляем P_k от 0 до k
                for j in range(1, k + 1):
                    M_j = (6*j - 5) * (2*j - 1) * (6*j - 1)
                    P *= (-M_j)
                    Q *= (j**3 * C3_OVER_24)
                
                # Вычисляем член ряда
                K_term = A + B * k
                term = (P * K_term) / Q
            
            # Добавляем к частичной сумме
            S += term
        
        # Возвращаем частичную сумму
        return S, Decimal(1), Decimal(0)

def test_correct_multithreading():
    """Тест исправленной многопоточности"""
    print("🧪 Тест исправленной многопоточности:")
    print("=" * 60)
    
    generator = CorrectChudnovskyBinarySplitting()
    
    # Тест с 2 потоками
    print("📊 2 потока (1000 цифр): ", end="")
    start = time.time()
    result2 = generator.compute_pi(1000, num_workers=2)
    elapsed2 = time.time() - start
    correct2 = result2.startswith("3.14159265358979323846264338327950288419716939937510")
    print(f"{elapsed2:.3f}s, коррект: {correct2}")
    print(f"   Результат: {result2[:50]}...")
    
    # Тест с 4 потоками
    print("📊 4 потока (1000 цифр): ", end="")
    start = time.time()
    result4 = generator.compute_pi(1000, num_workers=4)
    elapsed4 = time.time() - start
    speedup = elapsed2 / elapsed4 if elapsed4 > 0 else 0
    correct4 = result4.startswith("3.14159265358979323846264338327950288419716939937510")
    print(f"{elapsed4:.3f}s, ускорение: {speedup:.2f}x, коррект: {correct4}")
    print(f"   Результат: {result4[:50]}...")
    
    print()
    print("🎯 Итог:")
    print(f"2 потока: {'✅' if correct2 else '❌'} {'корректен' if correct2 else 'НЕ корректен'}")
    print(f"4 потока: {'✅' if correct4 else '❌'} {'корректен' if correct4 else 'НЕ корректен'}")
    
    if correct2 and correct4:
        print("🎉🎉🎉 МНОГОПОТОЧНОСТЬ ИСПРАВЛЕНА! 🎉🎉🎉")
        print(f"🚀 Ускорение 4 потока: {speedup:.2f}x")
        return True
    else:
        print("❌ Все еще есть проблемы")
        return False

if __name__ == "__main__":
    test_correct_multithreading()
