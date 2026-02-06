import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="Pro Alpha Tool", layout="wide")

st.title("🧪 Pro Color-to-Alpha")
st.markdown("Remove backgrounds with **Choke** and **Feather** controls for Unity-ready assets.")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Settings")
    
    # 1. Color Picker
    target_color = st.color_picker("Key Color", "#00FF00")
    
    # 2. Tolerance
    tolerance = st.slider("Tolerance (Sensitivity)", 0, 100, 40, help="How exact the color match must be.")
    
    st.divider() # Visual separator
    
    # 3. Choke (Erosion)
    st.markdown("**Edge Cleanup**")
    choke = st.slider("Choke (Shrink Edge)", 0, 10, 1, help="Cuts into the subject to remove green halos.")
    
    # 4. Feather (Blur)
    feather = st.slider("Feather (Soften Edge)", 0, 10, 1, help="Blurs the transparency mask for smooth blending.")

# --- MAIN LOGIC ---
uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"])

if uploaded_file:
    # 1. Convert Upload to OpenCV format
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # 2. Process Target Color (Hex to BGR)
    hex_val = target_color.lstrip('#')
    rgb = tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))
    target_bgr = np.array([rgb[2], rgb[1], rgb[0]])

    # 3. Create Base Mask
    # Calculate color distance
    diff = np.sqrt(np.sum((img - target_bgr)**2, axis=2))
    # Create binary mask (0=Transparent, 255=Opaque)
    base_mask = np.where(diff < tolerance, 0, 255).astype(np.uint8)

    # 4. Apply Choke (Erosion)
    if choke > 0:
        kernel_size = 2 * choke + 1
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        base_mask = cv2.erode(base_mask, kernel, iterations=1)

    # 5. Apply Feather (Gaussian Blur)
    if feather > 0:
        # Convert to float for precise blurring
        mask_float = base_mask.astype(np.float32)
        blur_size = 2 * feather + 1
        mask_float = cv2.GaussianBlur(mask_float, (blur_size, blur_size), 0)
        # Clip back to valid range
        final_mask = np.clip(mask_float, 0, 255).astype(np.uint8)
    else:
        final_mask = base_mask

    # 6. Merge Channels
    b, g, r = cv2.split(img)
    rgba = cv2.merge([b, g, r, final_mask])

    # --- DISPLAY & DOWNLOAD ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original")
        st.image(uploaded_file, use_container_width=True)
        
    with col2:
        st.subheader("Result")
        # Convert back to PIL for Streamlit display
        result_pil = Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA))
        # Create a checkerboard background for previewing transparency? 
        # Streamlit handles alpha display natively, so it usually looks dark/black or white.
        st.image(result_pil, use_container_width=True)

    # Download Button
    buf = io.BytesIO()
    result_pil.save(buf, format="PNG")
    st.download_button(
        label="Download PNG",
        data=buf.getvalue(),
        file_name="processed_asset.png",
        mime="image/png",
        type="primary"
    )