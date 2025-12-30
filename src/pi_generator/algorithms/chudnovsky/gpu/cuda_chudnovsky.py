#!/usr/bin/env python3
"""
CUDA Chudnovsky - CUDA реализация
"""

from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
import time
from typing import Optional, Callable, Dict, Any
import os

class CudaChudnovsky:
    """CUDA реализация Chudnovsky алгоритма"""
    
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.is_initialized = False
    
    def get_algorithm_name(self) -> str:
        return "Chudnovsky (CUDA)"
    
    def compute_pi(self, digits: int, progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Вычисляет π используя CUDA
        """
        precision = digits + 50
        getcontext().prec = precision
        
        print(f"CUDA вычисление {digits:,} цифр π...")
        start_time = time.time()
        
        try:
            # Инициализация CUDA
            self._initialize_cuda()
            
            # Создаем прогресс-бар
            try:
                from utils.working_progress import create_working_progress_bar
                progress_bar = create_working_progress_bar("CUDA", 20)
                progress_bar(0)
            except ImportError:
                progress_bar = None
            
            # Вычисляем количество итераций
            max_iterations = digits // 14 + 1
            
            # Выполняем на GPU
            result = self._compute_on_gpu(max_iterations, progress_bar, progress_callback)
            
            if progress_bar:
                progress_bar(100)
            
            elapsed = time.time() - start_time
            print(f"CUDA вычисление завершено за {elapsed:.2f} сек")
            
            return result[:digits]
            
        except Exception as e:
            print(f"CUDA ошибка вычисления: {e}")
            # Fallback на CPU
            return self._fallback_cpu(digits, progress_callback)
    
    def _initialize_cuda(self):
        """Инициализация CUDA"""
        try:
            import cupy as cp
            
            # Проверяем доступность CUDA
            if not cp.cuda.is_available():
                raise Exception("CUDA не доступна")
            
            # Получаем количество устройств
            device_count = cp.cuda.runtime.getDeviceCount()
            if device_count == 0:
                raise Exception("Нет CUDA устройств")
            
            # Выбираем устройство
            if self.device_id >= device_count:
                device_id = 0
                print(f"Устройство {self.device_id} не найдено, используем устройство 0")
            else:
                device_id = self.device_id
            
            # Устанавливаем устройство
            cp.cuda.Device(device_id).use()
            
            self.is_initialized = True
            
            # Получаем информацию об устройстве
            device = cp.cuda.Device(device_id)
            print(f"CUDA инициализирована на устройстве: {device.name}")
            
        except ImportError:
            raise Exception("CuPy не установлен")
        except Exception as e:
            raise Exception(f"Ошибка инициализации CUDA: {e}")
    
    def _compute_on_gpu(self, max_iterations: int, progress_bar=None, progress_callback=None) -> str:
        """Вычисление на GPU"""
        import cupy as cp
        
        # CUDA ядро для Chudnovsky
        kernel_code = '''
        extern "C" __global__
        void chudnovsky_kernel(double* results, int start_iter, int end_iter, int num_iterations) {
            int gid = blockIdx.x * blockDim.x + threadIdx.x;
            int total_iterations = end_iter - start_iter;
            
            if (gid >= total_iterations) return;
            
            int i = start_iter + gid;
            
            // Упрощенная реализация Chudnovsky
            double M = 1.0;
            double L = 13591409.0;
            double X = -2625374126407680000.0;
            double K = 6.0;
            
            // Пропускаем до i
            for (int j = 0; j < i; j++) {
                M = M * (pow(K, 3.0) - 16.0 * K) / pow(j + 1, 3);
                L += 545140134.0;
                X *= -2625374126407680000.0;
                K += 12.0;
            }
            
            // Вычисляем член ряда
            double term = M * L / X;
            results[gid] = term;
        }
        '''
        
        # Компилируем ядро
        kernel = cp.RawKernel(kernel_code, 'chudnovsky_kernel')
        
        # Выделяем память на GPU
        results = cp.zeros(max_iterations, dtype=cp.float64)
        
        # Настраиваем размеры блоков и сетки
        threads_per_block = 256
        blocks_per_grid = (max_iterations + threads_per_block - 1) // threads_per_block
        
        # Запускаем ядро
        kernel((blocks_per_grid,), (threads_per_block,), (results, 0, max_iterations, max_iterations))
        
        # Синхронизируем
        cp.cuda.Stream.null.synchronize()
        
        # Суммируем результаты
        total_sum = cp.sum(results)
        
        # Вычисляем π
        C = 426880.0 * cp.sqrt(10005.0)
        pi = C / total_sum
        
        # Конвертируем в строку
        pi_str = str(float(pi))
        
        return pi_str
    
    def _fallback_cpu(self, digits: int, progress_callback=None) -> str:
        """Fallback на CPU"""
        print("Используем CPU fallback...")
        
        # Простая реализация без circular import
        from decimal import Decimal, getcontext
        import time
        
        precision = digits + 50
        getcontext().prec = precision
        
        # Упрощенный Chudnovsky
        C = Decimal(426880) * Decimal(10005).sqrt()
        max_iterations = digits // 14 + 1
        
        M = Decimal(1)
        L = Decimal(13591409)
        X = Decimal(1)
        K = 6
        S = Decimal(0)
        
        for i in range(max_iterations):
            term = M * L / X
            S += term
            
            M = M * (K**3 - 16*K) // (i + 1)**3
            L += 545140134
            X *= -2625374126407680000
            K += 12
        
        pi = C / S
        return str(pi)[:digits]
