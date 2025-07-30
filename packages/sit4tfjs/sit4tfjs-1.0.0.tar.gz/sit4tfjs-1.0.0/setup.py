#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="sit4tfjs",
    version="1.0.0",
    description="Simple Inference Test for TensorFlow.js. A benchmark inference speed testing tool for TensorFlow.js models.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Katsuya Hyodo",
    author_email="rmsdh122@yahoo.co.jp",
    url="https://github.com/PINTO0309/sit4tfjs",
    license="MIT License",
    packages=find_packages(),
    platforms=["linux", "unix", "windows", "macos"],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.19.0",
        "tensorflowjs>=4.0.0",
        "rich>=10.0.0",
        "psutil>=5.8.0",
    ],
    extras_require={
        "tensorflow": [
            "tensorflow>=2.10.0",
        ],
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "sit4tfjs=sit4tfjs.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "tensorflow",
        "tensorflowjs",
        "tfjs",
        "benchmark",
        "inference",
        "performance",
        "testing",
        "deep learning",
        "machine learning",
        "neural network",
    ],
)