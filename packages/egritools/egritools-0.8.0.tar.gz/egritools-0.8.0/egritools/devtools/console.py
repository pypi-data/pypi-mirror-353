import streamlit as st
from pathlib import Path
from .file_editor import show_editor
from .log_viewer import show_logs
from .config_editor import show_config
from .sandbox import run_sandbox


def dev_console(
    root_dir: str = ".",
    tools=("Editor", "Logs", "Config", "Sandbox"),
    sidebar_only: bool = True
):
    location = st.sidebar if sidebar_only else st

    location.markdown("## 🛠️ Dev Console")
    selected = location.radio("Tool", tools, key="dev_tool_selection")

    if selected == "Editor":
        show_editor(root_dir)
    elif selected == "Logs":
        show_logs(root_dir)
    elif selected == "Config":
        show_config(root_dir)
    elif selected == "Sandbox":
        run_sandbox()