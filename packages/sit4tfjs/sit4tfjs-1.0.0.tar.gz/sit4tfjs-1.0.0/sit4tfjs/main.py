#!/usr/bin/env python3
"""
sit4tfjs - Simple Inference Test for TensorFlow.js

Command-line interface for benchmarking TensorFlow.js models.
"""

import argparse
import sys
import traceback
from pathlib import Path
from typing import Optional

from .core import TFJSBenchmark
from .utils import (
    parse_fixed_shapes,
    parse_numpy_files,
    validate_model_path,
    check_dependencies,
    get_system_info,
    print_model_summary,
    get_model_info,
)


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="sit4tfjs",
        description="Simple Inference Test for TensorFlow.js - Benchmark tool for TensorFlow.js models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic benchmark
  sit4tfjs --input_tfjs_file_path ./model_multi_input_fix_tfjs

  # Custom batch size and iterations
  sit4tfjs --input_tfjs_file_path ./model_optimized_fix_tfjs --batch_size 4 --test_loop_count 50

  # Fixed input shapes
  sit4tfjs --input_tfjs_file_path ./model_multi_input_fix_tfjs --fixed_shapes "feat:1,112,200,64 pc_dep:1,112,200,3"

  # With external numpy inputs
  sit4tfjs --input_tfjs_file_path ./model_multi_input_fix_tfjs --input_numpy_file_paths "feat:feat.npy pc_dep:pc_dep.npy"

  # Enable profiling
  sit4tfjs --input_tfjs_file_path ./model_multi_input_fix_tfjs --enable_profiling

  # Browser benchmarking with WebGL backend
  sit4tfjs --input_tfjs_file_path ./model_multi_input_fix_tfjs --execution_provider webgl

  # Browser benchmarking with WebGPU backend
  sit4tfjs --input_tfjs_file_path ./model_multi_input_fix_tfjs --execution_provider webgpu
        """,
    )

    # Required arguments
    parser.add_argument(
        "--input_tfjs_file_path",
        type=str,
        required=True,
        help="Input TensorFlow.js model directory path containing model.json",
    )

    # Optional arguments
    parser.add_argument(
        "--batch_size",
        type=int,
        default=1,
        help="Batch size for inference (default: 1)",
    )

    parser.add_argument(
        "--fixed_shapes",
        type=str,
        default="",
        help='Fixed input shapes in format "input1:1,224,224,3 input2:1,100"',
    )

    parser.add_argument(
        "--test_loop_count",
        type=int,
        default=100,
        help="Number of inference iterations for benchmarking (default: 100)",
    )

    parser.add_argument(
        "--enable_profiling",
        action="store_true",
        help="Enable detailed profiling output",
    )

    parser.add_argument(
        "--input_numpy_file_paths",
        type=str,
        default="",
        help='Paths to numpy input files in format "input1:data1.npy input2:data2.npy"',
    )

    parser.add_argument(
        "--info_only",
        action="store_true",
        help="Display model information only without running benchmark",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="sit4tfjs 1.0.0",
    )

    parser.add_argument(
        "--execution_provider",
        type=str,
        default="cpu",
        choices=["cpu", "webgl", "webgpu", "wasm", "nodejs"],
        help="Execution provider for TensorFlow.js (default: cpu)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with detailed error messages",
    )

    return parser


def print_header():
    """Print application header."""
    print("=" * 80)
    print("sit4tfjs - Simple Inference Test for TensorFlow.js")
    print("Benchmark tool for TensorFlow.js models")
    print("=" * 80)


def print_system_info():
    """Print system information."""
    info = get_system_info()
    print("\nSystem Information:")
    for key, value in info.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        print_header()

        # Check core dependencies
        if not check_dependencies():
            print("\nError: Core dependencies are missing.")
            print("Please install required packages:")
            print("  pip install sit4tfjs")
            return 1

        if args.debug:
            print_system_info()

        # Validate model path
        try:
            model_path = validate_model_path(args.input_tfjs_file_path)
        except (FileNotFoundError, ValueError) as e:
            print(f"\nError: {e}")
            return 1

        print(f"\nModel path: {model_path}")

        # Load and display model info
        try:
            model_info = get_model_info(model_path)
            print_model_summary(model_info)
        except Exception as e:
            print(f"\nError loading model info: {e}")
            if args.debug:
                traceback.print_exc()
            return 1

        # If info only, stop here
        if args.info_only:
            return 0

        # Parse additional arguments
        try:
            fixed_shapes = parse_fixed_shapes(args.fixed_shapes)
            numpy_file_paths = parse_numpy_files(args.input_numpy_file_paths)
        except (ValueError, FileNotFoundError) as e:
            print(f"\nError parsing arguments: {e}")
            return 1

        # Create and run benchmark
        try:
            benchmark = TFJSBenchmark(
                model_path=str(model_path),
                batch_size=args.batch_size,
                fixed_shapes=fixed_shapes,
                test_loop_count=args.test_loop_count,
                enable_profiling=args.enable_profiling,
                input_numpy_file_paths=numpy_file_paths,
                execution_provider=args.execution_provider,
            )

            results = benchmark.benchmark()

            # Save results if requested (future enhancement)
            # if args.output_results:
            #     with open(args.output_results, 'w') as f:
            #         json.dump(results, f, indent=2, default=str)

        except Exception as e:
            print(f"\nError during benchmarking: {e}")
            if args.debug:
                traceback.print_exc()
            return 1

        return 0

    except KeyboardInterrupt:
        print("\n\nBenchmarking interrupted by user.")
        return 130
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        if args.debug:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())