from streamlit_ace import st_ace
from pathlib import Path
import streamlit as st

def inject_self_editor(script_path: str = __file__, tab_title: str = "Edit This Script"):
    """Injects a Streamlit tab or section that allows live editing of the script at `script_path`."""

    this_file = Path(script_path)

    st.header(f"🛠️ {tab_title}")
    st.markdown("Edit the file you're running directly. Changes apply on reload!")

    # Try to read script
    try:
        code = this_file.read_text(encoding='utf-8')
    except Exception as e:
        st.error(f"Could not read the script: {e}")
        return

    # Code editor
    updated_code = st_ace(
        value=code,
        language='python',
        theme='monokai',
        height=600,
        key=f"editor_{this_file.name}"
    )

    if st.button("💾 Save Changes"):
        try:
            this_file.write_text(updated_code, encoding='utf-8')
            st.success("Script saved! Refresh to apply changes.")
        except Exception as e:
            st.error(f"Failed to save: {e}")
