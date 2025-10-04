import os
import streamlit.components.v1 as components

_component = None


def _declare():
    global _component
    if _component is None:
        build_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')
        _component = components.declare_component(
            'konva_canvas', path=build_dir
        )
    return _component


def konva_canvas(width: int = 900, height: int = 520, color: str = '#000000', stroke_width: int = 4, clear: bool = False, key: str | None = None):
    """
    Streamlit wrapper for the React + Konva drawing component.

    Returns a dict like { 'dataUrl': <png_data_url_or_none>, 'linesCount': <int> } when user clicks Export.
    """
    component = _declare()
    result = component(
        width=width,
        height=height,
        color=color,
        strokeWidth=stroke_width,
        clear=clear,
        key=key,
    )
    return result