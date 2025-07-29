
import ctypes

libcxxabi = ctypes.CDLL("/usr/lib/libc++abi.dylib")

__cxa_demangle = libcxxabi.__cxa_demangle
__cxa_demangle.argtypes = [
    ctypes.c_char_p,         # const char* mangled_name
    ctypes.c_void_p,         # char* output_buffer
    ctypes.POINTER(ctypes.c_size_t),  # size_t* length
    ctypes.POINTER(ctypes.c_int)      # int* status
]
__cxa_demangle.restype = ctypes.c_char_p


def demangle(mangled: str) -> str | None:
    if not mangled:
        return None

    status = ctypes.c_int(0)
    length = ctypes.c_size_t(0)

    demangled = __cxa_demangle(
        mangled.encode('utf-8'),
        None,
        ctypes.byref(length),
        ctypes.byref(status)
    )

    if status.value == 0 and demangled:
        return ctypes.cast(demangled, ctypes.c_char_p).value.decode("utf-8")
    return None
