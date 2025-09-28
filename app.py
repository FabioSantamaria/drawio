import os
import glob
import io

import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas

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

    # Initialize a counter for canvas key to allow clearing
    if "canvas_key_counter" not in st.session_state:
        st.session_state["canvas_key_counter"] = 0

    # Toolbar
    st.markdown("### Whiteboard")
    tool = st.radio("Tool", ["freedraw", "line", "rect", "circle", "point", "transform"], horizontal=True)
    stroke_color = st.color_picker("Stroke color", "#000000")
    bg_color = st.color_picker("Background color", "#FFFFFF")
    stroke_width = st.slider("Stroke width", 1, 30, 4)
    drawing_mode = tool
    point_display_radius = st.slider("Point display radius", 1, 25, 6) if drawing_mode == "point" else 0

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=600,
        width=1000,
        drawing_mode=drawing_mode,
        point_display_radius=point_display_radius,
        key=f"couple_canvas_{st.session_state['canvas_key_counter']}",
        display_toolbar=True,
    )

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Clear drawing"):
            st.session_state["canvas_key_counter"] += 1
            st.experimental_rerun()
    with col2:
        if canvas_result and canvas_result.image_data is not None:
            img = Image.fromarray(canvas_result.image_data.astype("uint8"))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button("Download drawing as PNG", data=buf.getvalue(), file_name="drawing.png", mime="image/png")
        else:
            st.info("Draw something to enable download.")
    with col3:
        if st.button("Reset selection and start over"):
            st.session_state.pop("selected_photo_path", None)
            st.experimental_rerun()

st.caption("Tip: Invite friends to guess the place over a video call or in person!")