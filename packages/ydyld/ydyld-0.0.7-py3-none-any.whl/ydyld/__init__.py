import platform
import sys

if platform.system() != "Darwin":
    raise RuntimeError("ydyld only works on macOS")
