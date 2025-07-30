import streamlit as st
from pathlib import Path

def show_config(root_dir: str):
    st.header("⚙️ Config Editor")
    config_path = Path(root_dir) / ".streamlit" / "config.toml"
    if config_path.exists():
        content = config_path.read_text(encoding="utf-8")
        updated = st.text_area("Edit config.toml", content, height=300)
        if st.button("💾 Save Config"):
            try:
                config_path.write_text(updated, encoding="utf-8")
                st.success("Config updated.")
            except Exception as e:
                st.error(f"Failed to save: {e}")
    else:
        st.warning("No config.toml found.")