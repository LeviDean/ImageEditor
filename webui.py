"""
Streamlit WebUI for AI Image Editor.
Connects to the persistent HTTP server (no new processes).
"""

import asyncio
import base64
import io
import logging
import requests
import time
from pathlib import Path

import streamlit as st
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersistentWebUI:
    """WebUI that connects to persistent HTTP server."""

    def __init__(self, server_url: str = "http://localhost:8888"):
        self.server_url = server_url.rstrip('/')

    def check_server_health(self):
        """Check if the server is healthy and ready."""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return None

    def edit_image(self, image: Image.Image, prompt: str, guidance_scale: float):
        """Edit image using the persistent HTTP server."""
        try:
            # Convert image to base64
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Send request to server
            payload = {
                "image_base64": image_base64,
                "prompt": prompt,
                "guidance_scale": guidance_scale
            }
            
            response = requests.post(
                f"{self.server_url}/edit_image",
                json=payload,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                result_base64 = result["result"]
                
                # Convert back to image
                image_data = base64.b64decode(result_base64)
                return Image.open(io.BytesIO(image_data))
            else:
                error_msg = response.json().get("detail", "Unknown error")
                raise Exception(f"Server error: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error editing image: {e}")
            raise

    def get_server_info(self):
        """Get server information."""
        try:
            response = requests.get(f"{self.server_url}/model_info", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting server info: {e}")
            return None

    def run(self):
        """Main WebUI application."""
        st.set_page_config(
            page_title="AI Image Editor",
            page_icon="🎨",
            layout="wide"
        )

        # Initialize session state
        if 'original_image' not in st.session_state:
            st.session_state.original_image = None
        if 'edited_image' not in st.session_state:
            st.session_state.edited_image = None
        if 'is_processing' not in st.session_state:
            st.session_state.is_processing = False

        # Header
        st.title("🎨 AI Image Editor")
        st.write("Upload an image and describe how you want to edit it!")

        # Server status banner
        health = self.check_server_health()
        if health and health.get("ready"):
            st.success(f"✅ Server is ready and model is loaded")
        else:
            st.error("❌ Server not ready. Make sure to start: `python server.py`")
            st.stop()

        # Sidebar
        with st.sidebar:
            st.header("🖥️ Server Info")
            
            # Real-time server status
            if st.button("🔄 Refresh Status"):
                st.rerun()
            
            if health:
                st.json(health)
            
            st.divider()
            
            st.header("⚙️ Settings")
            
            guidance_scale = st.slider(
                "Guidance Scale",
                min_value=0.1,
                max_value=10.0,
                value=2.5,
                step=0.1,
                help="Higher values follow the prompt more closely"
            )
            
            # Model info
            if st.button("📊 Model Info"):
                info = self.get_server_info()
                if info:
                    st.json(info)
                else:
                    st.error("Could not get model info")
            
            st.divider()
            
            # Instructions
            st.subheader("📖 Instructions")
            st.markdown("""
            **Setup:**
            1. Start server: `python server.py`
            2. Wait for "Server ready" message
            3. Use this WebUI
            
            **Benefits:**
            - ⚡ **Fast responses** (model stays loaded)
            - 🔄 **No reloading** between requests
            - 📊 **Real-time status** monitoring
            """)

        # Main content
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📤 Upload Image")
            
            uploaded_file = st.file_uploader(
                "Choose an image file",
                type=['png', 'jpg', 'jpeg', 'webp']
            )
            
            if uploaded_file is not None:
                st.session_state.original_image = Image.open(uploaded_file)
                st.image(
                    st.session_state.original_image,
                    caption="Original Image",
                    use_container_width=True
                )

        with col2:
            st.subheader("✨ Edit Image")
            
            if st.session_state.original_image is not None:
                prompt = st.text_area(
                    "Editing Prompt",
                    placeholder="Describe what you want to change...",
                    height=100
                )
                
                if st.button("🎨 Edit Image", disabled=st.session_state.is_processing):
                    if prompt.strip():
                        st.session_state.is_processing = True
                        
                        with st.spinner("🔄 Processing your image... This should be fast!"):
                            try:
                                edited_image = self.edit_image(
                                    st.session_state.original_image,
                                    prompt,
                                    guidance_scale
                                )
                                
                                if edited_image:
                                    st.session_state.edited_image = edited_image
                                    st.success("✅ Image edited successfully!")
                                    st.rerun()
                                    
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                            finally:
                                st.session_state.is_processing = False
                    else:
                        st.warning("⚠️ Please enter a prompt")
            else:
                st.info("👆 Please upload an image first")

        # Results
        if st.session_state.edited_image is not None:
            st.divider()
            st.subheader("📥 Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Original**")
                st.image(st.session_state.original_image, use_container_width=True)
            
            with col2:
                st.markdown("**Edited**")
                st.image(st.session_state.edited_image, use_container_width=True)
            
            # Download
            img_buffer = io.BytesIO()
            st.session_state.edited_image.save(img_buffer, format='PNG')
            
            st.download_button(
                label="📥 Download Edited Image",
                data=img_buffer.getvalue(),
                file_name="edited_image.png",
                mime="image/png"
            )

        # Footer
        st.divider()
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>🎨 AI Image Editor with Persistent Server</p>
            <p>⚡ Model stays loaded for fast responses!</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    app = PersistentWebUI()
    app.run()