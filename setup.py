import sys
from cx_Freeze import setup, Executable

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
    name="abc",
    version="0.9.1",
    description="Anno Building-menu Customizer",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, target_name="abc")],
)