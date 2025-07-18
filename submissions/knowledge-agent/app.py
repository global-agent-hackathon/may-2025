
def main():
    from ui.sidebar import render_sidebar
    from ui.sources import init_source_state, render_source_input, render_sources_list
    from ui.analysis import render_analysis_config, render_analysis_button, render_results
    from ui.footer import render_footer

    import streamlit as st

    # Page Configuration
    st.set_page_config(
        page_title="KnowledgeAgent Pro",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    init_source_state()

    # Header
    st.markdown("<h1 style='text-align: center; color: #333;'>✨ KnowledgeAgent Pro ✨</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555;'>Unlock Deeper Understanding from Your Content</h3>", unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar
    api_key, base_url, model_id = render_sidebar()

    # Main Application
    render_source_input()
    render_sources_list()

    # Analysis Configuration
    selected_analysis_keys, output_length = render_analysis_config()

    # Process Analysis
    results = render_analysis_button(api_key, base_url, model_id, selected_analysis_keys, output_length)

    # Display Results
    if results:
        render_results(results)

    # Footer
    render_footer()

if __name__ == "__main__":
    main()
