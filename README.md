# AI Image Editor

A simple AI image editing application using FLUX Kontext model with FastMCP architecture.

## Features

- 🎨 **AI-powered image editing** using FLUX.1-Kontext-dev model
- 🖥️ **Persistent server** - model stays loaded for fast responses
- 🌐 **Modern Web UI** built with Streamlit
- ⚡ **FastMCP integration** for reliable communication
- 📱 **Responsive design** works on desktop, tablet, mobile

## Architecture

```
Step 1: Start Server          Step 2: Start WebUI
┌─────────────────┐           ┌─────────────────┐
│                 │  FastMCP  │                 │
│ Persistent      │ ◄────────►│ Streamlit       │
│ MCP Server      │  (STDIO)  │ WebUI           │
│                 │           │                 │
│ - Model Loaded  │           │ - User Interface│
│ - Stays Running │           │ - Connects to   │
│ - Fast Response │           │   Server        │
└─────────────────┘           └─────────────────┘
```

## Quick Start

### Option 1: Automatic (Recommended)
```bash
# Set model path
export MODEL_PATH="/path/to/models/black-forest-labs/FLUX.1-Kontext-dev"

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
├── server.py           # 🎯 Persistent FastMCP server
├── webui.py            # 🌐 Streamlit web interface  
├── launcher.py         # 🚀 Automated launcher
├── simple_server.py    # (Legacy - single request)
├── simple_webui.py     # (Legacy - single request)
├── example.py          # Original FLUX usage
└── examples/
    └── simple_example.py # Programmatic usage
```

## Usage

### Web Interface
1. **Start server:** `python server.py` (wait for "Server ready")
2. **Start WebUI:** `streamlit run webui.py --server.port 30700`
3. **Upload image** and enter prompt
4. **Click "Edit Image"** (fast response after server is loaded)
5. **Download result**

### Command Line
```bash
# Check everything is ready
python launcher.py check

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
export MODEL_PATH="/path/to/FLUX.1-Kontext-dev"
export DEVICE="cuda"  # or "cpu"
export TORCH_DTYPE="bfloat16"  # or "float16", "float32"
export LOG_LEVEL="INFO"
```

## Benefits of Two-Step Architecture

### ✅ **Fast Response Times**
- Model loads **once** when server starts
- Subsequent requests are **fast** (seconds, not minutes)
- Server stays running with model in memory

### ✅ **Reliable Operation**
- **Persistent server** doesn't restart between requests
- **Clear separation** of concerns
- **Easy debugging** - can restart WebUI without reloading model

### ✅ **Resource Efficient**
- Model loaded **once** and reused
- No repeated loading overhead
- Better GPU memory management

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set model path:**
   ```bash
   export MODEL_PATH="/path/to/FLUX.1-Kontext-dev"
   ```

3. **Launch:**
   ```bash
   python launcher.py both
   ```

## API Reference

### FastMCP Tools

#### `edit_image`
Edit an image based on a text prompt.

**Parameters:**
- `image_base64` (string): Base64 encoded input image
- `prompt` (string): Description of the edit to make
- `guidance_scale` (number, optional): Guidance scale (0.1-10.0, default: 2.5)

**Returns:**
- Base64 encoded edited image

#### `get_model_info`
Get information about the loaded model.

#### `health_check`
Check if server is healthy and model is loaded.

## Troubleshooting

### Common Issues

1. **Server won't start:**
   ```bash
   # Check model path
   python launcher.py check
   ```

2. **WebUI can't connect:**
   ```bash
   # Make sure server is running first
   python server.py
   ```

3. **Out of memory:**
   ```bash
   export DEVICE=cpu
   export TORCH_DTYPE=float32
   ```

### Performance Tips

- **Start server once** and keep it running
- **WebUI can restart** without affecting server
- Use **CUDA GPU** for best performance
- Monitor **GPU memory** usage

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

This architecture provides the best of both worlds: fast response times with a simple, reliable setup!