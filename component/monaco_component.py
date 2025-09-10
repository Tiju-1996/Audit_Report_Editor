import os
import streamlit as st
import streamlit.components.v1 as components
from typing import Optional

# Toggle this to True when releasing the component (serving from build folder)
_RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "monaco_component",
        path=os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"),
    )
else:
    _component_func = components.declare_component("monaco_component")

def monaco_editor(value: str = "", key: Optional[str] = None, language: str = "markdown", theme: str = "vs-light"):
    """Embed the built Monaco component.

    Returns a dict with:
      - value: the full editor text
      - selection: { startLine, startColumn, endLine, endColumn, startIndex, endIndex }
    """
    component_value = _component_func(value=value, language=language, theme=theme, key=key)
    return component_value
