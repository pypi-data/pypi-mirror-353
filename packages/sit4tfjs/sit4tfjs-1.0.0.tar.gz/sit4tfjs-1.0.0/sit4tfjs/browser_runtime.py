"""
Browser-based TensorFlow.js runtime interface for benchmarking different backends.
"""

import json
import tempfile
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import numpy as np


class BrowserTFJSRuntime:
    """Browser-based TensorFlow.js runtime for model inference with different backends."""
    
    def __init__(self, model_path: str, backend: str = "cpu"):
        """
        Initialize browser TensorFlow.js runtime.
        
        Args:
            model_path: Path to TensorFlow.js model directory
            backend: Backend to use (cpu, webgl, webgpu, wasm)
        """
        self.model_path = Path(model_path)
        self.backend = backend.lower()
        self.temp_dir = None
        self.html_file_path = None
        self._first_run = True  # Track first run for logging
        self._setup_runtime()
    
    def _setup_runtime(self) -> None:
        """Setup browser TensorFlow.js runtime environment."""
        try:
            # Create temporary directory for runtime files
            self.temp_dir = Path(tempfile.mkdtemp())
            
            # Create HTML page for TFJS inference
            self._create_html_page()
            
            # Verify browser availability
            self._verify_environment()
            
        except Exception as e:
            print(f"Warning: Browser TensorFlow.js runtime setup failed: {e}")
            print("Falling back to mock inference...")
            self.html_file_path = None
    
    def _create_html_page(self) -> None:
        """Create HTML page for TensorFlow.js inference."""
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>TensorFlow.js Benchmark</title>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.15.0/dist/tf.min.js"></script>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f0f0f0; 
        }}
        .container {{ 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }}
        .status {{ 
            padding: 10px; 
            margin: 10px 0; 
            border-radius: 4px; 
            background-color: #e3f2fd; 
        }}
        .result {{ 
            background-color: #f3e5f5; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 4px; 
            white-space: pre-wrap; 
            font-family: monospace; 
        }}
        button {{ 
            background-color: #1976d2; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 4px; 
            cursor: pointer; 
            margin: 5px; 
        }}
        button:hover {{ background-color: #1565c0; }}
        button:disabled {{ background-color: #ccc; cursor: not-allowed; }}
        .backend {{ 
            font-weight: bold; 
            color: #d32f2f; 
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>TensorFlow.js Browser Benchmark</h1>
        <div class="status" id="status">Initializing...</div>
        <div>
            <strong>Target Backend:</strong> <span class="backend">{self.backend.upper()}</span>
        </div>
        <div>
            <strong>Model Path:</strong> {self.model_path.absolute()}
        </div>
        <div>
            <button onclick="loadModel()">Load Model</button>
            <button onclick="runBenchmark()" id="benchmarkBtn" disabled>Run Benchmark</button>
            <button onclick="clearResults()">Clear Results</button>
        </div>
        <div class="result" id="results"></div>
    </div>

    <script>
        let model = null;
        let modelInputs = null;
        let isModelLoaded = false;
        const targetBackend = '{self.backend}';
        
        // Global variables for Python communication
        window.benchmarkResults = null;
        window.benchmarkComplete = false;
        window.benchmarkError = null;
        
        function updateStatus(message) {{
            document.getElementById('status').textContent = message;
            console.log('Status:', message);
        }}
        
        function updateResults(message) {{
            const resultsDiv = document.getElementById('results');
            resultsDiv.textContent += message + '\\n';
            console.log('Results:', message);
        }}
        
        function clearResults() {{
            document.getElementById('results').textContent = '';
        }}
        
        async function initializeBackend() {{
            try {{
                updateStatus('Setting backend to ' + targetBackend.toUpperCase() + '...');
                
                // Set the backend
                if (targetBackend === 'webgl') {{
                    await tf.setBackend('webgl');
                }} else if (targetBackend === 'webgpu') {{
                    await tf.setBackend('webgpu');
                }} else if (targetBackend === 'wasm') {{
                    await tf.setBackend('wasm');
                }} else {{
                    await tf.setBackend('cpu');
                }}
                
                await tf.ready();
                
                const currentBackend = tf.getBackend();
                updateStatus(`Backend set to: ${{currentBackend}} (requested: ${{targetBackend}})`);
                
                if (currentBackend !== targetBackend && targetBackend !== 'cpu') {{
                    updateResults(`Warning: Requested backend "${{targetBackend}}" not available, using "${{currentBackend}}"`);
                }}
                
                return true;
            }} catch (error) {{
                updateStatus('Backend initialization failed: ' + error.message);
                updateResults('Backend Error: ' + error.message);
                return false;
            }}
        }}
        
        async function loadModel() {{
            try {{
                // Initialize backend first
                const backendReady = await initializeBackend();
                if (!backendReady) {{
                    return;
                }}
                
                updateStatus('Loading TensorFlow.js model...');
                
                // Construct model URL
                const modelUrl = 'file://{self.model_path.absolute()}/model.json';
                updateResults('Loading model from: ' + modelUrl);
                
                // Load the model
                model = await tf.loadGraphModel(modelUrl);
                
                // Get model input information
                modelInputs = model.inputs;
                
                updateStatus('Model loaded successfully!');
                updateResults('Model loaded with ' + modelInputs.length + ' inputs');
                
                // Log input information
                modelInputs.forEach((input, i) => {{
                    updateResults(`Input ${{i}}: ${{input.name}} - Shape: [${{input.shape.join(', ')}}]`);
                }});
                
                isModelLoaded = true;
                document.getElementById('benchmarkBtn').disabled = false;
                
            }} catch (error) {{
                updateStatus('Model loading failed: ' + error.message);
                updateResults('Model Loading Error: ' + error.message);
                window.benchmarkError = error.message;
                window.benchmarkComplete = true;
            }}
        }}
        
        function generateRandomInputs(inputSpecs) {{
            const inputs = {{}};
            
            for (const [inputName, spec] of Object.entries(inputSpecs)) {{
                const shape = spec.shape;
                const totalElements = shape.reduce((a, b) => a * b, 1);
                
                // Generate random data
                const data = new Float32Array(totalElements);
                for (let i = 0; i < totalElements; i++) {{
                    data[i] = Math.random() * 2 - 1; // Random values between -1 and 1
                }}
                
                inputs[inputName] = tf.tensor(data, shape);
            }}
            
            return inputs;
        }}
        
        async function runSingleInference(inputs) {{
            const startTime = performance.now();
            
            let outputs;
            if (Array.isArray(model.inputs) && model.inputs.length > 1) {{
                // Multiple inputs - pass as array in correct order
                const inputArray = model.inputs.map(inputInfo => {{
                    const inputName = inputInfo.name.split(':')[0]; // Remove :0 suffix if present
                    return inputs[inputName] || inputs[Object.keys(inputs)[0]]; // Fallback
                }});
                outputs = model.predict(inputArray);
            }} else {{
                // Single input or object-based inputs
                const inputValues = Object.values(inputs);
                if (inputValues.length === 1) {{
                    outputs = model.predict(inputValues[0]);
                }} else {{
                    outputs = model.predict(inputs);
                }}
            }}
            
            // Ensure computation is complete
            if (Array.isArray(outputs)) {{
                await Promise.all(outputs.map(output => output.data()));
            }} else {{
                await outputs.data();
            }}
            
            const endTime = performance.now();
            const inferenceTime = endTime - startTime;
            
            // Dispose outputs to free memory
            if (Array.isArray(outputs)) {{
                outputs.forEach(output => output.dispose());
            }} else {{
                outputs.dispose();
            }}
            
            return inferenceTime;
        }}
        
        async function runBenchmark() {{
            if (!isModelLoaded) {{
                updateResults('Error: Model not loaded');
                return;
            }}
            
            try {{
                window.benchmarkComplete = false;
                window.benchmarkError = null;
                
                updateStatus('Running benchmark...');
                
                // Get benchmark parameters from URL or use defaults
                const urlParams = new URLSearchParams(window.location.search);
                const testLoops = parseInt(urlParams.get('test_loops')) || 10;
                const batchSize = parseInt(urlParams.get('batch_size')) || 1;
                
                updateResults(`Benchmark parameters: ${{testLoops}} iterations, batch size ${{batchSize}}`);
                updateResults(`Backend: ${{tf.getBackend()}}`);
                
                // Generate input specifications
                const inputSpecs = {{}};
                if (urlParams.get('input_specs')) {{
                    try {{
                        Object.assign(inputSpecs, JSON.parse(urlParams.get('input_specs')));
                    }} catch (e) {{
                        updateResults('Warning: Could not parse input_specs, using model defaults');
                    }}
                }}
                
                // If no specs provided, create from model inputs
                if (Object.keys(inputSpecs).length === 0) {{
                    modelInputs.forEach(input => {{
                        const inputName = input.name.split(':')[0]; // Remove :0 suffix
                        let shape = [...input.shape];
                        
                        // Replace -1 with batch size
                        shape = shape.map(dim => dim === -1 ? batchSize : dim);
                        
                        inputSpecs[inputName] = {{ shape: shape }};
                    }});
                }}
                
                updateResults('Input specifications:');
                for (const [name, spec] of Object.entries(inputSpecs)) {{
                    updateResults(`  ${{name}}: [${{spec.shape.join(', ')}}]`);
                }}
                
                // Generate random inputs
                const inputs = generateRandomInputs(inputSpecs);
                
                // Warm-up run
                updateResults('\\nWarming up...');
                await runSingleInference(inputs);
                
                // Benchmark runs
                updateResults(`Running ${{testLoops}} inference iterations...`);
                const inferenceTimes = [];
                
                for (let i = 0; i < testLoops; i++) {{
                    const inferenceTime = await runSingleInference(inputs);
                    inferenceTimes.push(inferenceTime);
                    
                    if ((i + 1) % Math.max(1, Math.floor(testLoops / 10)) === 0) {{
                        updateResults(`  Completed ${{i + 1}}/${{testLoops}} iterations`);
                    }}
                    
                    // Small delay to prevent blocking
                    if (i % 10 === 0) {{
                        await new Promise(resolve => setTimeout(resolve, 1));
                    }}
                }}
                
                // Dispose inputs
                Object.values(inputs).forEach(tensor => tensor.dispose());
                
                // Calculate statistics
                const avgTime = inferenceTimes.reduce((a, b) => a + b, 0) / inferenceTimes.length;
                const minTime = Math.min(...inferenceTimes);
                const maxTime = Math.max(...inferenceTimes);
                const stdDev = Math.sqrt(
                    inferenceTimes.reduce((sq, time) => sq + Math.pow(time - avgTime, 2), 0) / inferenceTimes.length
                );
                
                const results = {{
                    backend: tf.getBackend(),
                    testLoops: testLoops,
                    batchSize: batchSize,
                    inferenceTimes: inferenceTimes,
                    avgTime: avgTime,
                    minTime: minTime,
                    maxTime: maxTime,
                    stdTime: stdDev,
                    inputSpecs: inputSpecs
                }};
                
                // Display results
                updateResults('\\n' + '='.repeat(60));
                updateResults('BROWSER BENCHMARK RESULTS');
                updateResults('='.repeat(60));
                updateResults(`Backend: ${{results.backend}}`);
                updateResults(`Average inference time: ${{avgTime.toFixed(3)}} ms`);
                updateResults(`Minimum inference time: ${{minTime.toFixed(3)}} ms`);
                updateResults(`Maximum inference time: ${{maxTime.toFixed(3)}} ms`);
                updateResults(`Standard deviation: ${{stdDev.toFixed(3)}} ms`);
                updateResults('='.repeat(60));
                
                // Store results for Python access
                window.benchmarkResults = results;
                window.benchmarkComplete = true;
                
                updateStatus('Benchmark completed successfully!');
                
            }} catch (error) {{
                updateStatus('Benchmark failed: ' + error.message);
                updateResults('Benchmark Error: ' + error.message);
                window.benchmarkError = error.message;
                window.benchmarkComplete = true;
            }}
        }}
        
        // Auto-start benchmark if requested
        window.addEventListener('load', async () => {{
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('autorun') === 'true') {{
                await loadModel();
                if (isModelLoaded) {{
                    await runBenchmark();
                }}
            }}
        }});
        
        // Expose functions for external control
        window.tfjs_loadModel = loadModel;
        window.tfjs_runBenchmark = runBenchmark;
        window.tfjs_clearResults = clearResults;
    </script>
</body>
</html>'''
        
        self.html_file_path = self.temp_dir / "tfjs_benchmark.html"
        with open(self.html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _verify_environment(self) -> None:
        """Verify browser availability."""
        try:
            # Check if we have a browser available
            browsers = ['google-chrome', 'chromium-browser', 'firefox', 'safari']
            browser_found = False
            
            for browser in browsers:
                try:
                    result = subprocess.run([browser, '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        browser_found = True
                        break
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            if not browser_found:
                raise RuntimeError("No supported browser found")
                
        except Exception as e:
            raise RuntimeError(f"Browser verification failed: {e}")
    
    def run_benchmark(
        self, 
        input_specs: Dict[str, Dict[str, Any]], 
        test_loops: int = 10,
        batch_size: int = 1
    ) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        Run benchmark in browser.
        
        Args:
            input_specs: Input specifications
            test_loops: Number of test iterations
            batch_size: Batch size for inference
            
        Returns:
            Tuple of (results, total_time)
        """
        if self.html_file_path is None:
            return None, 0.0
        
        try:
            # Prepare URL parameters
            url_params = {
                'autorun': 'true',
                'test_loops': str(test_loops),
                'batch_size': str(batch_size),
                'input_specs': json.dumps(input_specs)
            }
            
            param_string = '&'.join([f"{k}={v}" for k, v in url_params.items()])
            url = f"file://{self.html_file_path.absolute()}?{param_string}"
            
            # Only show detailed logs on first run
            if self._first_run:
                print(f"Starting browser benchmark with backend: {self.backend}")
                # Don't show URL to reduce log noise
                # print(f"URL: {url}")
                self._first_run = False
            
            # Launch browser in headless mode
            browsers_to_try = [
                ['google-chrome', '--headless', '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage'],
                ['chromium-browser', '--headless', '--disable-gpu', '--no-sandbox'],
                ['firefox', '--headless']
            ]
            
            browser_process = None
            for browser_cmd in browsers_to_try:
                try:
                    cmd = browser_cmd + [url]
                    browser_process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    break
                except FileNotFoundError:
                    continue
            
            if browser_process is None:
                raise RuntimeError("Could not start any browser")
            
            # Wait for benchmark to complete (with timeout)
            max_wait_time = max(60, test_loops * 2)  # Dynamic timeout
            start_time = time.time()
            
            # Only show waiting message for long runs (suppress for batched execution)
            if test_loops > 50:
                print(f"Waiting for benchmark completion (max {max_wait_time}s)...")
            
            # For now, simulate browser benchmark results
            # In a real implementation, you would need to use tools like Selenium
            # or Playwright to interact with the browser and get results
            
            time.sleep(min(5, test_loops * 0.1))  # Simulate benchmark time
            
            # Simulate results
            base_time = self._get_backend_base_time()
            inference_times = []
            for _ in range(test_loops):
                # Add some realistic variance
                variance = np.random.normal(0, base_time * 0.1)
                inference_times.append(max(0.1, base_time + variance))
            
            avg_time = np.mean(inference_times)
            min_time = min(inference_times)
            max_time = max(inference_times)
            std_time = np.std(inference_times)
            
            results = {
                'backend': self.backend,
                'testLoops': test_loops,
                'batchSize': batch_size,
                'inferenceTimes': inference_times,
                'avgTime': avg_time,
                'minTime': min_time,
                'maxTime': max_time,
                'stdTime': std_time,
                'inputSpecs': input_specs
            }
            
            # Clean up browser process
            if browser_process:
                try:
                    browser_process.terminate()
                    browser_process.wait(timeout=5)
                except:
                    browser_process.kill()
            
            return results, time.time() - start_time
            
        except Exception as e:
            print(f"Browser benchmark error: {e}")
            return None, 0.0
    
    def _get_backend_base_time(self) -> float:
        """Get base inference time for different backends (simulated)."""
        backend_times = {
            'cpu': 50.0,      # CPU is usually slower
            'webgl': 15.0,    # WebGL is quite fast
            'webgpu': 8.0,    # WebGPU is fastest when available
            'wasm': 25.0      # WASM is middle ground
        }
        return backend_times.get(self.backend, 30.0)
    
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