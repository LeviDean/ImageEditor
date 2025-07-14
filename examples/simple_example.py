"""
Simple example of using the AI Image Editor programmatically.
"""

import asyncio
import base64
import io
import logging
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def edit_image_example():
    """Example of editing an image using FastMCP."""
    
    # Connect to server
    server_params = StdioServerParameters(
        command="python",
        args=["simple_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        session = ClientSession(read, write)
        await session.initialize()
        
        print("✅ Connected to FastMCP server")
        
        # Get model info
        result = await session.call_tool("get_model_info", {})
        model_info = result.content[0].text
        print(f"📊 Model info: {model_info}")
        
        # Edit an image (if it exists)
        image_path = "cat.png"
        if Path(image_path).exists():
            print(f"\n🎨 Editing image: {image_path}")
            
            # Convert image to base64
            with open(image_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode()
            
            # Edit the image
            result = await session.call_tool("edit_image", {
                "image_base64": image_base64,
                "prompt": "Add a stylish hat to the cat",
                "guidance_scale": 2.5
            })
            
            # Save the result
            result_base64 = result.content[0].text
            image_data = base64.b64decode(result_base64)
            edited_image = Image.open(io.BytesIO(image_data))
            
            output_path = "cat_edited.png"
            edited_image.save(output_path)
            print(f"✅ Edited image saved to: {output_path}")
            
        else:
            print(f"⚠️ Example image not found: {image_path}")
            print("Place a cat.png file in the root directory to try image editing")


if __name__ == "__main__":
    asyncio.run(edit_image_example())