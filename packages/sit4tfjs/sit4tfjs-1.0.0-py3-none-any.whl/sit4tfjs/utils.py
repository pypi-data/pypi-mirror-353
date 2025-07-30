"""
Utility functions for TensorFlow.js benchmarking.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

import numpy as np


def get_model_info(model_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load model information from model.json.

    Args:
        model_path: Path to the TensorFlow.js model directory

    Returns:
        Model information dictionary
    """
    model_path = Path(model_path)
    model_json_path = model_path / "model.json"

    if not model_json_path.exists():
        raise FileNotFoundError(f"Model JSON not found: {model_json_path}")

    with open(model_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_shape(shape: List[int]) -> str:
    """
    Format tensor shape for display.

    Args:
        shape: Tensor shape

    Returns:
        Formatted shape string
    """
    return f"[{', '.join(map(str, shape))}]"


def parse_shape_string(shape_str: str) -> List[int]:
    """
    Parse shape string into list of integers.

    Args:
        shape_str: Shape string like "1,112,200,64"

    Returns:
        List of shape dimensions
    """
    try:
        return [int(x.strip()) for x in shape_str.split(",")]
    except ValueError as e:
        raise ValueError(f"Invalid shape string '{shape_str}': {e}")


def parse_fixed_shapes(fixed_shapes_str: str) -> Dict[str, List[int]]:
    """
    Parse fixed shapes string into dictionary.

    Args:
        fixed_shapes_str: Fixed shapes string like "input1:1,224,224,3 input2:1,100"

    Returns:
        Dictionary mapping input names to shapes
    """
    if not fixed_shapes_str.strip():
        return {}

    fixed_shapes = {}
    for shape_spec in fixed_shapes_str.split():
        if ":" not in shape_spec:
            raise ValueError(f"Invalid shape specification: {shape_spec}")

        input_name, shape_str = shape_spec.split(":", 1)
        fixed_shapes[input_name] = parse_shape_string(shape_str)

    return fixed_shapes


def parse_numpy_files(numpy_files_str: str) -> Dict[str, str]:
    """
    Parse numpy files string into dictionary.

    Args:
        numpy_files_str: Numpy files string like "input1:data1.npy input2:data2.npy"

    Returns:
        Dictionary mapping input names to file paths
    """
    if not numpy_files_str.strip():
        return {}

    numpy_files = {}
    for file_spec in numpy_files_str.split():
        if ":" not in file_spec:
            raise ValueError(f"Invalid numpy file specification: {file_spec}")

        input_name, file_path = file_spec.split(":", 1)
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Numpy file not found: {file_path}")

        numpy_files[input_name] = file_path

    return numpy_files


def generate_random_inputs(input_specs: Dict[str, Dict[str, Any]]) -> Dict[str, np.ndarray]:
    """
    Generate random inputs based on input specifications.

    Args:
        input_specs: Input specifications

    Returns:
        Dictionary of random input tensors
    """
    inputs = {}
    for input_name, spec in input_specs.items():
        dtype = np.float32 if spec["dtype"] == "DT_FLOAT" else np.int32
        inputs[input_name] = np.random.randn(*spec["shape"]).astype(dtype)
    return inputs


def load_numpy_inputs(
    input_specs: Dict[str, Dict[str, Any]],
    numpy_file_paths: Dict[str, str]
) -> Dict[str, np.ndarray]:
    """
    Load inputs from numpy files.

    Args:
        input_specs: Input specifications
        numpy_file_paths: Paths to numpy files for each input

    Returns:
        Dictionary of loaded input tensors
    """
    inputs = {}
    for input_name, spec in input_specs.items():
        if input_name in numpy_file_paths:
            # Load from file
            data = np.load(numpy_file_paths[input_name])
            
            # Validate shape compatibility
            expected_shape = spec["shape"]
            if data.shape != tuple(expected_shape):
                print(f"Warning: Shape mismatch for {input_name}")
                print(f"  Expected: {format_shape(expected_shape)}")
                print(f"  Got:      {format_shape(list(data.shape))}")
                print(f"  Attempting to reshape...")
                
                try:
                    data = data.reshape(expected_shape)
                except ValueError:
                    print(f"  Reshape failed. Using original shape.")
            
            inputs[input_name] = data
        else:
            # Generate random data
            dtype = np.float32 if spec["dtype"] == "DT_FLOAT" else np.int32
            inputs[input_name] = np.random.randn(*spec["shape"]).astype(dtype)
    
    return inputs


def print_model_summary(model_info: Dict[str, Any]) -> None:
    """
    Print model summary information.

    Args:
        model_info: Model information from model.json
    """
    print("Model Information:")
    print(f"  Format: {model_info.get('format', 'unknown')}")
    print(f"  Generated by: {model_info.get('generatedBy', 'unknown')}")
    print(f"  Converted by: {model_info.get('convertedBy', 'unknown')}")

    if "signature" in model_info:
        signature = model_info["signature"]
        
        if "inputs" in signature:
            print("  Inputs:")
            for input_name, input_info in signature["inputs"].items():
                shape = []
                for dim in input_info["tensorShape"]["dim"]:
                    shape.append(dim.get("size", "?"))
                print(f"    {input_name}: {format_shape(shape)} ({input_info['dtype']})")
        
        if "outputs" in signature:
            print("  Outputs:")
            for output_name, output_info in signature["outputs"].items():
                shape = []
                for dim in output_info["tensorShape"]["dim"]:
                    shape.append(dim.get("size", "?"))
                print(f"    {output_name}: {format_shape(shape)} ({output_info['dtype']})")


def validate_model_path(model_path: Union[str, Path]) -> Path:
    """
    Validate and return model path.

    Args:
        model_path: Path to model directory

    Returns:
        Validated Path object

    Raises:
        FileNotFoundError: If model path or model.json doesn't exist
    """
    model_path = Path(model_path)
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model directory not found: {model_path}")
    
    if not model_path.is_dir():
        raise ValueError(f"Model path is not a directory: {model_path}")
    
    model_json_path = model_path / "model.json"
    if not model_json_path.exists():
        raise FileNotFoundError(f"model.json not found in: {model_path}")
    
    return model_path


def estimate_memory_usage(model_info: Dict[str, Any]) -> float:
    """
    Estimate model memory usage in MB.

    Args:
        model_info: Model information

    Returns:
        Estimated memory usage in MB
    """
    total_params = 0
    
    if "weightsManifest" in model_info:
        for manifest in model_info["weightsManifest"]:
            for weight in manifest.get("weights", []):
                shape = weight.get("shape", [])
                if shape:
                    total_params += np.prod(shape)
    
    # Assume float32 (4 bytes per parameter)
    memory_mb = total_params * 4 / 1024 / 1024
    return memory_mb


def check_dependencies() -> bool:
    """
    Check if core dependencies are available.

    Returns:
        True if core dependencies are available, False otherwise
    """
    try:
        import numpy
        import rich
        import psutil
        return True
    except ImportError as e:
        print(f"Missing core dependency: {e}")
        return False


def check_tensorflow_available() -> bool:
    """
    Check if TensorFlow is available for SavedModel conversion.

    Returns:
        True if TensorFlow is available, False otherwise
    """
    try:
        import tensorflow
        import tensorflowjs
        return True
    except ImportError:
        return False


def get_system_info() -> Dict[str, str]:
    """
    Get system information for debugging.

    Returns:
        System information dictionary
    """
    import platform
    
    try:
        import tensorflow as tf
        tf_version = tf.__version__
    except ImportError:
        tf_version = "Not installed"
    
    try:
        import tensorflowjs
        tfjs_version = tensorflowjs.__version__
    except ImportError:
        tfjs_version = "Not installed"
    
    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "tensorflow_version": tf_version,
        "tensorflowjs_version": tfjs_version,
    }