# ydyld

**ydyld** is a Python toolkit for introspecting Mach-O binaries at runtime using `ctypes` and the macOS `dyld` APIs. It lets you list all loaded images (executables and libraries), inspect their Mach-O structure, and extract/demangle symbol information.

---

## Features

- 🔍 List all currently loaded Mach-O images in the process
- 🧩 Parse headers: `mach_header_64`, `load_command`, etc.
- 🧠 Read and classify symbol table entries (kind, binding, scope)
- 🧵 Support for C++ demangling via `__cxa_demangle`
- 🐍 Pure Python (`ctypes` only), no build or dependencies

---

## Usage

```bash
git clone https://github.com/zokrezyl/ydyld
cd ydyld
python3 syms.py
```

This will print information about symbols from all loaded binaries in the current Python process.

---

## Output Example

```
Processing image: 0, /usr/bin/python3
header: magic 0xfeedfacf, filetype: 2, ncmds: 18, ...
symtab: cmd: 2, symoff: 123456, ...
found symbol  _main (defined:external)
found symbol  __ZNSt3__112basic_stringIc... (defined:external)
```

---

## Modules

- `ydyld.py` – low-level bindings to `_dyld_*` APIs and Mach-O structs
- `syms.py` – logic to walk headers and symbol tables for introspection

---

## Notes

- Works only on **macOS**
- Inspects the Python process itself and any loaded `.dylib`s
- To add more images, use `ctypes.CDLL()` or `dlopen()`

---

## License

MIT © [zokrezyl](https://github.com/zokrezyl)
