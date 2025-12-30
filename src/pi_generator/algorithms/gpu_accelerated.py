#!/usr/bin/env python3
"""
GPU и специализированные алгоритмы генерации π
OpenCL, CUDA, и другие ускоренные реализации
"""

from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
import time
from typing import Optional, Callable, Dict, Any
import numpy as np

class BaseGPUGenerator(ABC):
    """Базовый класс для GPU генераторов"""
    
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.is_initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """Инициализирует GPU"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Освобождает ресурсы GPU"""
        pass
    
    @abstractmethod
    def compute_pi(self, digits: int, **kwargs) -> str:
        """Вычисляет π на GPU"""
        pass

class OpenCLChudnovsky(BaseGPUGenerator):
    """OpenCL реализация Chudnovsky алгоритма"""
    
    def get_algorithm_name(self) -> str:
        return "Chudnovsky (OpenCL GPU)"
    
    def initialize(self) -> bool:
        """Инициализирует OpenCL"""
        try:
            import pyopencl as cl
            
            # Получаем доступные платформы и устройства
            platforms = cl.get_platforms()
            if not platforms:
                print("OpenCL: платформы не найдены")
                return False
            
            # Выбираем первую платформу и устройство
            platform = platforms[0]
            devices = platform.get_devices()
            
            if not devices:
                print("OpenCL: устройства не найдены")
                return False
            
            self.device = devices[self.device_id] if self.device_id < len(devices) else devices[0]
            self.context = cl.Context([self.device])
            self.queue = cl.CommandQueue(self.context)
            
            print(f"OpenCL инициализирован: {self.device.name}")
            self.is_initialized = True
            return True
            
        except ImportError:
            print("OpenCL: pyopencl не установлен")
            return False
        except Exception as e:
            print(f"OpenCL ошибка инициализации: {e}")
            return False
    
    def cleanup(self):
        """Освобождает ресурсы OpenCL"""
        if hasattr(self, 'context'):
            self.context = None
        self.is_initialized = False
    
    def compute_pi(self, digits: int, progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Вычисляет π используя OpenCL
        """
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("Не удалось инициализировать OpenCL")
        
        try:
            import pyopencl as cl
            
            precision = digits + 100
            getcontext().prec = precision
            
            print(f"OpenCL вычисление {digits:,} цифр π...")
            start_time = time.time()
            
            # OpenCL ядро для Chudnovsky
            kernel_source = """
            __kernel void chudnovsky_term(
                __global double* results,
                const int start_k,
                const int count_k,
                const double precision_factor
            ) {
                int gid = get_global_id(0);
                int k = start_k + gid;
                
                if (k >= count_k) return;
                
                // Упрощенные вычисления для GPU
                double k_d = (double)k;
                double term = 13591409.0 + 545140134.0 * k_d;
                
                // Базовая аппроксимация
                results[gid] = term / pow(640320.0, 3.0 * k_d);
            }
            """
            
            # Компилируем ядро
            program = cl.Program(self.context, kernel_source).build()
            
            # Вычисляем количество итераций
            max_iterations = digits // 14 + 1
            
            # Разделяем на батчи для GPU
            batch_size = min(1024, max_iterations)
            num_batches = (max_iterations + batch_size - 1) // batch_size
            
            # Создаем буферы
            results_buffer = cl.Buffer(self.context, cl.mem_flags.READ_WRITE, 
                                     batch_size * 8)  # double
            
            total_sum = Decimal(0)
            
            for batch in range(num_batches):
                start_k = batch * batch_size
                count_k = min(batch_size, max_iterations - start_k)
                
                if progress_callback:
                    progress = (batch / num_batches) * 100
                    progress_callback(progress, batch, num_batches)
                
                # Запускаем ядро
                program.chudnovsky_term(
                    self.queue, 
                    (count_k,), 
                    None,
                    results_buffer,
                    np.int32(start_k),
                    np.int32(max_iterations),
                    np.float64(1.0)
                )
                
                # Читаем результаты
                results = np.empty(count_k, dtype=np.float64)
                cl.enqueue_copy(self.queue, results, results_buffer)
                
                # Суммируем результаты
                for result in results:
                    total_sum += Decimal(str(result))
            
            # Финальное вычисление π
            C = Decimal(426880) * Decimal(10005).sqrt()
            pi = C / total_sum
            
            # Преобразуем в строку
            pi_str = str(pi)[2:][:digits]
            
            elapsed = time.time() - start_time
            print(f"OpenCL вычисление завершено за {elapsed:.2f} сек")
            
            if progress_callback:
                progress_callback(100, num_batches, num_batches)
            
            return pi_str
            
        except Exception as e:
            print(f"OpenCL ошибка вычисления: {e}")
            raise

class NumpyOptimizedChudnovsky:
    """Оптимизированная NumPy реализация Chudnovsky"""
    
    def get_algorithm_name(self) -> str:
        return "Chudnovsky (NumPy Optimized)"
    
    def compute_pi(self, digits: int, progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Вычисляет π используя NumPy векторизацию
        """
        precision = digits + 100
        getcontext().prec = precision
        
        print(f"NumPy вычисление {digits:,} цифр π...")
        start_time = time.time()
        
        # Вычисляем количество итераций
        max_iterations = digits // 14 + 1
        
        # Используем NumPy для векторизованных вычислений
        k_values = np.arange(1, max_iterations, dtype=np.int64)
        
        # Векторизованные вычисления
        k_cubed = k_values ** 3
        k_values_decimal = [Decimal(k) for k in k_values]
        
        # Инициализация
        M = Decimal(1)
        L = Decimal(13591409)
        X = Decimal(1)
        K = 6
        S = Decimal(L) / Decimal(X)
        
        # Основной цикл с NumPy оптимизациями
        for i, k in enumerate(k_values):
            if progress_callback and i % 1000 == 0:
                progress = (i / len(k_values)) * 100
                progress_callback(progress, i, len(k_values))
            
            # Используем предвычисленные значения
            i_cubed = int(k_cubed[i])
            
            M = M * (K**3 - 16*K) // i_cubed
            L += Decimal(545140134)
            X *= Decimal(-262537412640768000)
            
            term = M * L / X
            S += term
            K += 12
        
        # Финальное вычисление π
        C = Decimal(426880) * Decimal(10005).sqrt()
        pi = C / S
        
        # Преобразуем в строку
        pi_str = str(pi)[2:][:digits]
        
        elapsed = time.time() - start_time
        print(f"NumPy вычисление завершено за {elapsed:.2f} сек")
        
        if progress_callback:
            progress_callback(100, len(k_values), len(k_values))
        
        return pi_str

class CudaChudnovsky(BaseGPUGenerator):
    """CUDA реализация Chudnovsky алгоритма"""
    
    def get_algorithm_name(self) -> str:
        return "Chudnovsky (CUDA GPU)"
    
    def initialize(self) -> bool:
        """Инициализирует CUDA"""
        try:
            import cupy as cp
            
            # Проверяем доступность CUDA
            if not cp.cuda.is_available():
                print("CUDA: устройства не найдены")
                return False
            
            self.device = cp.cuda.Device(self.device_id)
            print(f"CUDA инициализирован: {self.device.name.decode()}")
            self.is_initialized = True
            return True
            
        except ImportError:
            print("CUDA: cupy не установлен")
            return False
        except Exception as e:
            print(f"CUDA ошибка инициализации: {e}")
            return False
    
    def cleanup(self):
        """Освобождает ресурсы CUDA"""
        if hasattr(self, 'device'):
            cp.cuda.Device(0).synchronize()
        self.is_initialized = False
    
    def compute_pi(self, digits: int, progress_callback: Optional[Callable] = None, **kwargs) -> str:
        """
        Вычисляет π используя CUDA
        """
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("Не удалось инициализировать CUDA")
        
        try:
            import cupy as cp
            
            precision = digits + 100
            getcontext().prec = precision
            
            print(f"CUDA вычисление {digits:,} цифр π...")
            start_time = time.time()
            
            # Вычисляем количество итераций
            max_iterations = digits // 14 + 1
            
            # CUDA ядро для Chudnovsky
            chudnovsky_kernel = cp.RawKernel(r'''
            extern "C" __global__
            void chudnovsky_terms(double* results, int start_k, int max_iterations) {
                int tid = blockIdx.x * blockDim.x + threadIdx.x;
                int k = start_k + tid;
                
                if (k >= max_iterations) return;
                
                // Упрощенные вычисления для CUDA
                double k_d = (double)k;
                double term = 13591409.0 + 545140134.0 * k_d;
                double denominator = pow(640320.0, 3.0 * k_d);
                
                results[tid] = term / denominator;
            }
            ''', 'chudnovsky_terms')
            
            # Разделяем на батчи
            batch_size = min(1024, max_iterations)
            num_batches = (max_iterations + batch_size - 1) // batch_size
            
            total_sum = Decimal(0)
            
            for batch in range(num_batches):
                start_k = batch * batch_size
                count_k = min(batch_size, max_iterations - start_k)
                
                if progress_callback:
                    progress = (batch / num_batches) * 100
                    progress_callback(progress, batch, num_batches)
                
                # Выделяем память на GPU
                results_gpu = cp.zeros(count_k, dtype=cp.float64)
                
                # Запускаем ядро
                threads_per_block = 256
                blocks_per_grid = (count_k + threads_per_block - 1) // threads_per_block
                
                chudnovsky_kernel((blocks_per_grid,), (threads_per_block,), 
                                (results_gpu, start_k, max_iterations))
                
                # Копируем результаты обратно
                results_cpu = cp.asnumpy(results_gpu)
                
                # Суммируем результаты
                for result in results_cpu:
                    total_sum += Decimal(str(result))
            
            # Финальное вычисление π
            C = Decimal(426880) * Decimal(10005).sqrt()
            pi = C / total_sum
            
            # Преобразуем в строку
            pi_str = str(pi)[2:][:digits]
            
            elapsed = time.time() - start_time
            print(f"CUDA вычисление завершено за {elapsed:.2f} сек")
            
            if progress_callback:
                progress_callback(100, num_batches, num_batches)
            
            return pi_str
            
        except Exception as e:
            print(f"CUDA ошибка вычисления: {e}")
            raise

def test_gpu_algorithms():
    """Тест GPU алгоритмов"""
    
    algorithms = [
        NumpyOptimizedChudnovsky(),
        OpenCLChudnovsky(),
        CudaChudnovsky()
    ]
    
    precision = 1000
    
    print("🧪 Тест GPU алгоритмов:")
    
    for algo in algorithms:
        print(f"\n📊 {algo.get_algorithm_name()}:")
        
        start = time.time()
        try:
            pi_digits = algo.compute_pi(precision)
            elapsed = time.time() - start
            
            print(f"   Время: {elapsed:.3f} сек")
            print(f"   Первые 20 цифр: {pi_digits[:20]}")
            
            # Проверяем правильность
            known_pi = "14159265358979323846"
            if pi_digits.startswith(known_pi):
                print("   ✅ Правильно")
            else:
                print("   ❌ Неправильно")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        finally:
            # Очищаем ресурсы
            if hasattr(algo, 'cleanup'):
                algo.cleanup()

if __name__ == "__main__":
    test_gpu_algorithms()
