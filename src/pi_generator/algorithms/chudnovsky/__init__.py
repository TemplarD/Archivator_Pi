"""
Алгоритмы Chudnovsky
"""

# Отложенный импорт для избежания circular import
def _import_single_thread():
    from .single_thread import BaseChudnovskySingleThread, ChudnovskySingleThread
    return BaseChudnovskySingleThread, ChudnovskySingleThread

def _import_multi_thread():
    from .multi_thread import (
        ChudnovskyBinarySplitting,
        ChudnovskyBlockParallel,
        BBPParallel,
        SimpleParallelChudnovsky
    )
    return ChudnovskyBinarySplitting, ChudnovskyBlockParallel, BBPParallel, SimpleParallelChudnovsky

def _import_gpu():
    from .gpu import (
        BaseChudnovskyGPU,
        NumpyOptimizedChudnovsky,
        OpenCLChudnovsky,
        CudaChudnovsky,
        GPUChudnovskyGenerator,
        AMDGPUChudnovskyGenerator
    )
    return (BaseChudnovskyGPU, NumpyOptimizedChudnovsky, OpenCLChudnovsky, 
            CudaChudnovsky, GPUChudnovskyGenerator, AMDGPUChudnovskyGenerator)

# Ленивые импорты
BaseChudnovskySingleThread = None
ChudnovskySingleThread = None
ChudnovskyBinarySplitting = None
ChudnovskyBlockParallel = None
BBPParallel = None
SimpleParallelChudnovsky = None
BaseChudnovskyGPU = None
NumpyOptimizedChudnovsky = None
OpenCLChudnovsky = None
CudaChudnovsky = None
GPUChudnovskyGenerator = None
AMDGPUChudnovskyGenerator = None

def _init_imports():
    """Инициализирует импорты при первом обращении"""
    global BaseChudnovskySingleThread, ChudnovskySingleThread
    global ChudnovskyBinarySplitting, ChudnovskyBlockParallel, BBPParallel, SimpleParallelChudnovsky
    global BaseChudnovskyGPU, NumpyOptimizedChudnovsky, OpenCLChudnovsky, CudaChudnovsky
    global GPUChudnovskyGenerator, AMDGPUChudnovskyGenerator
    
    if BaseChudnovskySingleThread is None:
        BaseChudnovskySingleThread, ChudnovskySingleThread = _import_single_thread()
    
    if ChudnovskyBinarySplitting is None:
        ChudnovskyBinarySplitting, ChudnovskyBlockParallel, BBPParallel, SimpleParallelChudnovsky = _import_multi_thread()
    
    if BaseChudnovskyGPU is None:
        (BaseChudnovskyGPU, NumpyOptimizedChudnovsky, OpenCLChudnovsky, 
         CudaChudnovsky, GPUChudnovskyGenerator, AMDGPUChudnovskyGenerator) = _import_gpu()

__all__ = [
    # Однопоточные
    'BaseChudnovskySingleThread',
    'ChudnovskySingleThread',
    
    # Многопоточные
    'ChudnovskyBinarySplitting',
    'ChudnovskyBlockParallel',
    'BBPParallel',
    'SimpleParallelChudnovsky',
    
    # GPU
    'BaseChudnovskyGPU',
    'NumpyOptimizedChudnovsky',
    'OpenCLChudnovsky',
    'CudaChudnovsky',
    'GPUChudnovskyGenerator',
    'AMDGPUChudnovskyGenerator'
]
