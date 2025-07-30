"""
Unit tests for utility functions.
"""

import pytest
import tempfile
import json
from pathlib import Path

from sit4tfjs.utils import (
    parse_shape_string,
    parse_fixed_shapes,
    parse_numpy_files,
    format_shape,
    validate_model_path,
    estimate_memory_usage,
    get_system_info,
)


class TestUtilityFunctions:
    """Test utility functions."""

    def test_parse_shape_string(self):
        """Test shape string parsing."""
        assert parse_shape_string("1,224,224,3") == [1, 224, 224, 3]
        assert parse_shape_string("1,100") == [1, 100]
        assert parse_shape_string("64") == [64]
        
        with pytest.raises(ValueError):
            parse_shape_string("1,invalid,3")

    def test_parse_fixed_shapes(self):
        """Test fixed shapes parsing."""
        result = parse_fixed_shapes("input1:1,224,224,3 input2:1,100")
        expected = {
            "input1": [1, 224, 224, 3],
            "input2": [1, 100]
        }
        assert result == expected
        
        assert parse_fixed_shapes("") == {}
        
        with pytest.raises(ValueError):
            parse_fixed_shapes("invalid_format")

    def test_format_shape(self):
        """Test shape formatting."""
        assert format_shape([1, 224, 224, 3]) == "[1, 224, 224, 3]"
        assert format_shape([100]) == "[100]"
        assert format_shape([]) == "[]"

    def test_validate_model_path(self):
        """Test model path validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "test_model"
            model_dir.mkdir()
            
            # Create a dummy model.json
            model_json = model_dir / "model.json"
            model_json.write_text('{"format": "graph-model"}')
            
            # Should succeed
            result = validate_model_path(str(model_dir))
            assert result == model_dir
            
            # Should fail if model.json doesn't exist
            model_json.unlink()
            with pytest.raises(FileNotFoundError):
                validate_model_path(str(model_dir))

    def test_estimate_memory_usage(self):
        """Test memory usage estimation."""
        model_info = {
            "weightsManifest": [
                {
                    "weights": [
                        {"shape": [3, 3, 64, 128]},  # 3*3*64*128 = 73,728 params
                        {"shape": [128]},  # 128 params
                    ]
                }
            ]
        }
        
        # Total: 73,856 params * 4 bytes = 295,424 bytes = ~0.28 MB
        memory_mb = estimate_memory_usage(model_info)
        assert 0.25 < memory_mb < 0.35

    def test_get_system_info(self):
        """Test system info retrieval."""
        info = get_system_info()
        assert "python_version" in info
        assert "platform" in info
        assert "tensorflow_version" in info
        assert "tensorflowjs_version" in info