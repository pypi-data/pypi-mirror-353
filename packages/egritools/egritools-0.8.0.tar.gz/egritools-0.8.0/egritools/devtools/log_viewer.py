import streamlit as st
from pathlib import Path

def show_logs(root_dir: str):
    st.header("📜 Logs Viewer")
    log_path = Path(root_dir) / "logs" / "app.log"
    if log_path.exists():
        st.download_button("📥 Download Log", log_path.read_bytes(), file_name="app.log")
        st.code(log_path.read_text(encoding="utf-8"), language="bash")
    else:
        st.warning("No log file found at logs/app.log")