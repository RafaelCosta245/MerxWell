import sys
import os
from cx_Freeze import setup, Executable

# Import apenas do flet_runtime (correto para as versões atuais)
import flet_runtime

flet_runtime_path = os.path.dirname(flet_runtime.__file__)

build_exe_options = {
    "packages": [
        "flet",
        "flet_runtime",
        "supabase",
        "dotenv",
        "requests",
        "docx",
        "docx2pdf",
        "pythoncom",
        "win32com",
        "pywintypes",
    ],

    "includes": [
        "config",
        "screens",
        "scripts",
        "helpers",
    ],

    "include_files": [
        ("assets", "assets"),
        (".env", ".env"),
        (flet_runtime_path, "flet_runtime"),
    ],

    "zip_include_packages": ["*"],
    "zip_exclude_packages": [],

    "excludes": [
        "tkinter",
        "unittest",
        "pydoc",
    ],

    "optimize": 2,
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="MerxWell",
    version="1.0",
    description="MerxWell - Sistema de Gestão",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="MerxWell.exe",
            icon="assets/icons/LogoMerx256.ico",
        )
    ],
)
