# sit4tfjs

**Simple Inference Test for TensorFlow.js** - A benchmark tool for evaluating TensorFlow.js model performance

[![PyPI](https://img.shields.io/pypi/v/sit4tfjs.svg)](https://pypi.org/project/sit4tfjs/) [![Python](https://img.shields.io/pypi/pyversions/sit4tfjs.svg)](https://pypi.org/project/sit4tfjs/) [![License](https://img.shields.io/pypi/l/sit4tfjs.svg)](https://github.com/PINTO0309/sit4tfjs/blob/main/LICENSE) [![Downloads](https://img.shields.io/pypi/dm/sit4tfjs.svg)](https://pypi.org/project/sit4tfjs/)

## Overview

sit4tfjs is a comprehensive benchmarking tool designed specifically for TensorFlow.js models. It provides detailed performance analysis, supports multiple input models, dynamic tensor shapes, and offers extensive profiling capabilities for optimizing TensorFlow.js model deployment.

## Features

### Core Functionality
- **TensorFlow.js Model Support**: Native support for TensorFlow.js graph models (model.json + .bin files)
- **Performance Benchmarking**: Detailed inference time measurements with statistical analysis
- **Multi-Input Models**: Full support for models with multiple input tensors
- **Dynamic Shape Intelligence**: Automatic detection and handling of dynamic tensor dimensions
- **Memory Usage Estimation**: Built-in model size and memory footprint analysis

### Advanced Features
- **External Data Support**: Load real input data from numpy files for realistic benchmarking
- **Batch Processing**: Configurable batch sizes for throughput optimization
- **Profiling Mode**: Detailed model architecture and performance profiling
- **Shape Override**: Manual specification of input tensor shapes for dynamic models
- **Statistical Analysis**: Comprehensive timing statistics (min, max, average, standard deviation)

### Usability
- **Command-Line Interface**: Easy-to-use CLI with extensive options
- **Python API**: Programmatic access for integration into larger workflows
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Detailed Logging**: Comprehensive output for debugging and optimization

## Installation

### From PyPI (Recommended)
```bash
pip install sit4tfjs
```

### From Source
```bash
git clone https://github.com/PINTO0309/sit4tfjs.git
cd sit4tfjs
pip install -e .
```

### Dependencies

**Core Requirements:**
- Python >= 3.10
- TensorFlow.js >= 4.0.0
- NumPy >= 1.19.0
- Rich >= 10.0.0
- psutil >= 5.8.0

**Optional Dependencies:**
- TensorFlow >= 2.10.0 (for SavedModel conversion only)
- Node.js >= 16.0.0 (for Node.js runtime)
- @tensorflow/tfjs-node (for Node.js runtime)

**Note:** sit4tfjs supports multiple execution environments:
- **Browser CPU (default)**: Uses headless browser for TensorFlow.js execution
- **Browser WebGL/WebGPU/WASM**: GPU-accelerated browser-based inference
- **Node.js runtime**: Server-side TensorFlow.js execution (requires Node.js)
- **SavedModel support**: Automatic conversion (requires TensorFlow installation)
- **Fallback**: Mock inference for testing and analysis

## Quick Start

### Basic Usage

```bash
# Basic benchmark test (uses browser CPU by default)
sit4tfjs \
--input_tfjs_file_path ./model_optimized_fix_tfjs

# Custom batch size and iterations
sit4tfjs \
--input_tfjs_file_path ./model_optimized_fix_tfjs \
--batch_size 4 \
--test_loop_count 200

# Enable detailed profiling
sit4tfjs \
--input_tfjs_file_path ./model_optimized_fix_tfjs \
--enable_profiling

# Browser benchmarking with GPU acceleration
sit4tfjs \
--input_tfjs_file_path ./model_optimized_fix_tfjs \
--execution_provider webgl

sit4tfjs \
--input_tfjs_file_path ./model_optimized_fix_tfjs \
--execution_provider webgpu

# WebAssembly backend
sit4tfjs \
--input_tfjs_file_path ./model_optimized_fix_tfjs \
--execution_provider wasm

# Node.js runtime (requires Node.js + @tensorflow/tfjs-node)
sit4tfjs \
--input_tfjs_file_path ./model_optimized_fix_tfjs \
--execution_provider nodejs
```

### Advanced Usage

```bash
# Specify fixed input shapes (for dynamic models or multiple inputs)
sit4tfjs \
--input_tfjs_file_path ./model_multi_input_fix_tfjs \
--fixed_shapes "feat:1,112,200,64 pc_dep:1,112,200,3"

# Single input model with fixed shape
sit4tfjs \
--input_tfjs_file_path ./model_optimized_fix_tfjs \
--fixed_shapes "input:1,105,90"

# Use external numpy input files (multiple inputs)
sit4tfjs \
--input_tfjs_file_path ./model_multi_input_fix_tfjs \
--input_numpy_file_paths "feat:feat_data.npy pc_dep:depth_data.npy"

# Single input model with external data
sit4tfjs \
--input_tfjs_file_path ./model_optimized_fix_tfjs \
--input_numpy_file_paths "input:input_data.npy"

# Combined advanced options with multiple inputs
sit4tfjs \
--input_tfjs_file_path ./model_multi_input_fix_tfjs \
--batch_size 8 \
--test_loop_count 500 \
--fixed_shapes "feat:8,112,200,64 pc_dep:8,112,200,3" \
--enable_profiling

# Batch processing with external data
sit4tfjs \
--input_tfjs_file_path ./model_multi_input_fix_tfjs \
--batch_size 4 \
--input_numpy_file_paths "feat:batch_feat.npy pc_dep:batch_depth.npy" \
--test_loop_count 200
```

### Python API Usage

```python
from sit4tfjs import TFJSBenchmark

# Basic usage - multi-input model
benchmark = TFJSBenchmark(
    model_path="./model_multi_input_fix_tfjs",
    batch_size=1,
    test_loop_count=100,
    enable_profiling=True
)

# Run benchmark
results = benchmark.benchmark()

# Access results
print(f"Average inference time: {results['avg_time_ms']:.3f} ms")
print(f"Throughput: {1000/results['avg_time_ms']:.1f} FPS")

# Advanced usage - with custom shapes and external data
benchmark_advanced = TFJSBenchmark(
    model_path="./model_multi_input_fix_tfjs",
    batch_size=4,
    fixed_shapes={
        "feat": [4, 112, 200, 64],
        "pc_dep": [4, 112, 200, 3]
    },
    input_numpy_file_paths={
        "feat": "batch_feat_data.npy",
        "pc_dep": "batch_depth_data.npy"
    },
    test_loop_count=50,
    enable_profiling=True
)

results_advanced = benchmark_advanced.benchmark()
```

### Creating Input Data Files

```python
import numpy as np

# Create sample input data for multi-input model
feat_data = np.random.randn(1, 112, 200, 64).astype(np.float32)
pc_dep_data = np.random.randn(1, 112, 200, 3).astype(np.float32)

# Save as numpy files
np.save('feat_data.npy', feat_data)
np.save('depth_data.npy', pc_dep_data)

# For single input model
input_data = np.random.randn(1, 105, 90).astype(np.float32)
np.save('input_data.npy', input_data)

# For batch processing
batch_feat = np.random.randn(4, 112, 200, 64).astype(np.float32)
batch_depth = np.random.randn(4, 112, 200, 3).astype(np.float32)
np.save('batch_feat.npy', batch_feat)
np.save('batch_depth.npy', batch_depth)
```

### Setting Up TensorFlow.js Runtime (Optional)

For true TensorFlow.js benchmarking, install Node.js dependencies:

```bash
# Install Node.js (if not already installed)
# Ubuntu/Debian:
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS with Homebrew:
brew install node

# Windows: Download from https://nodejs.org/

# Install TensorFlow.js for Node.js
npm install @tensorflow/tfjs-node

# For GPU support (optional):
npm install @tensorflow/tfjs-node-gpu
```

**Runtime Detection:**
- **Node.js Runtime**: If Node.js and @tensorflow/tfjs-node are available, uses Node.js TFJS runtime
- **Browser Runtime**: For browser backends (cpu, webgl, webgpu, wasm), uses headless browser automation
- **Fallback**: Falls back to mock inference with correct shapes and timing simulation

## Model Support

### Supported Formats
- **TensorFlow.js Graph Models**: model.json + .bin weight files
- **Multi-Input Models**: Models with multiple named input tensors
- **Dynamic Shapes**: Models with variable input dimensions (-1 dimensions)
- **Mixed Precision**: Support for various tensor data types (float32, int32, etc.)

### Input Handling
- **Automatic Shape Inference**: Reads input specifications from model.json
- **Multi-Input Support**: Full support for models with multiple named inputs (e.g., feat + pc_dep)
- **Dynamic Tensor Support**: Handles models with variable batch sizes or sequence lengths
- **Custom Shape Override**: Manual specification for dynamic dimensions using `--fixed_shapes`
- **External Data Loading**: Support for numpy (.npy) input files with `--input_numpy_file_paths`
- **Random Data Generation**: Automatic generation of realistic test inputs
- **Flexible Input Specification**: Space-separated format for multiple inputs:
  - `--fixed_shapes "input1:1,224,224,3 input2:1,100"`
  - `--input_numpy_file_paths "input1:data1.npy input2:data2.npy"`

### Execution Providers

sit4tfjs supports multiple execution providers for comprehensive benchmarking:

| Provider | Environment | Description | Use Case |
|----------|-------------|-------------|-----------|
| `cpu` (default) | Browser | Browser CPU backend | Web deployment, CPU-only environments, default choice |
| `webgl` | Browser | WebGL-accelerated execution | Web deployment with GPU acceleration |
| `webgpu` | Browser | WebGPU backend (experimental) | Latest web GPU acceleration |
| `wasm` | Browser | WebAssembly backend | Cross-platform web deployment |
| `nodejs` | Node.js | Native TensorFlow.js runtime | Server-side deployment, highest accuracy |

**Performance Characteristics:**
- **webgpu** > **webgl** > **wasm** > **cpu** (typical performance order)
- **nodejs** provides the most accurate server-side performance
- **cpu** (default) provides good baseline performance for web deployment
- Browser backends simulate real web deployment scenarios

### Tested Model Types
- Computer Vision Models (CNN, ResNet, EfficientNet)
- Natural Language Processing (BERT, Transformer)
- Time Series Analysis
- Multi-Modal Models (Vision + Text)
- Custom Neural Networks

## Performance Analysis

### Metrics Provided
- **Inference Time**: Per-inference timing in milliseconds
- **Statistical Analysis**: Min, max, average, and standard deviation
- **Throughput**: Inferences per second (FPS)
- **Memory Usage**: Estimated model memory footprint
- **Parameter Count**: Total model parameters

### Sample Output
```
================================================================================
sit4tfjs - Simple Inference Test for TensorFlow.js
Benchmark tool for TensorFlow.js models
================================================================================

Model: ./model_multi_input_fix_tfjs
Test loops: 100
Batch size: 1

Input tensors:
  feat: [1, 112, 200, 64] (DT_FLOAT)
  pc_dep: [1, 112, 200, 3] (DT_FLOAT)

Output tensors:
  output_0: [1, 112, 200, 3] (DT_FLOAT)
  output_2: [1, 112, 200, 1] (DT_FLOAT)
  Identity_3:0: [1, 112, 200, 8] (DT_FLOAT)
  Identity_1:0: [1, 112, 200, 8] (DT_FLOAT)

Running 100 inference iterations...
  Completed 100/100 iterations

============================================================
BENCHMARK RESULTS
============================================================
Average inference time: 45.234 ms
Minimum inference time: 42.156 ms
Maximum inference time: 52.789 ms
Standard deviation:     2.145 ms
============================================================
```

## Command-Line Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--input_tfjs_file_path` | string | **Required** | Path to TensorFlow.js model directory |
| `--batch_size` | int | 1 | Batch size for inference |
| `--test_loop_count` | int | 100 | Number of inference iterations |
| `--fixed_shapes` | string | "" | Fixed input shapes (format: "input1:1,224,224,3") |
| `--input_numpy_file_paths` | string | "" | External numpy input files (format: "input1:data1.npy") |
| `--enable_profiling` | flag | False | Enable detailed profiling output |
| `--info_only` | flag | False | Display model info without benchmarking |
| `--debug` | flag | False | Enable debug mode with detailed errors |

## Error Handling

### Common Issues and Solutions

**Model Loading Errors**
```bash
# Verify model structure
sit4tfjs --input_tfjs_file_path ./model --info_only

# Check file permissions
ls -la ./model/
```

**Shape Mismatch Errors**
```bash
# Override dynamic shapes
sit4tfjs \
--input_tfjs_file_path ./model \
--fixed_shapes "input:1,224,224,3"
```

**Memory Issues**
```bash
# Reduce batch size
sit4tfjs \
--input_tfjs_file_path ./model \
--batch_size 1
```

## Troubleshooting

### Installation Issues
```bash
# Upgrade pip and dependencies
pip install --upgrade pip setuptools wheel
pip install --upgrade tensorflowjs

# Add TensorFlow if needed for SavedModel conversion
pip install sit4tfjs[tensorflow]

# For M1 Macs (if using TensorFlow)
pip install tensorflow-macos
```

### Performance Optimization
- Use smaller batch sizes for memory-constrained environments
- Enable CPU optimizations in TensorFlow
- Consider model quantization for faster inference
- Use profiling mode to identify bottlenecks

### Debug Mode
```bash
# Enable detailed error output
sit4tfjs --input_tfjs_file_path ./model --debug
```

## Requirements

### System Requirements
- **Operating System**: Linux, macOS, Windows
- **Python**: 3.10+
- **Memory**: Minimum 4GB RAM (8GB+ recommended for large models)
- **Storage**: Model size + 1GB for temporary files

### Python Dependencies
```
# Core dependencies (always required)
tensorflowjs>=4.0.0
numpy>=1.19.0
rich>=10.0.0
psutil>=5.8.0

# Optional dependencies
tensorflow>=2.10.0  # Only for SavedModel conversion
```

### Installation with Optional Dependencies
```bash
# Basic installation (browser backends only)
pip install sit4tfjs

# With TensorFlow for SavedModel support
pip install sit4tfjs[tensorflow]

# For development
pip install sit4tfjs[dev]
```

## Development

### Running Tests
```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest tests/

# Run with coverage
pytest --cov=sit4tfjs tests/
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Related Projects

- **[sit4onnxw](https://github.com/PINTO0309/sit4onnxw)**: ONNX model benchmarking tool
- **[TensorFlow.js](https://www.tensorflow.org/js)**: Machine learning for JavaScript
- **[PINTO Model Zoo](https://github.com/PINTO0309/PINTO_model_zoo)**: Pre-trained model collection
