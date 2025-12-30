#!/usr/bin/env python3
"""
GPU генератор числа π с использованием OpenCL
Оптимизирован для AMD Fury X
"""

import numpy as np
import time
from pathlib import Path
from typing import Optional, Tuple

try:
    import pyopencl as cl
    OPENCL_AVAILABLE = True
except ImportError:
    OPENCL_AVAILABLE = False
    print("OpenCL недоступен. Установите pyopencl для GPU ускорения.")

class GPUChudnovskyGenerator:
    """GPU генератор π по алгоритму Chudnovsky"""
    
    def __init__(self):
        self.ctx = None
        self.queue = None
        self.program = None
        self.device_info = None
        
        if OPENCL_AVAILABLE:
            self._initialize_opencl()
    
    def _initialize_opencl(self):
        """Инициализация OpenCL"""
        try:
            # Выбираем платформу и устройство
            platforms = cl.get_platforms()
            
            # Ищем AMD платформу для Fury X
            amd_platform = None
            for platform in platforms:
                if "AMD" in platform.name or "Advanced Micro Devices" in platform.name:
                    amd_platform = platform
                    break
            
            if not amd_platform:
                # Используем первую доступную платформу
                amd_platform = platforms[0]
            
            # Выбираем устройство (GPU)
            devices = amd_platform.get_devices()
            gpu_device = None
            
            for device in devices:
                if device.type == cl.device_type.GPU:
                    gpu_device = device
                    break
            
            if not gpu_device:
                gpu_device = devices[0]  # Используем первое устройство
            
            # Создаем контекст и очередь
            self.ctx = cl.Context([gpu_device])
            self.queue = cl.CommandQueue(self.ctx)
            
            # Сохраняем информацию об устройстве
            self.device_info = {
                'name': gpu_device.name,
                'max_compute_units': gpu_device.max_compute_units,
                'global_mem_size': gpu_device.global_mem_size,
                'max_work_group_size': gpu_device.max_work_group_size
            }
            
            # Компилируем ядро
            kernel_source = self._load_kernel_source()
            self.program = cl.Program(self.ctx, kernel_source).build()
            
            print(f"OpenCL инициализирован: {gpu_device.name}")
            print(f"Вычислительных блоков: {gpu_device.max_compute_units}")
            print(f"Глобальная память: {gpu_device.global_mem_size / 1024**3:.1f} GB")
            
        except Exception as e:
            print(f"Ошибка инициализации OpenCL: {e}")
            self.ctx = None
    
    def _load_kernel_source(self) -> str:
        """Загружает исходный код ядра OpenCL"""
        kernel_path = Path(__file__).parent / "gpu_chudnovsky.cl"
        
        if kernel_path.exists():
            with open(kernel_path, 'r') as f:
                return f.read()
        else:
            # Встроенная версия если файл не найден
            return """
__kernel void chudnovsky_term(
    __global double* results,
    const int start_k,
    const int end_k,
    const double sqrt_10005,
    const double c
) {
    int gid = get_global_id(0);
    int k = start_k + gid;
    
    if (k >= end_k) return;
    
    double k_d = (double)k;
    double term = pow(-1.0, k_d) * factorial(6*k) * (13591409.0 + 545140134.0 * k_d) /
                  (factorial(3*k) * pow(factorial(k), 3) * pow(640320.0, 3.0*k_d + 1.5));
    
    results[gid] = term;
}
"""
    
    def generate_pi_digits_gpu(self, digits: int) -> str:
        """
        Генерирует цифры π с использованием GPU
        
        Args:
            digits: количество цифр для генерации
            
        Returns:
            строка с цифрами π
        """
        if not self.ctx or not self.program:
            raise RuntimeError("OpenCL не инициализирован")
        
        print(f"GPU генерация {digits} цифр π...")
        start_time = time.time()
        
        # Вычисляем количество членов ряда
        terms_needed = digits // 14 + 1
        
        # Константы Chudnovsky
        sqrt_10005 = np.sqrt(10005.0)
        c = 426880.0 * sqrt_10005
        
        # Создаем буферы
        results = np.zeros(terms_needed, dtype=np.float64)
        
        # GPU буферы
        results_buffer = cl.Buffer(self.ctx, cl.mem_flags.WRITE_ONLY, results.nbytes)
        
        # Запускаем ядро
        work_group_size = min(256, self.device_info['max_work_group_size'])
        global_size = ((terms_needed + work_group_size - 1) // work_group_size) * work_group_size
        
        kernel = self.program.chudnovsky_term
        kernel.set_args(
            results_buffer,
            np.int32(0),  # start_k
            np.int32(terms_needed),  # end_k
            np.float64(sqrt_10005),
            np.float64(c)
        )
        
        cl.enqueue_nd_range_kernel(
            self.queue,
            kernel,
            (global_size,),
            (work_group_size,)
        )
        
        # Копируем результаты
        cl.enqueue_copy(self.queue, results, results_buffer)
        self.queue.finish()
        
        # Суммируем члены ряда
        total_sum = np.sum(results)
        pi = c / total_sum
        
        # Преобразуем в строку
        pi_str = f"{pi:.{digits}f}"
        pi_str = pi_str.replace(".", "")[2:]  # Убираем "0."
        
        generation_time = time.time() - start_time
        
        print(f"GPU генерация завершена за {generation_time:.2f} сек")
        print(f"Скорость: {digits / generation_time:.0f} цифр/сек")
        
        return pi_str[:digits]
    
    def parallel_search_gpu(self, pattern: str, pi_digits: str) -> Tuple[bool, int]:
        """
        Параллельный поиск паттерна в π с использованием GPU
        
        Args:
            pattern: паттерн для поиска (hex строка)
            pi_digits: цифры π
            
        Returns:
            (найдено, позиция)
        """
        if not self.ctx or not self.program:
            raise RuntimeError("OpenCL не инициализирован")
        
        pattern_bytes = pattern.encode('ascii')
        pi_bytes = pi_digits.encode('ascii')
        
        # Создаем буферы
        pattern_buffer = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=pattern_bytes)
        pi_buffer = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=pi_bytes)
        
        results = np.full(len(pi_bytes) - len(pattern_bytes) + 1, -1, dtype=np.int32)
        results_buffer = cl.Buffer(self.ctx, cl.mem_flags.WRITE_ONLY, results.nbytes)
        
        # Запускаем ядро поиска
        kernel = self.program.parallel_search
        kernel.set_args(
            pi_buffer,
            np.int32(len(pi_bytes)),
            pattern_buffer,
            np.int32(len(pattern_bytes)),
            results_buffer
        )
        
        work_group_size = 64
        global_size = ((len(results) + work_group_size - 1) // work_group_size) * work_group_size
        
        cl.enqueue_nd_range_kernel(
            self.queue,
            kernel,
            (global_size,),
            (work_group_size,)
        )
        
        # Копируем результаты
        cl.enqueue_copy(self.queue, results, results_buffer)
        self.queue.finish()
        
        # Ищем первое совпадение
        for i, pos in enumerate(results):
            if pos >= 0:
                return True, pos
        
        return False, -1
    
    def xor_decorrelate_gpu(self, data: bytes, pi_sequence: bytes, xor_key: int) -> bytes:
        """
        GPU XOR-декорреляция данных
        
        Args:
            data: исходные данные
            pi_sequence: последовательность π
            xor_key: XOR ключ
            
        Returns:
            декоррелированные данные
        """
        if not self.ctx or not self.program:
            raise RuntimeError("OpenCL не инициализирован")
        
        data_array = np.frombuffer(data, dtype=np.uint8)
        pi_array = np.frombuffer(pi_sequence[:len(data)], dtype=np.uint8)
        
        # Создаем буферы
        data_buffer = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=data_array)
        pi_buffer = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=pi_array)
        
        results = np.zeros(len(data_array), dtype=np.uint8)
        results_buffer = cl.Buffer(self.ctx, cl.mem_flags.WRITE_ONLY, results.nbytes)
        
        # Запускаем ядро
        kernel = self.program.xor_decorrelate
        kernel.set_args(
            data_buffer,
            pi_buffer,
            results_buffer,
            np.int32(len(data_array)),
            np.uint8(xor_key)
        )
        
        work_group_size = 256
        global_size = ((len(data_array) + work_group_size - 1) // work_group_size) * work_group_size
        
        cl.enqueue_nd_range_kernel(
            self.queue,
            kernel,
            (global_size,),
            (work_group_size,)
        )
        
        # Копируем результаты
        cl.enqueue_copy(self.queue, results, results_buffer)
        self.queue.finish()
        
        return results.tobytes()
    
    def get_device_info(self) -> dict:
        """Возвращает информацию об устройстве"""
        if self.device_info:
            return self.device_info
        else:
            return {'error': 'OpenCL не инициализирован'}
    
    def benchmark_performance(self, test_digits: int = 100000) -> dict:
        """
        Тест производительности GPU
        
        Args:
            test_digits: количество цифр для теста
            
        Returns:
            результаты бенчмарка
        """
        if not self.ctx:
            return {'error': 'OpenCL не инициализирован'}
        
        print(f"GPU бенчмарк: {test_digits} цифр π")
        
        # Тест генерации
        start_time = time.time()
        try:
            pi_digits = self.generate_pi_digits_gpu(test_digits)
            generation_time = time.time() - start_time
            
            return {
                'digits_generated': test_digits,
                'generation_time': generation_time,
                'generation_speed': test_digits / generation_time,
                'device_info': self.device_info
            }
        except Exception as e:
            return {'error': str(e)}


if __name__ == "__main__":
    # Тестирование GPU генератора
    if OPENCL_AVAILABLE:
        gpu_gen = GPUChudnovskyGenerator()
        
        if gpu_gen.ctx:
            # Тест генерации
            try:
                pi_digits = gpu_gen.generate_pi_digits_gpu(10000)
                print(f"Сгенерировано {len(pi_digits)} цифр π")
                print(f"Первые 50 цифр: {pi_digits[:50]}")
                
                # Бенчмарк
                benchmark = gpu_gen.benchmark_performance(50000)
                print(f"Бенчмарк: {benchmark}")
                
            except Exception as e:
                print(f"Ошибка тестирования: {e}")
        else:
            print("Не удалось инициализировать OpenCL")
    else:
        print("OpenCL недоступен")
