import streamlit as st

def render_footer():
    """Render a footer with information about the hackathon and creator"""

    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**KnowledgeAgent Pro**")
        st.markdown("Created by [renzo4web](https://github.com/renzo4web) | [X/Twitter](https://x.com/turbopila)")

    with col2:
        st.markdown("**Global Agent Hackathon May 2025**")
        st.markdown("Submission for the Global Agent Hackathon 2025")

    st.markdown("<div style='text-align: center; color: #888; padding: 10px;'>© 2025 - Built with ❤️ by renzo4web</div>",
                unsafe_allow_html=True)

