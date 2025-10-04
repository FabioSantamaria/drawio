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

# Track which uploaded filenames we've already saved to disk to avoid re-saving
if "saved_upload_names" not in st.session_state:
    st.session_state["saved_upload_names"] = []

def _on_upload_change():
    # When the selection changes, allow saving new files again
    st.session_state["saved_upload_names"] = []

uploaded_files = st.file_uploader(
    "Upload images (JPG/PNG)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    key="photo_uploads",
    on_change=_on_upload_change,
)

if uploaded_files:
    for f in uploaded_files:
        name = f.name
        file_path = os.path.join(UPLOAD_DIR, name)
        # Only save once per selection to prevent re-adding removed images on reruns
        if name not in st.session_state["saved_upload_names"]:
            if not os.path.exists(file_path):
                bytes_data = f.read()
                with open(file_path, "wb") as out:
                    out.write(bytes_data)
            st.session_state["saved_upload_names"].append(name)

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
            # Safely load image into memory so the file isn't locked (Windows)
            try:
                with Image.open(p) as im:
                    img = im.copy()
            except Exception:
                img = None

            if img is not None:
                st.image(img, use_column_width=True)
            else:
                st.warning("Could not preview this image.")

            btn_select, btn_remove = st.columns(2)
            with btn_select:
                if st.button("Select this photo", key=f"select_{i}"):
                    st.session_state["selected_photo_path"] = p
            with btn_remove:
                if st.button("Remove photo", type="secondary", key=f"remove_{i}"):
                    delete_ok = False
                    try:
                        # If currently selected, clear selection
                        if st.session_state.get("selected_photo_path") == p:
                            st.session_state.pop("selected_photo_path", None)
                        os.remove(p)
                        # Prevent the uploader from re-creating this file on rerun
                        base = os.path.basename(p)
                        if base not in st.session_state["saved_upload_names"]:
                            st.session_state["saved_upload_names"].append(base)
                        delete_ok = True
                    except Exception as e:
                        st.error(f"Failed to remove photo: {e}")

                    # Trigger rerun AFTER the try/except so we don't catch the rerun
                    if delete_ok:
                        st.success("Photo removed.")
                        st.rerun()

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

    st.info("Click Export to send the image from the canvas, then download.")

    # Reset export flag after one-shot
    if st.session_state.get("wb_export"):
        st.session_state["wb_export"] = False

st.caption("Tip: Invite friends to guess the place over a video call or in person!")