import os
import glob
import io
import base64

import streamlit as st
from PIL import Image
from whiteboard_excalidraw import excalidraw_canvas

APP_TITLE = "Couple's Place Guess — Drawing Game"
UPLOAD_DIR = "uploads"

st.set_page_config(page_title=APP_TITLE, page_icon="🎨", layout="wide")
st.title(APP_TITLE)

# Sidebar: Instructions
with st.sidebar:
    st.header("How it works")
    st.markdown(
        """
        1. Upload a few photos from places you've been together.\n
        2. Pick one to draw. The photo will then be hidden.\n
        3. Draw on the whiteboard while your partner guesses the place!\n
        Pro tip: Use colors, undo, and eraser to refine your drawing.
        """
    )
    st.markdown("— Made for couples 💑")

# Ensure upload directory exists (temporary)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Photo upload section
st.subheader("Step 1 — Upload your photos")
uploaded_files = st.file_uploader(
    "Upload images (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

if uploaded_files:
    for f in uploaded_files:
        # Save to temporary folder
        bytes_data = f.read()
        file_path = os.path.join(UPLOAD_DIR, f.name)
        with open(file_path, "wb") as out:
            out.write(bytes_data)

# Discover available photos
image_paths = sorted(
    glob.glob(os.path.join(UPLOAD_DIR, "*.jpg"))
    + glob.glob(os.path.join(UPLOAD_DIR, "*.jpeg"))
    + glob.glob(os.path.join(UPLOAD_DIR, "*.png"))
)

# Preview & select section
st.subheader("Step 2 — Preview and choose a photo to draw")
if len(image_paths) == 0:
    st.info("No images found yet. Upload some to get started!")
else:
    cols = st.columns(3)
    for i, p in enumerate(image_paths):
        with cols[i % 3]:
            img = Image.open(p)
            st.image(img, use_column_width=True)
            if st.button(f"Select this photo", key=f"select_{i}"):
                st.session_state["selected_photo_path"] = p

# Drawing section
st.subheader("Step 3 — Draw while your partner guesses")
selected_path = st.session_state.get("selected_photo_path")
if not selected_path:
    st.info("Select a photo above to start drawing.")
else:
    # Hide photo preview, but allow optional peek
    with st.expander("Optional: Peek the selected photo (cheat mode)"):
        st.image(Image.open(selected_path), caption="Selected photo", use_column_width=True)

    # Initialize export trigger for Excalidraw component
    if "wb_export" not in st.session_state:
        st.session_state["wb_export"] = False

    # Toolbar
    st.markdown("### Whiteboard")
    st.caption("Excalidraw canvas: use built-in tools; click Export below to capture PNG.")
    result = excalidraw_canvas(
        width=900,
        height=520,
        read_only=False,
        theme="light",
        export=st.session_state["wb_export"],
        key="excalidraw_canvas",
    )

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Export drawing"):
            st.session_state["wb_export"] = True
            st.experimental_rerun()
    with col2:
        data_url = result.get("dataUrl") if isinstance(result, dict) else None
        if data_url:
            try:
                payload = data_url.split(",", 1)[1]
                png_bytes = base64.b64decode(payload)
                st.download_button("Download drawing as PNG", data=png_bytes, file_name="drawing.png", mime="image/png")
            except Exception as e:
                st.error(f"Failed to decode image: {e}")
        else:
            st.info("Click Export to send the image from the canvas, then download.")
    with col3:
        if st.button("Reset selection and start over"):
            st.session_state.pop("selected_photo_path", None)
            st.experimental_rerun()

    # Reset export flag after one-shot
    if st.session_state.get("wb_export"):
        st.session_state["wb_export"] = False

st.caption("Tip: Invite friends to guess the place over a video call or in person!")