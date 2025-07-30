import streamlit as st
from pathlib import Path
from streamlit_ace import st_ace

def show_editor(root_dir: str):
    st.header("📝 File Editor")
    py_files = list(Path(root_dir).rglob("*.py"))
    if not py_files:
        st.warning("No Python files found.")
        return

    selected = st.selectbox("Choose file to edit", py_files)
    code = selected.read_text(encoding='utf-8')
    updated_code = st_ace(value=code, language='python', theme='monokai', height=600, key=str(selected))

    if st.button("💾 Save Changes"):
        try:
            selected.write_text(updated_code, encoding='utf-8')
            st.success("File saved.")
        except Exception as e:
            st.error(f"Failed to save: {e}")