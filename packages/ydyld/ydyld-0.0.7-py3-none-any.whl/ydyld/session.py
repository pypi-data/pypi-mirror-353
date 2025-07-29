""" Abstraction of a dyld details of a process as all the operations are happenning on the libraries loaded in the process."""

import ctypes
from functools import cached_property

from . import dyld


class YdyldSymbol:
    """Represents a higher-level wrapper for a symbol in a dyld image."""

    def __init__(self, sym, string_table):
        self._sym = sym
        self._string_table = string_table

    @cached_property
    def name(self):
        raw = ctypes.c_char_p(self._string_table + self._sym.n_strx).value
        return raw.decode(errors="replace") if raw else ""

    @cached_property
    def kind(self):
        return dyld.symbol_kind(self._sym)

    @cached_property
    def binding(self):
        return dyld.symbol_binding(self._sym)

    @cached_property
    def scope(self):
        return dyld.symbol_scope(self._sym)

    def __repr__(self):
        return f"<Symbol {self.name} ({self.kind}:{self.binding})>"

    @cached_property
    def address(self):
        """Return the address of the symbol."""
        return self._sym.n_value


class YdyldImage:
    """Represents a loaded image in the dyld session."""

    def __init__(self, index):
        self._index = index

    @property
    def index(self):
        return self._index

    @cached_property
    def name(self):
        return dyld.get_image_name(self._index)

    @cached_property
    def header(self):
        return dyld.mach_header_64.from_address(dyld.get_image_header(self._index))

    @cached_property
    def vmaddr_slide(self):
        return dyld.get_image_vmaddr_slide(self._index)

    @cached_property
    def symtab_and_linkedit(self):
        """Return (symtab, linkedit_base, fileoff_linkedit) from load commands."""
        base_addr = dyld.get_image_header(self._index)
        cmd_addr = base_addr + ctypes.sizeof(dyld.mach_header_64)
        symtab = None
        seg_linkedit = None

        for _ in range(self.header.ncmds):
            cmd = dyld.load_command.from_address(cmd_addr)
            if cmd.cmd == dyld.LC_SYMTAB:
                symtab = dyld.symtab_command.from_address(cmd_addr)
            elif cmd.cmd == dyld.LC_SEGMENT_64:
                seg = dyld.segment_command_64.from_address(cmd_addr)
                if seg.segname.rstrip(b"\x00") == dyld.SEG_LINKEDIT:
                    seg_linkedit = seg
            cmd_addr += cmd.cmdsize

        if not symtab or not seg_linkedit:
            raise RuntimeError("Required commands not found")

        fileoff_linkedit = seg_linkedit.fileoff
        linkedit_base = self.vmaddr_slide + seg_linkedit.vmaddr

        return symtab, linkedit_base, fileoff_linkedit

    def symbols(self):
        """Yield Symbol objects from this image."""
        symtab, linkedit_base, fileoff_linkedit = self.symtab_and_linkedit

        symbol_table_ptr = linkedit_base + (symtab.symoff - fileoff_linkedit)
        string_table_ptr = linkedit_base + (symtab.stroff - fileoff_linkedit)

        for i in range(symtab.nsyms):
            sym = dyld.nlist_64.from_address(
                symbol_table_ptr + i * ctypes.sizeof(dyld.nlist_64)
            )
            if (
                (sym.n_type & dyld.N_TYPE) == dyld.N_SECT
                and sym.n_sect == 1
                and sym.n_strx
            ):
                symbol_name = ctypes.c_char_p(string_table_ptr + sym.n_strx).value
                if not symbol_name:
                    continue
                yield YdyldSymbol(sym, string_table_ptr)


class YdyldSession:
    def __init__(self):
        self._self_loaded = {}
        pass

    def load_image(self, image_name):
        """load a shared library image into the process."""
        pass

    def get_images(self, all=False):
        """Yield all currently loaded images as DyldImage objects."""
        count = dyld.image_count()
        for i in range(count):
            yield YdyldImage(i)

    def load_image(self, path: str, flags=ctypes.RTLD_NOW):
        """Loads a dynamic library and returns its handle."""
        handle = ctypes.cdll.LoadLibrary(path)  # OR: ctypes.CDLL(path, mode=flags)
        return handle
