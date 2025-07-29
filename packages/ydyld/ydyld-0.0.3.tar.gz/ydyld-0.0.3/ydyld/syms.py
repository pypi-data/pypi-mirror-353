import ctypes

import ydyld


def symbol_kind(sym):
    t = sym.n_type & ydyld.N_TYPE
    if t == ydyld.N_UNDF:
        return "undefined" if sym.n_value == 0 else "common (zero-filled)"
    if t == ydyld.N_ABS:
        return "absolute"
    if t == ydyld.N_SECT:
        return "defined"
    if t == ydyld.N_INDR:
        return "indirect"
    return "unknown"


def symbol_binding(sym):
    return "external" if (sym.n_type & ydyld.N_EXT) else "local"


def symbol_scope(sym):
    if sym.n_desc & ydyld.N_WEAK_DEF:
        return "weak-def"
    if sym.n_desc & ydyld.N_WEAK_REF:
        return "weak-ref"
    return "strong"


# def process_symbols_from_image(_, __, image_index):
def process_symbols_from_image(image_index):
    image_name = ydyld.get_image_name(image_index)
    print(image_name)
    if not image_name:
        ydyld.ycritical("image_name is null")
        return
    ydyld.ydebug("Processing image: %d, %s", image_index, image_name.decode())

    header_ptr = ydyld.get_image_header(image_index)
    if not header_ptr:
        ydyld.ycritical("header is null")
        return

    header = ydyld.mach_header_64.from_address(header_ptr)
    ydyld.ydebug(
        "header: magic %x, filetype: %d, ncmds: %d, sizeofcmds: %d, flags: %d",
        header.magic,
        header.filetype,
        header.ncmds,
        header.sizeofcmds,
        header.flags,
    )

    base = header_ptr
    slide = ydyld.get_image_vmaddr_slide(image_index)

    cmd_addr = base + ctypes.sizeof(ydyld.mach_header_64)

    symtab = None
    seg_linkedit = None

    for _ in range(header.ncmds):
        cmd = ydyld.load_command.from_address(cmd_addr)
        if cmd.cmd == ydyld.LC_SYMTAB:
            symtab = ydyld.symtab_command.from_address(cmd_addr)
        elif cmd.cmd == ydyld.LC_SEGMENT_64:
            seg = ydyld.segment_command_64.from_address(cmd_addr)
            if seg.segname.rstrip(b"\0") == ydyld.SEG_LINKEDIT:
                seg_linkedit = seg
        cmd_addr += cmd.cmdsize

    if not seg_linkedit:
        ydyld.ycritical("LC_SEGMENT_64 __LINKEDIT not found!")
        return

    fileoff_linkedit = seg_linkedit.fileoff
    linkedit_base = slide + seg_linkedit.vmaddr

    symbol_table_ptr = linkedit_base + (symtab.symoff - fileoff_linkedit)
    string_table_ptr = linkedit_base + (symtab.stroff - fileoff_linkedit)

    ydyld.ydebug("symtab seems to be ok")
    ydyld.ydebug(
        "symtab: cmd: %d, symoff: %d, stroff: %d, nsyms: %d, strsize: %d",
        symtab.cmd,
        symtab.symoff,
        symtab.stroff,
        symtab.nsyms,
        symtab.strsize,
    )

    for i in range(symtab.nsyms):
        sym = ydyld.nlist_64.from_address(
            symbol_table_ptr + i * ctypes.sizeof(ydyld.nlist_64)
        )
        if (
            (sym.n_type & ydyld.N_TYPE) == ydyld.N_SECT
            and sym.n_sect == 1
            and sym.n_strx
        ):
            symbol_name = ctypes.c_char_p(string_table_ptr + sym.n_strx).value
            if not symbol_name:
                continue
            kind = symbol_kind(sym)
            binding = symbol_binding(sym)
            print(
                "found symbol  %s (%s:%s)"
                % (symbol_name.decode(errors="replace"), kind, binding)
            )
