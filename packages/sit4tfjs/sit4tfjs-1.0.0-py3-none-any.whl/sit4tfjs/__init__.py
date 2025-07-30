"""
sit4tfjs - Simple Inference Test for TensorFlow.js

A benchmark tool for testing inference speed of TensorFlow.js models.
"""

from .core import TFJSBenchmark
from .utils import (
    get_model_info,
    generate_random_inputs,
    load_numpy_inputs,
    format_shape,
)

__version__ = "1.0.0"
__author__ = "Katsuya Hyodo"
__email__ = "rmsdh122@yahoo.co.jp"
__license__ = "MIT"

__all__ = [
    "TFJSBenchmark",
    "get_model_info",
    "generate_random_inputs",
    "load_numpy_inputs",
    "format_shape",
]