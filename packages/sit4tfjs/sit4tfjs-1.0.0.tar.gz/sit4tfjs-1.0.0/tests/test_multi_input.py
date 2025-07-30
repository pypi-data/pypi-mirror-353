"""
Unit tests for multi-input functionality.
"""

import pytest
import tempfile
import json
import numpy as np
from pathlib import Path

from sit4tfjs.utils import parse_fixed_shapes, parse_numpy_files
from sit4tfjs.core import TFJSBenchmark


class TestMultiInputSupport:
    """Test multi-input model support."""

    def create_multi_input_model(self, tmpdir):
        """Create a mock multi-input TensorFlow.js model for testing."""
        model_dir = Path(tmpdir) / "multi_input_model"
        model_dir.mkdir()
        
        # Create mock model.json with multiple inputs and outputs
        model_info = {
            "format": "graph-model",
            "generatedBy": "Test",
            "convertedBy": "Test Converter",
            "signature": {
                "inputs": {
                    "feat": {
                        "name": "feat:0",
                        "dtype": "DT_FLOAT",
                        "tensorShape": {
                            "dim": [
                                {"size": "1"},
                                {"size": "112"},
                                {"size": "200"},
                                {"size": "64"}
                            ]
                        }
                    },
                    "pc_dep": {
                        "name": "pc_dep:0",
                        "dtype": "DT_FLOAT",
                        "tensorShape": {
                            "dim": [
                                {"size": "1"},
                                {"size": "112"},
                                {"size": "200"},
                                {"size": "3"}
                            ]
                        }
                    }
                },
                "outputs": {
                    "velocity": {
                        "name": "velocity:0",
                        "dtype": "DT_FLOAT",
                        "tensorShape": {
                            "dim": [
                                {"size": "1"},
                                {"size": "112"},
                                {"size": "200"},
                                {"size": "3"}
                            ]
                        }
                    },
                    "depth": {
                        "name": "depth:0",
                        "dtype": "DT_FLOAT",
                        "tensorShape": {
                            "dim": [
                                {"size": "1"},
                                {"size": "112"},
                                {"size": "200"},
                                {"size": "1"}
                            ]
                        }
                    }
                }
            },
            "weightsManifest": [
                {
                    "weights": [
                        {"name": "weight1", "shape": [3, 3, 67, 256], "dtype": "float32"}
                    ]
                }
            ]
        }
        
        model_json_path = model_dir / "model.json"
        with open(model_json_path, "w") as f:
            json.dump(model_info, f)
        
        return str(model_dir)

    def test_parse_multiple_fixed_shapes(self):
        """Test parsing multiple fixed shapes."""
        shapes_str = "feat:1,112,200,64 pc_dep:1,112,200,3 extra:1,100"
        result = parse_fixed_shapes(shapes_str)
        
        expected = {
            "feat": [1, 112, 200, 64],
            "pc_dep": [1, 112, 200, 3],
            "extra": [1, 100]
        }
        assert result == expected

    def test_parse_multiple_numpy_files(self):
        """Test parsing multiple numpy file paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dummy numpy files
            feat_file = Path(tmpdir) / "feat.npy"
            depth_file = Path(tmpdir) / "depth.npy"
            
            np.save(feat_file, np.random.randn(1, 112, 200, 64))
            np.save(depth_file, np.random.randn(1, 112, 200, 3))
            
            files_str = f"feat:{feat_file} pc_dep:{depth_file}"
            result = parse_numpy_files(files_str)
            
            expected = {
                "feat": str(feat_file),
                "pc_dep": str(depth_file)
            }
            assert result == expected

    def test_multi_input_model_specs(self):
        """Test multi-input model specification parsing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = self.create_multi_input_model(tmpdir)
            
            benchmark = TFJSBenchmark(model_path=model_path)
            
            # Test input specs
            input_specs = benchmark.get_input_specs()
            assert len(input_specs) == 2
            assert "feat" in input_specs
            assert "pc_dep" in input_specs
            assert input_specs["feat"]["shape"] == [1, 112, 200, 64]
            assert input_specs["pc_dep"]["shape"] == [1, 112, 200, 3]
            
            # Test output specs
            output_specs = benchmark.get_output_specs()
            assert len(output_specs) == 2
            assert "velocity" in output_specs
            assert "depth" in output_specs

    def test_multi_input_with_fixed_shapes(self):
        """Test multi-input model with fixed shapes override."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = self.create_multi_input_model(tmpdir)
            
            fixed_shapes = {
                "feat": [2, 112, 200, 64],
                "pc_dep": [2, 112, 200, 3]
            }
            
            benchmark = TFJSBenchmark(
                model_path=model_path,
                fixed_shapes=fixed_shapes
            )
            
            input_specs = benchmark.get_input_specs()
            assert input_specs["feat"]["shape"] == [2, 112, 200, 64]
            assert input_specs["pc_dep"]["shape"] == [2, 112, 200, 3]

    def test_multi_input_random_generation(self):
        """Test random input generation for multi-input models."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = self.create_multi_input_model(tmpdir)
            
            benchmark = TFJSBenchmark(model_path=model_path)
            inputs = benchmark.generate_random_inputs()
            
            assert len(inputs) == 2
            assert "feat" in inputs
            assert "pc_dep" in inputs
            assert inputs["feat"].shape == (1, 112, 200, 64)
            assert inputs["pc_dep"].shape == (1, 112, 200, 3)
            assert inputs["feat"].dtype == np.float32
            assert inputs["pc_dep"].dtype == np.float32

    def test_multi_input_with_numpy_files(self):
        """Test multi-input model with external numpy files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = self.create_multi_input_model(tmpdir)
            
            # Create numpy input files
            feat_file = Path(tmpdir) / "feat.npy"
            depth_file = Path(tmpdir) / "depth.npy"
            
            feat_data = np.random.randn(1, 112, 200, 64).astype(np.float32)
            depth_data = np.random.randn(1, 112, 200, 3).astype(np.float32)
            
            np.save(feat_file, feat_data)
            np.save(depth_file, depth_data)
            
            numpy_file_paths = {
                "feat": str(feat_file),
                "pc_dep": str(depth_file)
            }
            
            benchmark = TFJSBenchmark(
                model_path=model_path,
                input_numpy_file_paths=numpy_file_paths
            )
            
            inputs = benchmark.generate_random_inputs()
            
            # Should load from files, not generate random
            assert np.array_equal(inputs["feat"], feat_data)
            assert np.array_equal(inputs["pc_dep"], depth_data)

    def test_mock_inference_multi_output(self):
        """Test mock inference with multiple outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = self.create_multi_input_model(tmpdir)
            
            benchmark = TFJSBenchmark(model_path=model_path)
            inputs = benchmark.generate_random_inputs()
            
            outputs, inference_time = benchmark.run_inference(inputs)
            
            assert len(outputs) == 2
            assert "velocity" in outputs
            assert "depth" in outputs
            assert outputs["velocity"].shape == (1, 112, 200, 3)
            assert outputs["depth"].shape == (1, 112, 200, 1)
            assert inference_time > 0