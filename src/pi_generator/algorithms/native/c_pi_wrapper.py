"""
Python обертка для C++ генератора π
"""
import ctypes
import os
import threading
from pathlib import Path

class CPiGenerator:
    def __init__(self):
        # Загружаем C++ библиотеку
        lib_path = Path(__file__).parent / "cpu_chudnovsky.so"
        self.lib = ctypes.CDLL(str(lib_path))
        
        # Определяем сигнатуры функций
        self.lib.generate_pi_digits.restype = ctypes.c_char_p
        self.lib.generate_pi_digits.argtypes = [ctypes.c_int, ctypes.c_int]
        
        self.lib.get_last_error.restype = ctypes.c_char_p
        self.lib.get_last_error.argtypes = []
    
    def generate_pi_digits(self, digits: int, num_workers: int = 1) -> str:
        """Генерирует цифры π используя C++ код"""
        try:
            result = self.lib.generate_pi_digits(digits, num_workers)
            if result:
                return result.decode('utf-8')
            else:
                error = self.lib.get_last_error()
                if error:
                    raise RuntimeError(f"C++ error: {error.decode('utf-8')}")
                else:
                    raise RuntimeError("Unknown C++ error")
        except Exception as e:
            raise RuntimeError(f"Failed to generate π: {e}")

# Глобальный экземпляр
_c_generator = None
_generator_lock = threading.Lock()

def get_c_generator():
    """Получаем Singleton экземпляр C++ генератора"""
    global _c_generator
    if _c_generator is None:
        with _generator_lock:
            if _c_generator is None:
                _c_generator = CPiGenerator()
    return _c_generator
