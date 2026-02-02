import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="Alpha Channel Generator", layout="centered")

st.title("🖼️ Color to Alpha Converter")
st.write("Upload an image and select a color to turn transparent.")

# 1. Sidebar Controls
with st.sidebar:
    st.header("Settings")
    target_color = st.color_picker("Color to remove", "#00FF00")
    tolerance = st.slider("Tolerance", 1, 100, 30)
    
    # Convert hex to BGR (OpenCV format)
    hex_color = target_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    target_bgr = np.array([rgb[2], rgb[1], rgb[0]])

# 2. File Uploader
uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Convert uploaded file to OpenCV format
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    # Create the Alpha Mask
    # Calculate distance from target color
    diff = np.sqrt(np.sum((img - target_bgr)**2, axis=2))
    
    # Create a mask: 0 where color matches (transparent), 255 elsewhere (opaque)
    mask = np.where(diff < tolerance, 0, 255).astype(np.uint8)
    
    # Add alpha channel to image
    b, g, r = cv2.split(img)
    rgba = cv2.merge([b, g, r, mask])
    
    # Display results
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file, caption="Original")
    with col2:
        # Convert to PIL for Streamlit display
        result_img = Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA))
        st.image(result_img, caption="Result (Alpha Applied)")

    # 3. Download Button
    buf = io.BytesIO()
    result_img.save(buf, format="PNG")
    st.download_button(
        label="Download PNG with Alpha",
        data=buf.getvalue(),
        file_name="alpha_result.png",
        mime="image/png"
    )