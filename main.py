from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import Response
import cv2
import numpy as np

app = FastAPI()

@app.post("/process-image")
async def process_image(
    image: UploadFile = File(...),
    hex_color: str = Form("#00FF00"),
    tolerance: int = Form(30),
    choke_pixels: int = Form(0),   # New: Shrinks the mask to remove halos
    feather_pixels: int = Form(0)  # New: Softens the edges
):
    # 1. Read and Decode Image
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 2. Process Target Color
    hex_val = hex_color.lstrip('#')
    rgb = tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))
    target_bgr = np.array([rgb[2], rgb[1], rgb[0]])

    # 3. Create Initial Alpha Mask
    # Calculate difference from target color
    diff = np.sqrt(np.sum((img - target_bgr)**2, axis=2))
    # Create binary mask: 255 = Subject (Keep), 0 = Background (Remove)
    mask = np.where(diff < tolerance, 0, 255).astype(np.uint8)

    # --- ADVANCED PROCESSING ---

    # 4. Apply Choke (Erosion)
    # Shrinks the white area (subject) to cut off green edges
    if choke_pixels > 0:
        kernel_size = 2 * choke_pixels + 1
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)

    # 5. Apply Feather (Gaussian Blur)
    # Softens the transition between opaque and transparent
    if feather_pixels > 0:
        # Convert to float to allow smooth gradients
        mask = mask.astype(np.float32)
        # Sigma is calculated from pixels roughly (sigma = x * 0.3 + 0.8) or just let OpenCV calc it
        blur_size = 2 * feather_pixels + 1
        mask = cv2.GaussianBlur(mask, (blur_size, blur_size), 0)
        # Normalize back to 0-255 range if needed, but OpenCV handles float masks well usually.
        # For strict PNG compliance, let's cast back carefully
        mask = np.clip(mask, 0, 255).astype(np.uint8)

    # ---------------------------

    # 6. Merge & Encode
    b, g, r = cv2.split(img)
    # If using feather, the mask is now grayscale (0-255), creating semi-transparency
    rgba = cv2.merge([b, g, r, mask])

    _, encoded_img = cv2.imencode('.png', rgba)
    return Response(content=encoded_img.tobytes(), media_type="image/png")