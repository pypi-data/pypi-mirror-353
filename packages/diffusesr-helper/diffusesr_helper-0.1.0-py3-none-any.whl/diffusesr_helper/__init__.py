import os
import ctypes

lib_path = os.path.join(os.path.dirname(__file__), "core.so")
lib = ctypes.CDLL(lib_path)

# Example: expose C function from .so
lib.generate.argtypes = [ctypes.c_int]
lib.generate.restype = ctypes.c_int

def generate(x: int) -> int:
    return lib.generate(x)
