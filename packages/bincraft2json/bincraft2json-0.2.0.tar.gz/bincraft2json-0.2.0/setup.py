from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
from setuptools import setup, Extension
import os

# Define extension with pybind11
ext_modules = [
    Pybind11Extension(
        "bincraft2json._core",
        [
            "src/python_bindings.cpp",
        ],
        include_dirs=[
            # Path to pybind11 headers
            pybind11.get_include(),
            # Current directory for our header
            ".",
        ],
        libraries=["zstd"],
        cxx_std=17,
        define_macros=[("VERSION_INFO", '"0.2.0"')],
    ),
]

setup(
    name="bincraft2json",
    version="0.2.0",
    author="@aymene69",
    author_email="",
    description="Python module to decode BinCraft files to JSON",
    long_description="",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    packages=["bincraft2json"],
    package_dir={"bincraft2json": "src/bincraft2json"},
    python_requires=">=3.7",
    install_requires=[
        "pybind11>=2.6.0",
    ],
    extras_require={
        "dev": ["pytest", "build"],
    },
) 