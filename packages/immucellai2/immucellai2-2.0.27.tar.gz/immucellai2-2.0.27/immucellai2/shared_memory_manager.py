import numpy as np
import multiprocessing as mp
import ctypes

class SharedMemoryManager:
    def __init__(self, shape, dtype=np.float32):
        self.shape = shape
        self.dtype = dtype
        # 将 dtype 转换为 ctypes 类型
        typecode = self._get_typecode(dtype)
        # 计算总大小
        size = int(np.prod(shape))
        # 创建共享内存数组
        self.shared_array_base = mp.RawArray(typecode, size)
        self.shared_array = np.frombuffer(self.shared_array_base, dtype=dtype).reshape(shape)
    def get_shared_array(self):
        return self.shared_array
    def _get_typecode(self, dtype):
        # 将 NumPy dtype 转换为 ctypes 类型
        if dtype == np.float32:
            return ctypes.c_float
        elif dtype == np.float64:
            return ctypes.c_double
        elif dtype == np.int32:
            return ctypes.c_int
        elif dtype == np.int64:
            return ctypes.c_long
        else:
            raise ValueError(f"Unsupported dtype: {dtype}")


