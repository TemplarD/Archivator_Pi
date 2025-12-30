"""
GPU алгоритмы Chudnovsky
"""

from .chudnovsky_numpy_optimized import (
    BaseChudnovskyGPU,
    NumpyOptimizedChudnovsky
)

# Ленивые импорты для GPU алгоритмов (могут требовать дополнительные зависимости)
OpenCLChudnovsky = None
CudaChudnovsky = None
GPUChudnovskyGenerator = None
AMDGPUChudnovskyGenerator = None

def _import_gpu_algorithms():
    """Импортирует GPU алгоритмы при наличии зависимостей"""
    global OpenCLChudnovsky, CudaChudnovsky, GPUChudnovskyGenerator, AMDGPUChudnovskyGenerator
    
    try:
        from .opencl_chudnovsky import OpenCLChudnovsky
    except ImportError:
        pass
    
    try:
        from .cuda_chudnovsky import CudaChudnovsky
    except ImportError:
        pass
    
    try:
        from .gpu_chudnovsky import GPUChudnovskyGenerator
    except ImportError:
        pass
    
    try:
        from .gpu_pi_generator_amd import GPUChudnovskyGenerator as AMDGPUChudnovskyGenerator
    except ImportError:
        pass

__all__ = [
    'BaseChudnovskyGPU',
    'NumpyOptimizedChudnovsky',
    'OpenCLChudnovsky',
    'CudaChudnovsky',
    'GPUChudnovskyGenerator',
    'AMDGPUChudnovskyGenerator',
    '_import_gpu_algorithms'
]
