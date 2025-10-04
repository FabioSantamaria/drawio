from pathlib import Path
import typing as t
import streamlit.components.v1 as components

_frontend_dir = Path(__file__).parent / "frontend" / "dist"

_component_func = components.declare_component(
    "whiteboard_excalidraw",
    path=str(_frontend_dir),
)


def excalidraw_canvas(
    width: int = 900,
    height: int = 520,
    read_only: bool = False,
    theme: str = "light",
    initial_data: t.Optional[dict] = None,
    export: bool = False,
    key: t.Optional[str] = None,
):
    return _component_func(
        width=width,
        height=height,
        readOnly=read_only,
        theme=theme,
        initialData=initial_data or {},
        exportRequested=export,
        key=key,
        default={},
    )