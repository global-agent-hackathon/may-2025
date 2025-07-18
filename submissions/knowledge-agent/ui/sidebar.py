import json
import streamlit as st
from streamlit_local_storage import LocalStorage
from agents import DEFAULT_MODEL_ID, DEFAULT_BASE_URL


def render_sidebar():
    """Sidebar that persists settings in browser localStorage."""
    ls = LocalStorage()

    # ---------- read previous settings (if any) -----------------
    saved_raw = ls.getItem("knowledge_agent_settings")
    saved = json.loads(saved_raw) if saved_raw else {}

    with st.sidebar:
        st.markdown("## Configuration")

        api_key = st.text_input(
            "🔑 OpenAI API Key",
            value=saved.get("api_key", ""),
            type="password",
            help="Kept only in this browser."
        )

        base_url = st.text_input(
            "🌐 Base URL (optional)",
            value=saved.get("base_url", DEFAULT_BASE_URL),
        )

        model_id = st.text_input(
            "🤖 Model ID (optional)",
            value=saved.get("model_id", DEFAULT_MODEL_ID),
        )

        # ---------- action buttons --------------------------------
        if st.button("💾 Save settings", use_container_width=True):
            new_blob = json.dumps({
                "api_key":  api_key,
                "base_url": base_url,
                "model_id": model_id,
            })
            ls.setItem("knowledge_agent_settings", new_blob)
            st.toast("Settings saved locally!")

        if st.button("🗑️ Clear settings", use_container_width=True,
                     type="secondary"):
            ls.deleteAll()                     # wipe everything
            st.toast("Local settings cleared.")
            api_key = base_url = model_id = "" # update returns

        # ---------- helper text -----------------------------------
        st.markdown("---")
        with st.expander("📘 How to use", expanded=False):
            st.markdown(
                "1. Enter your API key\n"
                "2. Add content sources\n"
                "3. Pick analyses\n"
                "4. Hit **🚀 Analyze**"
            )
        st.caption("KnowledgeAgent Pro")

    return api_key, base_url, model_id
