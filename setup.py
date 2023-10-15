import sys
from cx_Freeze import setup, Executable

from data import values

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "excludes": [],
    "zip_include_packages": [],
    "packages": [
      "ttkbootstrap"
    ],
    "include_files": [
        "resources"
    ]
}

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name=values.SHORT,
    version=values.VERSION,
    description=values.NAME,
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, target_name=values.SHORT)],
)