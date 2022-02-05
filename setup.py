# -*- coding: utf-8 -*-
import sys

from cx_Freeze import setup, Executable


if sys.platform == "win32":
    base = "Win32GUI"
else:
    base = None

executables = [Executable("main.py")]  # , base=base)]
exclude_packages = [
    "tkinter",
    "matplotlib",
    "matplotlib_inline",
    "email",
    "scipy",
    "multiprocessing",
    "asyncio",
    "html",
    "html5lib",
    "http",
    "jupyter_client",
    "jupyter_core",
    "jupyterlab_pygments",
    "logging",
    "pandas",
    "PyQt5",
    "simpy",
]
packages = [
    "functools",
    "operator",
    "os",
    "json",
    "random",
    "re",
    "datetime",
    "PIL",
]
options = {
    'build_exe': {
        'packages': packages,
        'include_files': ["./config.json"],
        "excludes": exclude_packages,
    },
}

setup(
    name="NFT Generator",
    options=options,
    version="1.0",
    description="",
    executables=executables
)
