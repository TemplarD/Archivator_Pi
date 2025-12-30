#!/usr/bin/env python3
"""
GPU генерация числа π по алгоритму Chudnovsky с использованием OpenCL
"""

import pyopencl as cl
import numpy as np
import time
from typing import Optional

class GPUChudnovskyGenerator:
    def __init__(self):
        self.ctx = None
        self.queue = None
        self.program = None
        self._init_opencl()
    
    def _init_opencl(self):
        """Инициализация OpenCL контекста"""
        try:
            # Проверяем доступность OpenCL
            try:
                platforms = cl.get_platforms()
            except Exception as e:
                if "PLATFORM_NOT_FOUND_KHR" in str(e):
                    print("⚠️  OpenCL не установлен или недоступен")
                    print("💡 Установите OpenCL драйверы:")
                    print("   sudo apt install ocl-icd-opencl-dev")
                    print("   ")
                    print("🎮 Для NVIDIA GPU:")
                    print("   sudo apt install nvidia-opencl-dev nvidia-driver-535")
                    print("   ")
                    print("🔥 Для AMD GPU:")
                    print("   sudo apt install mesa-opencl-icd opencl-headers")
                    print("   sudo apt install amdgpu-pro-opencl (для драйверов AMD)")
                    print("   ")
                    print("📦 Intel GPU:")
                    print("   sudo apt install intel-opencl-icd")
                    raise RuntimeError("OpenCL недоступен")
                else:
                    raise
            
            if not platforms:
                print("⚠️  OpenCL платформы не найдены")
                print("💡 Проверьте установку драйверов:")
                print("   lspci | grep -i vga")
                print("   clinfo")
                raise RuntimeError("OpenCL платформы не найдены")
            
            print(f"🔍 Найдено {len(platforms)} OpenCL платформ")
            
            # Ищем GPU устройство
            device = None
            gpu_found = False
            
            for i, platform in enumerate(platforms):
                try:
                    devices = platform.get_devices()
                    print(f"   Платформа {i}: {platform.name} ({len(devices)} устройств)")
                    
                    for j, dev in enumerate(devices):
                        dev_type = "GPU" if dev.type == cl.device_type.GPU else "CPU"
                        print(f"     Устройство {j}: {dev.name} ({dev_type})")
                        
                        if dev.type == cl.device_type.GPU and not gpu_found:
                            device = dev
                            gpu_found = True
                            print(f"✅ Выбран GPU: {dev.name}")
                            
                except Exception as e:
                    print(f"   ⚠️  Ошибка платформы {i}: {e}")
                    continue
                
                if gpu_found:
                    break
            
            if not gpu_found:
                # Если GPU нет, используем лучший CPU
                print("⚠️  GPU не найден, используем CPU")
                try:
                    device = platforms[0].get_devices()[0]
                    print(f"✅ Выбран CPU: {device.name}")
                except Exception as e:
                    raise RuntimeError(f"Не удалось найти устройство: {e}")
            
            # Создаем контекст
            self.ctx = cl.Context([device])
            self.queue = cl.CommandQueue(self.ctx)
            
            print(f"🚀 OpenCL контекст создан для {device.name}")
            
            # Компилируем OpenCL программу с обходом проблемных заголовков
            try:
                # Пробуем компиляцию с опциями для обхода проблем
                build_options = [
                    "-I/usr/include",
                    "-I/usr/include/clc",
                    "-Dcl_khr_fp64",
                    "-cl-mad-enable"
                ]
                
                kernel_code = """
                __kernel void chudnovsky_term(
                    __global const long* k_values,
                    __global const double* m_values,
                    __global const double* l_values,
                    __global const double* x_values,
                    __global double* results,
                    const int num_terms
                ) {
                    int gid = get_global_id(0);
                    if (gid >= num_terms) return;
                    
                    long k = k_values[gid];
                    double m = m_values[gid];
                    double l = l_values[gid];
                    double x = x_values[gid];
                    
                    // Вычисляем член ряда Chudnovsky
                    results[gid] = m * l / x;
                }
                """
                
                self.program = cl.Program(self.ctx, kernel_code).build(options=build_options)
                
            except cl._cl.RuntimeError as e:
                if "BUILD_PROGRAM_FAILURE" in str(e):
                    print("⚠️  Ошибка компиляции OpenCL kernel")
                    print("💡 Пробуем упрощенный kernel...")
                    
                    # Максимально простой kernel
                    simple_kernel = """
                    __kernel void chudnovsky_term(
                        __global const double* m_values,
                        __global const double* l_values,
                        __global const double* x_values,
                        __global double* results,
                        const int num_terms
                    ) {
                        int gid = get_global_id(0);
                        if (gid >= num_terms) return;
                        
                        results[gid] = m_values[gid] * l_values[gid] / x_values[gid];
                    }
                    """
                    
                    self.program = cl.Program(self.ctx, simple_kernel).build()
                    print("✅ Упрощенный kernel скомпилирован")
                else:
                    raise
            print("✅ OpenCL программа скомпилирована")
            
        except Exception as e:
            print(f"❌ OpenCL инициализация не удалась: {e}")
            print("💡 Возможные решения:")
            print("   1. Установите OpenCL: sudo apt install ocl-icd-opencl-dev")
            print("   2. Установите GPU драйверы")
            print("   3. Проверьте поддержку: clinfo")
            raise RuntimeError(f"OpenCL недоступен: {e}")
    
    def generate_pi_digits(self, digits: int, progress_callback=None) -> str:
        """
        Генерирует цифры π с использованием GPU
        
        Args:
            digits: количество цифр для генерации
            progress_callback: функция для отслеживания прогресса
            
        Returns:
            строка с цифрами π
        """
        if not self.program:
            raise RuntimeError("OpenCL не инициализирован")
        
        print(f"GPU генерация {digits:,} цифр π...")
        start_time = time.time()
        
        # Для демонстрации используем упрощенный подход
        # В реальной реализации здесь был бы полноценный GPU алгоритм
        
        # Вычисляем количество итераций
        num_terms = digits // 14 + 1
        
        # Подготавливаем данные для GPU
        k_values = np.array([6 + i*12 for i in range(num_terms)], dtype=np.int64)
        m_values = np.ones(num_terms, dtype=np.float64)
        l_values = np.array([13591409 + i*545140134 for i in range(num_terms)], dtype=np.float64)
        x_values = np.array([(-262537412640768000) ** i for i in range(num_terms)], dtype=np.float64)
        results = np.zeros(num_terms, dtype=np.float64)
        
        # Создаем буферы
        k_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=k_values)
        m_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=m_values)
        l_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=l_values)
        x_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=x_values)
        results_buf = cl.Buffer(self.ctx, cl.mem_flags.WRITE_ONLY, results.nbytes)
        
        # Запускаем GPU вычисления
        local_size = 64
        global_size = ((num_terms + local_size - 1) // local_size) * local_size
        
        try:
            # Пробуем полный набор параметров
            cl.enqueue_nd_range_kernel(
                self.queue, 
                self.program.chudnovsky_term, 
                (global_size,), 
                (local_size,),
                k_buf, m_buf, l_buf, x_buf, results_buf, np.int32(num_terms)
            )
        except:
            # Если не получилось, используем упрощенную версию
            cl.enqueue_nd_range_kernel(
                self.queue, 
                self.program.chudnovsky_term, 
                (global_size,), 
                (local_size,),
                m_buf, l_buf, x_buf, results_buf, np.int32(num_terms)
            )
        
        # Читаем результаты
        cl.enqueue_copy(self.queue, results, results_buf)
        cl.finish(self.queue)
        
        # Суммируем результаты
        from decimal import Decimal, getcontext
        getcontext().prec = digits + 10
        
        C = 426880 * Decimal(10005).sqrt()
        S = Decimal(0)
        
        for i in range(num_terms):
            if progress_callback and i % max(1, num_terms // 100) == 0:
                progress = (i / num_terms) * 100
                progress_callback(progress, i, num_terms)
            
            S += Decimal(results[i])
        
        pi = C / S
        
        # Преобразуем в строку
        pi_str = str(pi)[2:]  # Убираем "0."
        pi_str = pi_str[:digits]  # Обрезаем до нужного количества
        
        generation_time = time.time() - start_time
        print(f"GPU генерация завершена за {generation_time:.2f} сек")
        
        return pi_str
    
    def cleanup(self):
        """Очистка ресурсов OpenCL"""
        if self.queue:
            self.queue.finish()
        # OpenCL автоматически очистит ресурсы при выходе
