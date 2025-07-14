#!/usr/bin/env python3
"""
Persistent server for AI Image Editor.
Uses HTTP/WebSocket to serve requests without restarting.
"""

import asyncio
import base64
import io
import json
import logging
import os
import signal
import sys
from typing import Dict, Any

import torch
import uvicorn
from diffusers import FluxKontextPipeline
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "./models/black-forest-labs/FLUX.1-Kontext-dev")
DEVICE = os.getenv("DEVICE", None)  # Auto-detect if None
TORCH_DTYPE = os.getenv("TORCH_DTYPE", "bfloat16")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8888"))

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global model instance
pipe = None
model_loaded = False

# FastAPI app
app = FastAPI(title="AI Image Editor Server", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class EditImageRequest(BaseModel):
    image_base64: str
    prompt: str
    guidance_scale: float = 2.5


class EditImageResponse(BaseModel):
    result: str


class ModelInfoResponse(BaseModel):
    model_name: str
    model_path: str
    device: str
    torch_dtype: str
    loaded: bool


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    ready: bool


def load_model():
    """Load the model synchronously."""
    global pipe, model_loaded
    
    if model_loaded:
        return
    
    try:
        logger.info("Loading FLUX model...")
        
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

        # Determine device
        device = DEVICE or ("cuda" if torch.cuda.is_available() else "cpu")

        # Load model
        dtype_map = {
            "bfloat16": torch.bfloat16,
            "float16": torch.float16,
            "float32": torch.float32,
        }
        torch_dtype = dtype_map.get(TORCH_DTYPE, torch.bfloat16)

        pipe = FluxKontextPipeline.from_pretrained(
            MODEL_PATH, torch_dtype=torch_dtype
        )
        pipe.to(device)

        model_loaded = True
        logger.info(f"✅ Model loaded successfully on {device}")

    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        raise


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    try:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        logger.error(f"Failed to convert image to base64: {e}")
        raise


def base64_to_image(base64_str: str) -> Image.Image:
    """Convert base64 string to PIL Image."""
    try:
        image_data = base64.b64decode(base64_str)
        return Image.open(io.BytesIO(image_data))
    except Exception as e:
        logger.error(f"Failed to convert base64 to image: {e}")
        raise ValueError("Invalid base64 image data")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the server is healthy and ready."""
    return HealthResponse(
        status="healthy",
        model_loaded=model_loaded,
        ready=model_loaded
    )


@app.get("/model_info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get information about the loaded model."""
    device = DEVICE or ("cuda" if torch.cuda.is_available() else "cpu")
    
    return ModelInfoResponse(
        model_name="FLUX.1-Kontext-dev",
        model_path=MODEL_PATH,
        device=device,
        torch_dtype=TORCH_DTYPE,
        loaded=model_loaded
    )


@app.post("/edit_image", response_model=EditImageResponse)
async def edit_image(request: EditImageRequest):
    """Edit an image based on a text prompt using FLUX Kontext model."""
    global pipe, model_loaded
    
    try:
        # Validation
        if not request.image_base64:
            raise HTTPException(status_code=400, detail="image_base64 cannot be empty")
        if not request.prompt:
            raise HTTPException(status_code=400, detail="prompt cannot be empty")
        if not (0.1 <= request.guidance_scale <= 10.0):
            raise HTTPException(status_code=400, detail="guidance_scale must be between 0.1 and 10.0")

        # Check if model is loaded
        if not model_loaded:
            raise HTTPException(status_code=503, detail="Model not loaded. Please restart the server.")

        # Process image
        input_image = base64_to_image(request.image_base64)
        
        logger.info(f"Processing image edit request: '{request.prompt}'")
        result = pipe(
            image=input_image,
            prompt=request.prompt,
            guidance_scale=request.guidance_scale
        )

        edited_image = result.images[0]
        result_base64 = image_to_base64(edited_image)
        
        return EditImageResponse(result=result_base64)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in edit_image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    logger.info("🚀 Server starting up...")
    try:
        load_model()
        logger.info("✅ Server ready!")
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        raise


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("Received shutdown signal, stopping server...")
    sys.exit(0)


def main():
    """Main entry point."""
    # Handle shutdown signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🎨 Starting Persistent AI Image Editor Server")
    logger.info(f"Model path: {MODEL_PATH}")
    logger.info(f"Device: {DEVICE or 'auto-detect'}")
    logger.info(f"Server will run on: http://{SERVER_HOST}:{SERVER_PORT}")
    
    # Run the server
    uvicorn.run(
        "server:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level=LOG_LEVEL.lower(),
        reload=False
    )


if __name__ == "__main__":
    main()