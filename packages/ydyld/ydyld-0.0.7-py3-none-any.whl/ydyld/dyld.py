import ctypes
from ctypes import (Structure, c_char_p, c_int, c_longlong, c_uint8, c_uint16,
                    c_uint32, c_uint64, c_void_p)

# --- Load dyld API ---
libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib")

libc._dyld_image_count.restype = c_uint32
libc._dyld_get_image_name.argtypes = [c_uint32]
libc._dyld_get_image_name.restype = c_char_p
libc._dyld_get_image_header.argtypes = [c_uint32]
libc._dyld_get_image_header.restype = c_void_p
libc._dyld_get_image_vmaddr_slide.argtypes = [c_uint32]
libc._dyld_get_image_vmaddr_slide.restype = c_longlong

image_count = libc._dyld_image_count
get_image_name = libc._dyld_get_image_name
get_image_header = libc._dyld_get_image_header
get_image_vmaddr_slide = libc._dyld_get_image_vmaddr_slide


# --- Mach-O constants ---
LC_SEGMENT_64 = 0x19
LC_SYMTAB = 0x2
N_TYPE = 0x0E
N_SECT = 0x0E
N_UNDF = 0x0
N_ABS = 0x2
N_INDR = 0xA
N_EXT = 0x01
N_WEAK_DEF = 0x0040
N_WEAK_REF = 0x0080
SEG_LINKEDIT = b"__LINKEDIT"


# --- Mach-O structures ---
class mach_header_64(Structure):
    _fields_ = [
        ("magic", c_uint32),
        ("cputype", c_int),
        ("cpusubtype", c_int),
        ("filetype", c_uint32),
        ("ncmds", c_uint32),
        ("sizeofcmds", c_uint32),
        ("flags", c_uint32),
        ("reserved", c_uint32),
    ]


class load_command(Structure):
    _fields_ = [("cmd", c_uint32), ("cmdsize", c_uint32)]


class segment_command_64(Structure):
    _fields_ = [
        ("cmd", c_uint32),
        ("cmdsize", c_uint32),
        ("segname", ctypes.c_char * 16),
        ("vmaddr", c_uint64),
        ("vmsize", c_uint64),
        ("fileoff", c_uint64),
        ("filesize", c_uint64),
        ("maxprot", c_int),
        ("initprot", c_int),
        ("nsects", c_uint32),
        ("flags", c_uint32),
    ]


class symtab_command(Structure):
    _fields_ = [
        ("cmd", c_uint32),
        ("cmdsize", c_uint32),
        ("symoff", c_uint32),
        ("nsyms", c_uint32),
        ("stroff", c_uint32),
        ("strsize", c_uint32),
    ]


class nlist_64(Structure):
    _fields_ = [
        ("n_strx", c_uint32),
        ("n_type", c_uint8),
        ("n_sect", c_uint8),
        ("n_desc", c_uint16),
        ("n_value", c_uint64),
    ]


# --- Utility functions ---
def ylog(fmt, *args):
    print(fmt % args)


ydebug = yinfo = ycritical = ylog


def symbol_kind(sym):
    t = sym.n_type & N_TYPE
    if t == N_UNDF:
        return "undefined" if sym.n_value == 0 else "common (zero-filled)"
    if t == N_ABS:
        return "absolute"
    if t == N_SECT:
        return "defined"
    if t == N_INDR:
        return "indirect"
    return "unknown"


def symbol_binding(sym):
    return "external" if (sym.n_type & N_EXT) else "local"


def symbol_scope(sym):
    if sym.n_desc & N_WEAK_DEF:
        return "weak-def"
    if sym.n_desc & N_WEAK_REF:
        return "weak-ref"
    return "strong"
