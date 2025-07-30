"""
Unit tests for core benchmarking functionality.
"""

import pytest
import tempfile
import json
from pathlib import Path

from sit4tfjs.core import TFJSBenchmark


class TestTFJSBenchmark:
    """Test TensorFlow.js benchmark functionality."""

    def create_mock_model(self, tmpdir):
        """Create a mock TensorFlow.js model for testing."""
        model_dir = Path(tmpdir) / "mock_model"
        model_dir.mkdir()
        
        # Create mock model.json
        model_info = {
            "format": "graph-model",
            "generatedBy": "Test",
            "convertedBy": "Test Converter",
            "signature": {
                "inputs": {
                    "input1": {
                        "name": "input1:0",
                        "dtype": "DT_FLOAT",
                        "tensorShape": {
                            "dim": [
                                {"size": "1"},
                                {"size": "224"},
                                {"size": "224"},
                                {"size": "3"}
                            ]
                        }
                    }
                },
                "outputs": {
                    "output1": {
                        "name": "output1:0",
                        "dtype": "DT_FLOAT",
                        "tensorShape": {
                            "dim": [
                                {"size": "1"},
                                {"size": "1000"}
                            ]
                        }
                    }
                }
            },
            "weightsManifest": [
                {
                    "weights": [
                        {"name": "weight1", "shape": [224, 224, 3, 64], "dtype": "float32"}
                    ]
                }
            ]
        }
        
        model_json_path = model_dir / "model.json"
        with open(model_json_path, "w") as f:
            json.dump(model_info, f)
        
        return str(model_dir)

    def test_model_loading(self):
        """Test model loading and info parsing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = self.create_mock_model(tmpdir)
            
            benchmark = TFJSBenchmark(
                model_path=model_path,
                batch_size=1,
                test_loop_count=1
            )
            
            assert benchmark.model_info["format"] == "graph-model"

    def test_input_specs(self):
        """Test input specification parsing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = self.create_mock_model(tmpdir)
            
            benchmark = TFJSBenchmark(model_path=model_path)
            input_specs = benchmark.get_input_specs()
            
            assert "input1" in input_specs
            assert input_specs["input1"]["shape"] == [1, 224, 224, 3]
            assert input_specs["input1"]["dtype"] == "DT_FLOAT"

    def test_output_specs(self):
        """Test output specification parsing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = self.create_mock_model(tmpdir)
            
            benchmark = TFJSBenchmark(model_path=model_path)
            output_specs = benchmark.get_output_specs()
            
            assert "output1" in output_specs
            assert output_specs["output1"]["shape"] == [1, 1000]
            assert output_specs["output1"]["dtype"] == "DT_FLOAT"

    def test_random_input_generation(self):
        """Test random input generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = self.create_mock_model(tmpdir)
            
            benchmark = TFJSBenchmark(model_path=model_path)
            inputs = benchmark.generate_random_inputs()
            
            assert "input1" in inputs
            assert inputs["input1"].shape == (1, 224, 224, 3)

    def test_fixed_shapes(self):
        """Test fixed shape override."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = self.create_mock_model(tmpdir)
            
            fixed_shapes = {"input1": [2, 224, 224, 3]}
            benchmark = TFJSBenchmark(
                model_path=model_path,
                fixed_shapes=fixed_shapes
            )
            
            input_specs = benchmark.get_input_specs()
            assert input_specs["input1"]["shape"] == [2, 224, 224, 3]

    def test_mock_inference(self):
        """Test mock inference (when model can't be loaded)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = self.create_mock_model(tmpdir)
            
            benchmark = TFJSBenchmark(model_path=model_path)
            inputs = benchmark.generate_random_inputs()
            
            outputs, inference_time = benchmark.run_inference(inputs)
            
            assert "output1" in outputs
            assert outputs["output1"].shape == (1, 1000)
            assert inference_time > 0