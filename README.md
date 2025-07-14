# AI Image Editor

A persistent AI image editing application using FLUX Kontext model with HTTP API architecture.

## Features

- 🎨 **AI-powered image editing** using FLUX.1-Kontext-dev model
- 🖥️ **Persistent server** - model stays loaded for fast responses  
- 🌐 **Modern Web UI** built with Streamlit
- ⚡ **HTTP API** for reliable communication
- 📱 **Responsive design** works on desktop, tablet, mobile

## Architecture

```
Step 1: Start Server          Step 2: Start WebUI
┌─────────────────┐           ┌─────────────────┐
│                 │    HTTP   │                 │
│ Persistent      │ ◄────────►│ Streamlit       │
│ HTTP Server     │  REST API │ WebUI           │
│                 │           │                 │
│ - Model Loaded  │           │ - User Interface│
│ - Stays Running │           │ - HTTP Client   │
│ - Fast Response │           │ - Real-time UI  │
└─────────────────┘           └─────────────────┘
```

## Quick Start

### Option 1: Automatic (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt

# Set model path (optional - defaults to ./models/)
export MODEL_PATH="./models/black-forest-labs/FLUX.1-Kontext-dev"

# Start both server and WebUI automatically
python launcher.py both
```

### Option 2: Manual (Two Steps)
```bash
# Step 1: Start the persistent server (Terminal 1)
python server.py

# Step 2: Start the WebUI (Terminal 2) 
streamlit run webui.py --server.port 30700
```

Access the WebUI at: `http://localhost:30700`

## Project Structure

```
├── server.py           # 🎯 Persistent HTTP server (FastAPI)
├── webui.py            # 🌐 Streamlit web interface  
├── launcher.py         # 🚀 Automated launcher
├── example.py          # Original FLUX usage example
├── requirements.txt    # Dependencies
└── models/             # Model storage directory
```

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download FLUX model:**
   ```bash
   # Create models directory
   mkdir -p models/black-forest-labs

   # Download FLUX.1-Kontext-dev model to ./models/black-forest-labs/FLUX.1-Kontext-dev/
   # Or set MODEL_PATH to your model location
   export MODEL_PATH="/path/to/your/FLUX.1-Kontext-dev"
   ```

3. **Launch:**
   ```bash
   python launcher.py both
   ```

## Usage

### Web Interface
1. **Start system:** `python launcher.py both`
2. **Upload image** in the WebUI
3. **Enter editing prompt** (e.g., "add sunglasses", "change to winter scene")
4. **Click "Edit Image"** (fast response after initial model load)
5. **Download result**

### Command Line
```bash
# Check system status
python launcher.py check

# Check server status  
python launcher.py status

# Start only server
python launcher.py server

# Start only WebUI (server must be running)
python launcher.py webui

# Start both automatically
python launcher.py both
```

## Configuration

Configure via environment variables:

```bash
# Model configuration
export MODEL_PATH="./models/black-forest-labs/FLUX.1-Kontext-dev"
export DEVICE="cuda"           # or "cpu" for CPU-only
export TORCH_DTYPE="bfloat16"  # or "float16", "float32"
export LOG_LEVEL="INFO"        # or "DEBUG", "WARNING", "ERROR"

# Server configuration  
export SERVER_HOST="0.0.0.0"  # Server bind address
export SERVER_PORT="8888"     # Server port
```

## API Reference

### HTTP Endpoints

#### `GET /health`
Check if server is healthy and model is loaded.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "ready": true
}
```

#### `GET /model_info`
Get information about the loaded model.

**Response:**
```json
{
  "model_name": "FLUX.1-Kontext-dev",
  "model_path": "./models/black-forest-labs/FLUX.1-Kontext-dev",
  "device": "cuda",
  "torch_dtype": "bfloat16",
  "loaded": true
}
```

#### `POST /edit_image`
Edit an image based on a text prompt.

**Request:**
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAA...",
  "prompt": "add sunglasses to the person",
  "guidance_scale": 2.5
}
```

**Response:**
```json
{
  "result": "iVBORw0KGgoAAAANSUhEUgAAA..."
}
```

## Benefits of Persistent Architecture

### ✅ **Fast Response Times**
- Model loads **once** when server starts
- Subsequent requests are **fast** (seconds, not minutes)
- Server stays running with model in memory

### ✅ **Reliable Operation**
- **Persistent server** doesn't restart between requests
- **Clear separation** of concerns (server vs UI)
- **Easy debugging** - can restart WebUI without reloading model

### ✅ **Resource Efficient**
- Model loaded **once** and reused
- No repeated loading overhead
- Better GPU memory management

### ✅ **Scalable**
- Multiple clients can connect to same server
- HTTP API allows integration with other applications
- Server can run on different machine than UI

## Troubleshooting

### Common Issues

1. **Server won't start:**
   ```bash
   # Check dependencies and model
   python launcher.py check
   
   # Check specific error
   python server.py
   ```

2. **WebUI can't connect:**
   ```bash
   # Check server status
   python launcher.py status
   
   # Make sure server is running first
   python server.py
   ```

3. **Out of memory:**
   ```bash
   # Use CPU instead of GPU
   export DEVICE=cpu
   export TORCH_DTYPE=float32
   ```

4. **Model not found:**
   ```bash
   # Check model path
   export MODEL_PATH="/correct/path/to/FLUX.1-Kontext-dev"
   python launcher.py check
   ```

### Performance Tips

- **Start server once** and keep it running
- **WebUI can restart** without affecting server
- Use **CUDA GPU** for best performance (if available)
- Monitor **GPU memory** usage with `nvidia-smi`
- Use **bfloat16** for optimal GPU memory usage

## Development Workflow

```bash
# Development setup
python launcher.py check          # Verify setup

# Start development
python server.py                  # Terminal 1: Keep server running
streamlit run webui.py           # Terminal 2: Develop WebUI

# Production
python launcher.py both           # Single command for everything
```

## System Requirements

- **Python 3.8+**
- **8GB+ RAM** (16GB+ recommended)
- **CUDA GPU** (optional but recommended for speed)
- **10GB+ disk space** for model files

This architecture provides fast, reliable AI image editing with a simple setup process!