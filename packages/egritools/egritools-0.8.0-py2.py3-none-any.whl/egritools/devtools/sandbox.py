import streamlit as st

def run_sandbox():
    st.header("🧪 Sandbox")

    st.markdown("Use this to test snippets live during dev.")
    user_code = st.text_area("Enter Python code:", height=200, key="sandbox_code")

    if st.button("Run Code"):
        with st.expander("Output"):
            try:
                local_vars = {}
                exec(user_code, {}, local_vars)
                for var, val in local_vars.items():
                    st.write(f"`{var}` =", val)
            except Exception as e:
                st.error(f"Execution failed: {e}")