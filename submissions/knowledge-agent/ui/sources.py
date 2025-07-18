import streamlit as st
from utils import process_pdf, format_source_title, count_tokens

MAX_SOURCES = 20


def init_source_state():
    """Initialize source-related session state"""
    if "sources" not in st.session_state:
        st.session_state.sources = []
    if "textarea_key_counter" not in st.session_state:
        st.session_state.textarea_key_counter = 0
    if "file_uploader_key" not in st.session_state:
        st.session_state.file_uploader_key = 0


def render_source_input():
    """Render PDF upload and text input section"""
    st.markdown("## 1. Add Your Content Sources")

    # PDF Uploader
    uploaded_file = st.file_uploader(
        "📄 Upload a PDF file:",
        type=['pdf'],
        key=f"pdf_uploader_{st.session_state.file_uploader_key}"
    )

    # Process PDF automatically
    if uploaded_file is not None and len(st.session_state.sources) < MAX_SOURCES:
        add_pdf_source(uploaded_file)

    # Text input
    current_textarea_key = f"new_source_input_{st.session_state.textarea_key_counter}"

    new_source_text = st.text_area(
        "Or paste your text here:",
        height=200,
        placeholder="Example: A news article, a chapter from a book...",
        key=current_textarea_key
    )

    # Add text button
    if len(st.session_state.sources) < MAX_SOURCES:
        if st.button("➕ Add Text Source", use_container_width=True, type="secondary"):
            add_text_source(current_textarea_key)
    else:
        st.info(f"ℹ️ Maximum of {MAX_SOURCES} sources reached.", icon="ℹ️")


def add_pdf_source(uploaded_file):
    """Process and add PDF file as source"""
    try:
        text_content = process_pdf(uploaded_file)

        if text_content:
            st.session_state.sources.append({
                "title": format_source_title(uploaded_file.name, "📄"),
                "content": text_content
            })

            st.session_state.file_uploader_key += 1
            st.success(f"✅ PDF '{uploaded_file.name}' added successfully!")
            st.rerun()

    except Exception as e:
        st.error(f"❌ {str(e)}")


def add_text_source(textarea_key):
    """Add text from textarea as source"""
    text_to_add = st.session_state.get(textarea_key, "").strip()

    if text_to_add:
        st.session_state.sources.append({
            "title": format_source_title(text_to_add, "📝"),
            "content": text_to_add
        })
        st.session_state.textarea_key_counter += 1
        st.rerun()
    else:
        st.warning("❗ Please paste some text to add.", icon="⚠️")


def render_sources_list():
    """Display list of added sources with management options"""
    if not st.session_state.sources:
        st.info("ℹ️ Add content sources using the options above.", icon="ℹ️")
        return

    st.markdown("---")

    # Token counter
    combined_text = "\n\n".join([s['content'] for s in st.session_state.sources])
    total_tokens = count_tokens(combined_text)

    st.info(f"📊 **Total tokens: {total_tokens:,}**")

    with st.expander("Common model context limits"):
        st.markdown("""
        - GPT-4: 8K - 128K tokens
        - Claude: 100K - 200K tokens  
        - Gemini: 1M+ tokens
        - Mistral: 32K - 131K tokens
        - Most open models: 4K - 32K tokens
        """)

    # Sources header and clear button
    st.markdown("### My Content Sources")
    if st.button("🗑️ Clear All Sources", type="secondary", use_container_width=True):
        st.session_state.sources = []
        st.rerun()

    # Display sources in columns
    num_columns = min(len(st.session_state.sources), 3)
    cols = st.columns(num_columns)

    for index, source in enumerate(st.session_state.sources):
        col_index = index % num_columns
        with cols[col_index]:
            render_source_card(index, source)

    st.markdown("---")


def render_source_card(index, source):
    """Render individual source card with actions"""
    with st.container(border=True):
        st.markdown(f"**Source {index + 1}:** {source['title']}")

        with st.expander("View/Hide Content", expanded=False):
            st.text_area(
                f"Content of Source {index + 1}",
                source['content'],
                height=150,
                disabled=True,
                key=f"source_content_view_{index}"
            )

        if st.button(
                f"🗑️ Remove",
                key=f"del_source_{index}",
                use_container_width=True,
                type="secondary"
        ):
            st.session_state.sources.pop(index)
            st.rerun()
