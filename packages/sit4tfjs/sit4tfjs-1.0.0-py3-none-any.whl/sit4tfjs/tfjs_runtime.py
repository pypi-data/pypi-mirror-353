"""
TensorFlow.js runtime interface for Python.
"""

import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import numpy as np


class TensorFlowJSRuntime:
    """TensorFlow.js runtime for model inference."""
    
    def __init__(self, model_path: str):
        """
        Initialize TensorFlow.js runtime.
        
        Args:
            model_path: Path to TensorFlow.js model directory
        """
        self.model_path = Path(model_path)
        self.temp_dir = None
        self.node_script_path = None
        self._setup_runtime()
    
    def _setup_runtime(self) -> None:
        """Setup TensorFlow.js runtime environment."""
        try:
            # Create temporary directory for runtime files
            self.temp_dir = Path(tempfile.mkdtemp())
            
            # Create Node.js script for TFJS inference
            self._create_node_script()
            
            # Verify Node.js and @tensorflow/tfjs-node are available
            self._verify_environment()
            
        except Exception as e:
            print(f"Warning: TensorFlow.js runtime setup failed: {e}")
            print("Falling back to mock inference...")
            self.node_script_path = None
    
    def _create_node_script(self) -> None:
        """Create Node.js script for TensorFlow.js inference."""
        script_content = '''
const tf = require('@tensorflow/tfjs-node');
const fs = require('fs');
const path = require('path');

class TFJSInference {
    constructor() {
        this.model = null;
    }
    
    async loadModel(modelPath) {
        try {
            // Load TensorFlow.js model
            this.model = await tf.loadGraphModel(`file://${modelPath}/model.json`);
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    async predict(inputData) {
        if (!this.model) {
            throw new Error('Model not loaded');
        }
        
        try {
            // Convert input data to tensors
            const inputs = {};
            for (const [name, data] of Object.entries(inputData)) {
                inputs[name] = tf.tensor(data.data, data.shape, data.dtype);
            }
            
            const startTime = process.hrtime.bigint();
            
            // Run inference
            const outputs = this.model.predict(inputs);
            
            // Ensure computation is complete by accessing output data
            if (Array.isArray(outputs)) {
                await Promise.all(outputs.map(output => output.data()));
            } else if (typeof outputs === 'object') {
                await Promise.all(Object.values(outputs).map(tensor => tensor.data()));
            } else {
                await outputs.data();
            }
            
            const endTime = process.hrtime.bigint();
            const inferenceTime = Number(endTime - startTime) / 1000000; // Convert to milliseconds
            
            // Convert outputs to plain objects
            const result = {};
            if (Array.isArray(outputs)) {
                for (let i = 0; i < outputs.length; i++) {
                    const outputData = await outputs[i].data();
                    result[`output_${i}`] = {
                        data: Array.from(outputData),
                        shape: outputs[i].shape,
                        dtype: outputs[i].dtype
                    };
                    outputs[i].dispose();
                }
            } else if (typeof outputs === 'object') {
                for (const [name, tensor] of Object.entries(outputs)) {
                    const outputData = await tensor.data();
                    result[name] = {
                        data: Array.from(outputData),
                        shape: tensor.shape,
                        dtype: tensor.dtype
                    };
                    tensor.dispose();
                }
            } else {
                const outputData = await outputs.data();
                result['output'] = {
                    data: Array.from(outputData),
                    shape: outputs.shape,
                    dtype: outputs.dtype
                };
                outputs.dispose();
            }
            
            // Dispose input tensors
            for (const tensor of Object.values(inputs)) {
                tensor.dispose();
            }
            
            return {
                success: true,
                outputs: result,
                inferenceTime: inferenceTime
            };
            
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    async processCommand(command) {
        try {
            const cmd = JSON.parse(command);
            
            switch (cmd.action) {
                case 'load':
                    return await this.loadModel(cmd.modelPath);
                    
                case 'predict':
                    return await this.predict(cmd.inputData);
                    
                default:
                    return { success: false, error: 'Unknown command' };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
}

// Main execution
const inference = new TFJSInference();

// Read command from stdin
let inputData = '';
process.stdin.on('data', (chunk) => {
    inputData += chunk;
});

process.stdin.on('end', async () => {
    try {
        const result = await inference.processCommand(inputData.trim());
        console.log(JSON.stringify(result));
        process.exit(0);
    } catch (error) {
        console.log(JSON.stringify({ success: false, error: error.message }));
        process.exit(1);
    }
});
'''
        
        self.node_script_path = self.temp_dir / "tfjs_inference.js"
        with open(self.node_script_path, 'w') as f:
            f.write(script_content)
    
    def _verify_environment(self) -> None:
        """Verify Node.js and TensorFlow.js are available."""
        try:
            # Check Node.js
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise RuntimeError("Node.js not found")
            
            # Check @tensorflow/tfjs-node
            test_script = '''
            try {
                require('@tensorflow/tfjs-node');
                console.log('OK');
            } catch (error) {
                console.log('ERROR: ' + error.message);
                process.exit(1);
            }
            '''
            
            test_file = self.temp_dir / "test_tfjs.js"
            with open(test_file, 'w') as f:
                f.write(test_script)
            
            result = subprocess.run(['node', str(test_file)], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0 or 'ERROR' in result.stdout:
                raise RuntimeError("@tensorflow/tfjs-node not found")
                
        except Exception as e:
            raise RuntimeError(f"Environment verification failed: {e}")
    
    def load_model(self) -> bool:
        """
        Load TensorFlow.js model.
        
        Returns:
            True if successful, False otherwise
        """
        if self.node_script_path is None:
            return False
        
        try:
            command = {
                'action': 'load',
                'modelPath': str(self.model_path.absolute())
            }
            
            result = subprocess.run(
                ['node', str(self.node_script_path)],
                input=json.dumps(command),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"Node.js error: {result.stderr}")
                return False
            
            response = json.loads(result.stdout)
            if not response['success']:
                print(f"Model loading failed: {response.get('error', 'Unknown error')}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Model loading error: {e}")
            return False
    
    def predict(self, inputs: Dict[str, np.ndarray]) -> Tuple[Optional[Dict[str, np.ndarray]], float]:
        """
        Run inference with TensorFlow.js.
        
        Args:
            inputs: Input tensors as numpy arrays
            
        Returns:
            Tuple of (outputs, inference_time_ms)
        """
        if self.node_script_path is None:
            return None, 0.0
        
        try:
            # Convert numpy arrays to serializable format
            input_data = {}
            for name, array in inputs.items():
                input_data[name] = {
                    'data': array.flatten().tolist(),
                    'shape': list(array.shape),
                    'dtype': str(array.dtype)
                }
            
            command = {
                'action': 'predict',
                'inputData': input_data
            }
            
            result = subprocess.run(
                ['node', str(self.node_script_path)],
                input=json.dumps(command),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                print(f"Inference error: {result.stderr}")
                return None, 0.0
            
            response = json.loads(result.stdout)
            if not response['success']:
                print(f"Inference failed: {response.get('error', 'Unknown error')}")
                return None, 0.0
            
            # Convert outputs back to numpy arrays
            outputs = {}
            for name, output_info in response['outputs'].items():
                data = np.array(output_info['data'], dtype=np.float32)
                outputs[name] = data.reshape(output_info['shape'])
            
            return outputs, response['inferenceTime']
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return None, 0.0
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        if self.temp_dir and self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def __del__(self):
        """Destructor to clean up resources."""
        try:
            self.cleanup()
        except:
            pass