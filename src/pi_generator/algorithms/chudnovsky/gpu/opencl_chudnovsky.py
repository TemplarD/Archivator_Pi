#!/usr/bin/env python3
"""
OpenCL Chudnovsky - OpenCL реализация
"""

from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
import time
from typing import Optional, Callable, Dict, Any
import os

class OpenCLChudnovsky:
    """OpenCL реализация Chudnovsky алгоритма"""
    
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.context = None
        self.is_initialized = False
    
    def get_algorithm_name(self) -> str:
        return "Chudnovsky (OpenCL)"
    
    def compute_pi(self, digits: int, progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Вычисляет π используя OpenCL
        """
        precision = digits + 50
        getcontext().prec = precision
        
        print(f"OpenCL вычисление {digits:,} цифр π...")
        start_time = time.time()
        
        try:
            # Инициализация OpenCL
            self._initialize_opencl()
            
            # Создаем прогресс-бар
            try:
                from utils.working_progress import create_working_progress_bar
                progress_bar = create_working_progress_bar("OpenCL", 20)
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
            print(f"OpenCL вычисление завершено за {elapsed:.2f} сек")
            
            return result[:digits]
            
        except Exception as e:
            print(f"OpenCL ошибка вычисления: {e}")
            # Fallback на CPU
            return self._fallback_cpu(digits, progress_callback)
    
    def _initialize_opencl(self):
        """Инициализация OpenCL"""
        try:
            import pyopencl as cl
            
            # Получаем платформы и устройства
            platforms = cl.get_platforms()
            if not platforms:
                raise Exception("Нет доступных OpenCL платформ")
            
            # Выбираем устройство
            devices = []
            for platform in platforms:
                platform_devices = platform.get_devices()
                devices.extend(platform_devices)
            
            if not devices:
                raise Exception("Нет доступных OpenCL устройств")
            
            # Выбираем устройство по ID
            if self.device_id >= len(devices):
                device = devices[0]
                print(f"Устройство {self.device_id} не найдено, используем {device.name}")
            else:
                device = devices[self.device_id]
            
            # Создаем контекст
            self.context = cl.Context([device])
            self.is_initialized = True
            
            print(f"OpenCL инициализирован на устройстве: {device.name}")
            
        except ImportError:
            raise Exception("PyOpenCL не установлен")
        except Exception as e:
            raise Exception(f"Ошибка инициализации OpenCL: {e}")
    
    def _compute_on_gpu(self, max_iterations: int, progress_bar=None, progress_callback=None) -> str:
        """Вычисление на GPU"""
        import pyopencl as cl
        
        # Создаем очередь команд
        queue = cl.CommandQueue(self.context)
        
        # OpenCL код для Chudnovsky
        kernel_code = """
        __kernel void chudnovsky_kernel(
            __global double* results,
            const int start_iter,
            const int end_iter,
            const int num_iterations
        ) {
            int gid = get_global_id(0);
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
        """
        
        # Компилируем ядро
        program = cl.Program(self.context, kernel_code).build()
        kernel = program.chudnovsky_kernel
        
        # Выделяем память на GPU
        results = cl.Buffer(self.context, cl.mem_flags.WRITE_ONLY, 
                          max_iterations * 8)  # double = 8 bytes
        
        # Запускаем ядро
        global_size = (max_iterations,)
        kernel.set_args(results, 0, max_iterations, max_iterations)
        
        cl.enqueue_nd_range_kernel(queue, (1,), None, kernel, global_size)
        
        # Читаем результаты
        result_data = empty_like(max_iterations, dtype=float64)
        cl.enqueue_copy(queue, result_data, results)
        queue.finish()
        
        # Суммируем результаты
        total_sum = sum(result_data)
        
        # Вычисляем π
        C = 426880.0 * sqrt(10005.0)
        pi = C / total_sum
        
        return str(pi)
    
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
