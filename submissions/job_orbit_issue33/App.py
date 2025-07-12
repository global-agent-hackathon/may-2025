# improved_app.py
import streamlit as st
import json
import os
import fitz
from datetime import datetime
from main import create_agent, init_linkedin_api
from job_application_automation import initiate_job_application
from ask_referrals import automate_browser_referrals
from agno.utils.pprint import pprint_run_response
from typing import Iterator, Dict, Any
from agno.agent import Agent, RunResponse
import pandas as pd
import asyncio
import time


class AutoApplyUI:

    def __init__(self):
        st.set_page_config(page_title="AutoApply Agent",
                           page_icon="🚀",
                           layout="wide",
                           initial_sidebar_state="expanded")
        self.linkedin_api = init_linkedin_api()
        self.ensure_directories()
        self.init_session_state()

    def init_session_state(self):
        """Initialize session state variables"""
        if 'search_params' not in st.session_state:
            st.session_state.search_params = None
        if 'last_search_time' not in st.session_state:
            st.session_state.last_search_time = None

    def ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            './data', './data/customized_resumes', './data/applications',
            './data/logs'
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def show_header(self):
        st.title("🚀 AutoApply: Your Automated Job Search Assistant")
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h4>🎯 What AutoApply Does:</h4>
            <ul>
                <li>🔍 <b>Smart Job Search</b>: Find relevant jobs based on your preferences</li>
                <li>📝 <b>Resume Customization</b>: AI-powered resume tailoring for each job</li>
                <li>📧 <b>Automated Applications</b>: Submit applications with customized resumes</li>
                <li>📊 <b>Progress Tracking</b>: Monitor your application statistics</li>
            </ul>
        </div>
        """,
                    unsafe_allow_html=True)

    def show_sidebar(self):
        with st.sidebar:
            st.title("⚙️ Settings")

            # Provider selection
            provider = st.selectbox(
                "🤖 Select LLM Provider",
                options=['aws', 'ollama'],
                help="Choose the AI model provider for resume customization")

            # Advanced settings
            with st.expander("🔧 Advanced Settings"):
                max_jobs = st.slider("Max Jobs to Process", 1, 50, 10)
                auto_apply = st.checkbox("Enable Auto-Apply", value=False)
                include_referrals = st.checkbox("Request Referrals",
                                                value=True)

            # LinkedIn connection status
            st.subheader("🔗 LinkedIn Status")
            if self.linkedin_api:
                st.success("✅ Connected")
            else:
                st.error("❌ Not Connected")
                st.info("Add LinkedIn credentials to .env file")

            return {
                'provider': provider,
                'max_jobs': max_jobs,
                'auto_apply': auto_apply,
                'include_referrals': include_referrals
            }

    def show_job_preferences_upload(self):
        st.header("🎯 Job Preferences")

        col1, col2 = st.columns([2, 1])

        with col1:
            uploaded_file = st.file_uploader(
                "Upload your job preferences (CSV)",
                type=['csv'],
                help=
                "Upload a CSV file with columns: Company, Role, Location, Priority, etc."
            )

        with col2:
            if st.button("📋 Download Template"):
                # Create sample CSV template
                template_data = {
                    'Company': ['Google', 'Microsoft', 'Amazon'],
                    'Role':
                    ['Data Scientist', 'Software Engineer', 'Product Manager'],
                    'Location': ['San Francisco', 'Seattle', 'New York'],
                    'Priority': ['High', 'Medium', 'High'],
                    'Keywords':
                    ['python,ml', 'javascript,react', 'product,strategy'],
                    'Experience': ['Mid', 'Senior', 'Mid']
                }
                df = pd.DataFrame(template_data)
                csv = df.to_csv(index=False)
                st.download_button(label="Download CSV Template",
                                   data=csv,
                                   file_name="job_preferences_template.csv",
                                   mime="text/csv")

        if uploaded_file:
            try:
                # Save and preview
                with open('./data/job_pref.csv', 'wb') as f:
                    f.write(uploaded_file.getvalue())
                st.success("✅ Job preferences uploaded successfully!")

                # Enhanced preview
                df = pd.read_csv(uploaded_file)
                st.subheader("📊 Preview of Job Preferences")
                st.dataframe(df, use_container_width=True)

                # Quick stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Preferences", len(df))
                with col2:
                    st.metric(
                        "Companies", df['Company'].nunique()
                        if 'Company' in df.columns else 0)
                with col3:
                    st.metric(
                        "Locations", df['Location'].nunique()
                        if 'Location' in df.columns else 0)

            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")

    def show_resume_upload(self):
        st.header("📄 Base Resume")

        col1, col2 = st.columns([2, 1])

        with col1:
            uploaded_resume = st.file_uploader(
                "Upload your base resume (PDF)",
                type=['pdf'],
                help="Upload your base resume in PDF format for customization")

        with col2:
            if os.path.exists('./data/base_resume.pdf'):
                st.success("✅ Resume uploaded")
                file_size = os.path.getsize('./data/base_resume.pdf')
                st.info(f"File size: {file_size/1024:.1f} KB")

        if uploaded_resume:
            try:
                # Save the uploaded resume
                with open('./data/base_resume.pdf', 'wb') as f:
                    f.write(uploaded_resume.getvalue())
                st.success("✅ Base resume uploaded successfully!")

                # Enhanced preview with text extraction
                with st.expander("🔍 Preview Resume"):
                    try:
                        doc = fitz.open('./data/base_resume.pdf')

                        # Show first page as image
                        first_page = doc[0]
                        pix = first_page.get_pixmap(
                            matrix=fitz.Matrix(1.5, 1.5))
                        img_bytes = pix.tobytes()
                        st.image(img_bytes, caption="Resume Preview")

                        # Extract and show text summary
                        text = ""
                        for page in doc:
                            text += page.get_text()

                        st.subheader("📝 Extracted Text Summary")
                        st.text_area("Resume Content",
                                     text[:500] +
                                     "..." if len(text) > 500 else text,
                                     height=150)

                        doc.close()
                    except Exception as e:
                        st.error(f"Preview error: {str(e)}")

            except Exception as e:
                st.error(f"❌ Error uploading resume: {str(e)}")

    def show_job_search_interface(self):
        st.header("🔍 Job Search Configuration")

        # Show current search parameters if they exist
        if st.session_state.search_params:
            with st.expander("📋 Current Search Parameters", expanded=False):
                st.json(st.session_state.search_params)
                if st.button("🗑️ Clear Search Parameters"):
                    st.session_state.search_params = None
                    st.session_state.last_search_time = None
                    st.rerun()

        with st.form("job_search_form"):
            col1, col2 = st.columns(2)

            # Pre-fill form with saved parameters if they exist
            saved_params = st.session_state.search_params or {}

            with col1:
                keywords = st.text_input(
                    "🏷️ Job Title/Keywords",
                    value=saved_params.get("keywords", "Software Engineer"),
                    help="Enter job titles or keywords to search for")
                location = st.text_input("📍 Location",
                                         value=saved_params.get(
                                             "location", "India"),
                                         help="Enter location for job search")

            with col2:
                companies = st.text_input(
                    "🏢 Target Companies",
                    value=saved_params.get("companies_str", "Cohesity"),
                    help="Comma-separated list of target companies")
                experience = st.selectbox(
                    "💼 Experience Level",
                    options=[
                        'Open For All', '1+ years', '2+ years', '3+ years',
                        '4+ years', '5+years'
                    ],
                    index=[
                        'Open For All', '1+ years', '2+ years', '3+ years',
                        '4+ years', '5+years'
                    ].index(saved_params.get("experience", "Open For All")),
                    help="F=Fresh, C=Associate, P=Mid-Senior")

            # Advanced filters
            with st.expander("🔧 Advanced Filters"):
                col3, col4 = st.columns(2)
                with col3:
                    job_type = st.multiselect(
                        "Job Type",
                        ["Full-time", "Part-time", "Contract", "Internship"],
                        default=saved_params.get("job_type", []))
                    posted_within = st.selectbox("Posted Within",
                                                 options=[
                                                     "24 hours", "3 days",
                                                     "1 week", "2 weeks",
                                                     "1 month"
                                                 ],
                                                 index=2)
                with col4:
                    salary_range = st.slider(
                        "Salary Range (LPA)", 0, 100,
                        saved_params.get("salary_range", (10, 50)))
                    remote_ok = st.checkbox("Remote/Hybrid OK",
                                            value=saved_params.get(
                                                "remote_ok", True))

            search_submitted = st.form_submit_button(
                "🔍 Update Search Parameters", use_container_width=True)

            if search_submitted:
                # Store search parameters in session state
                search_params = {
                    'keywords':
                    keywords,
                    'location':
                    location,
                    'companies':
                    [c.strip() for c in companies.split(',') if c.strip()],
                    'companies_str':
                    companies,  # Store original string too
                    'experience':
                    experience,
                    'job_type':
                    job_type,
                    'posted_within':
                    posted_within,
                    'salary_range':
                    salary_range,
                    'remote_ok':
                    remote_ok
                }

                st.session_state.search_params = search_params
                st.session_state.last_search_time = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")
                st.success("✅ Search parameters updated!")
                st.rerun()

        return st.session_state.search_params

    def show_customized_resumes(self):
        st.header("📑 Customized Resumes")

        resume_dir = "./data/customized_resumes"
        if os.path.exists(resume_dir):
            resumes = [f for f in os.listdir(resume_dir) if f.endswith('.pdf')]

            if resumes:
                # Add search and filter
                col1, col2 = st.columns([2, 1])
                with col1:
                    search_term = st.text_input(
                        "🔍 Search resumes",
                        placeholder="Enter job ID or company name")
                with col2:
                    sort_by = st.selectbox("Sort by",
                                           ["Name", "Date Modified", "Size"])

                # Filter resumes
                if search_term:
                    resumes = [
                        r for r in resumes if search_term.lower() in r.lower()
                    ]

                st.info(f"📊 Found {len(resumes)} customized resumes")

                # Display resumes in a more organized way
                for i, resume in enumerate(resumes):
                    with st.expander(f"📄 {resume}"):
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            # Show resume preview
                            try:
                                doc = fitz.open(f"{resume_dir}/{resume}")
                                first_page = doc[0]
                                pix = first_page.get_pixmap(
                                    matrix=fitz.Matrix(0.8, 0.8))
                                img_bytes = pix.tobytes()
                                st.image(img_bytes, width=400)
                                doc.close()
                            except Exception as e:
                                st.error(f"Preview error: {str(e)}")

                        with col2:
                            # File info and actions
                            file_path = f"{resume_dir}/{resume}"
                            file_size = os.path.getsize(file_path)
                            mod_time = datetime.fromtimestamp(
                                os.path.getmtime(file_path))

                            st.metric("File Size", f"{file_size/1024:.1f} KB")
                            st.write(
                                f"**Modified:** {mod_time.strftime('%Y-%m-%d %H:%M')}"
                            )

                            # Download button
                            with open(file_path, "rb") as f:
                                st.download_button(label="📥 Download PDF",
                                                   data=f,
                                                   file_name=resume,
                                                   mime="application/pdf",
                                                   use_container_width=True)

                            # Delete button
                            if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                                os.remove(file_path)
                                st.rerun()
            else:
                st.info(
                    "📝 No customized resumes found. Run job search and customization first."
                )
        else:
            st.info("📁 Customized resumes directory not found.")

    def show_action_buttons(self, search_params: Dict[str, Any],
                            settings: Dict[str, Any]):
        st.header("🎯 Actions")

        # Show search parameters status
        if search_params:
            st.success(
                f"✅ Search parameters set for: {search_params['keywords']} at {search_params['companies_str']}"
            )
            if st.session_state.last_search_time:
                st.info(f"Last updated: {st.session_state.last_search_time}")
        else:
            st.warning(
                "⚠️ Please set search parameters first using the form above")

        col1, col2, col3, col4 = st.columns(4)

        # Check prerequisites
        has_preferences = os.path.exists('./data/job_pref.csv')
        has_resume = os.path.exists('./data/base_resume.pdf')
        has_search_params = search_params is not None

        with col1:
            search_disabled = not (has_preferences or has_search_params)
            search = st.button(
                "🔍 Search Jobs",
                disabled=search_disabled,
                help="Find jobs based on your search parameters" if
                not search_disabled else "Please set search parameters first",
                use_container_width=True)

        with col2:
            customize_disabled = not (has_resume and has_search_params)
            customize = st.button(
                "📝 Customize Resumes",
                disabled=customize_disabled,
                help="Create tailored resumes for found jobs"
                if not customize_disabled else
                "Please upload resume and set search parameters first",
                use_container_width=True)

        with col3:
            apply_disabled = not (has_resume and has_search_params)
            ask = st.button("📧 Ask Referrals",
                            disabled=apply_disabled,
                            help="Ask for referrals for search jobs"
                            if not apply_disabled else "Complete setup first",
                            use_container_width=True)

        with col4:
            apply_disabled = not (has_resume and has_search_params)
            apply = st.button(
                "📧 Apply to Jobs",
                disabled=apply_disabled,
                help="Submit applications with customized resumes"
                if not apply_disabled else "Complete setup first",
                use_container_width=True)

        # Show prerequisites status
        missing_items = []
        if not has_search_params:
            missing_items.append("- 🔍 Set search parameters")
        if not has_preferences:
            missing_items.append("- 📋 Upload job preferences (optional)")
        if not has_resume:
            missing_items.append("- 📄 Upload base resume")

        if missing_items:
            st.warning("⚠️ Complete setup to enable all features:")
            for item in missing_items:
                st.write(item)

        return search, customize, apply, ask

    def show_enhanced_stats(self):
        st.header("📊 Application Statistics")

        # Load stats from memory
        stats = {}
        if os.path.exists("data/memory.json"):
            try:
                with open("data/memory.json", "r") as f:
                    stats = json.load(f)
            except:
                stats = {}

        # Create metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            jobs_found = len(stats.get("jobs_found", []))
            st.metric("🔍 Jobs Found",
                      jobs_found,
                      delta=f"+{jobs_found}" if jobs_found > 0 else None)

        with col2:
            applications = len(stats.get("applications", []))
            st.metric("📧 Applications",
                      applications,
                      delta=f"+{applications}" if applications > 0 else None)

        with col3:
            customized_resumes = len([
                f for f in os.listdir("./data/customized_resumes")
                if f.endswith('.pdf')
            ] if os.path.exists("./data/customized_resumes") else [])
            st.metric("📑 Custom Resumes", customized_resumes)

        with col4:
            referrals = len(stats.get("referrals", []))
            st.metric("🤝 Referrals", referrals)

        # Show success rate
        if jobs_found > 0:
            success_rate = (applications / jobs_found) * 100
            st.progress(success_rate / 100)
            st.write(f"**Application Success Rate:** {success_rate:.1f}%")

    def run_agent_query(self, query: str, provider: str):
        """Enhanced agent query execution with better UI feedback"""
        import time
        from datetime import datetime

        # Create progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Add enhanced CSS styles
        st.markdown("""
        <style>
        .agent-message {
            margin-bottom: 1em;
            padding: 1em 1.25em;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-left: 4px solid #3b82f6;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: all 0.3s ease;
        }
        
        .agent-header {
            display: flex;
            align-items: center;
            margin-bottom: 0.75em;
            font-size: 13px;
            color: #64748b;
            font-weight: 600;
        }
        
        .agent-timestamp {
            margin-left: auto;
            background: #e2e8f0;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
        }
        
        .agent-content {
            font-size: 15px;
            line-height: 1.6;
            color: #1e293b;
            margin: 0;
        }
        
        .typing-cursor {
            color: #3b82f6;
            opacity: 0.7;
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        </style>
        """,
                    unsafe_allow_html=True)

        try:
            status_text.text("🤖 Initializing agent...")
            progress_bar.progress(20)

            agent = create_agent(provider)

            status_text.text("🔍 Processing your request...")
            progress_bar.progress(40)

            # Create a container for streaming results
            result_container = st.container()

            with result_container:
                st.subheader("🤖 Agent Response")

                # Define the initial container for the full response
                response_placeholder = st.empty()

                response_stream: Iterator[RunResponse] = agent.run(
                    query, stream=True, stream_intermediate_steps=True)

                accumulated_response = ""

                # Stream each chunk with enhanced formatting
                for chunk in response_stream:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    content = chunk.content.strip() if chunk.content else ""

                    if content:
                        accumulated_response += content + " "

                        # Enhanced message formatting
                        formatted_message = f"""
                        <div class="agent-message">
                            <div class="agent-header">
                                <span style="font-size: 16px; margin-right: 8px;">🤖</span>
                                <span><strong>AI Agent</strong></span>
                                <span class="agent-timestamp">{timestamp}</span>
                            </div>
                            <div class="agent-content">
                                {accumulated_response.strip()}
                                <span class="typing-cursor">▌</span>
                            </div>
                        </div>
                        """

                        response_placeholder.markdown(formatted_message,
                                                      unsafe_allow_html=True)
                        time.sleep(0.02)

                # Final response without cursor
                if accumulated_response.strip():
                    final_timestamp = datetime.now().strftime("%H:%M:%S")
                    final_message = f"""
                    <div class="agent-message">
                        <div class="agent-header">
                            <span style="font-size: 16px; margin-right: 8px;">✅</span>
                            <span><strong>AI Agent</strong></span>
                            <span class="agent-timestamp">{final_timestamp}</span>
                        </div>
                        <div class="agent-content">{accumulated_response.strip()}</div>
                    </div>
                    """
                    response_placeholder.markdown(final_message,
                                                  unsafe_allow_html=True)

                status_text.text("📝 Processing complete...")
                progress_bar.progress(80)

                # Keep your existing pprint_run_response if needed
                # pprint_run_response(response_stream, markdown=True)

                progress_bar.progress(100)
                status_text.text("✅ Complete!")

                # Clear progress indicators after a delay
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()

        except Exception as e:
            st.error(f"❌ Error running agent: {str(e)}")
            progress_bar.empty()
            status_text.empty()

    def show_application_history(self):
        st.header("📋 Application History")

        if os.path.exists("data/memory.json"):
            try:
                with open("data/memory.json", "r") as f:
                    history = json.load(f)

                # Create tabs for different types of history
                tab1, tab2, tab3 = st.tabs([
                    "📧 Applications", "🔍 Job Searches",
                    "📑 Resume Customizations"
                ])

                with tab1:
                    applications = history.get("applications", [])
                    if applications:
                        for i, app in enumerate(applications):
                            with st.expander(
                                    f"Application {i+1}: {app.get('company', 'Unknown')}"
                            ):
                                st.json(app)
                    else:
                        st.info("No applications submitted yet.")

                with tab2:
                    searches = history.get("job_searches", [])
                    if searches:
                        for search in searches:
                            st.write(
                                f"**Keywords:** {search.get('keywords', 'N/A')}"
                            )
                            st.write(
                                f"**Date:** {search.get('timestamp', 'N/A')}")
                    else:
                        st.info("No job searches performed yet.")

                with tab3:
                    customizations = history.get("resume_customizations", [])
                    if customizations:
                        for custom in customizations:
                            st.write(
                                f"**Job:** {custom.get('job_title', 'N/A')}")
                            st.write(
                                f"**Company:** {custom.get('company', 'N/A')}")
                    else:
                        st.info("No resume customizations performed yet.")

            except Exception as e:
                st.error(f"Error loading history: {str(e)}")
        else:
            st.info(
                "📝 No application history found. Start using the app to see your history here!"
            )

    def run(self):
        """Main application runner with enhanced flow"""
        self.show_header()
        settings = self.show_sidebar()

        # Create tabs for better organization
        tab1, tab2, tab3, tab4 = st.tabs(
            ["🎯 Setup", "🔍 Search & Apply", "📊 Results", "📋 History"])

        with tab1:
            self.show_job_preferences_upload()
            self.show_resume_upload()

        with tab2:
            search_params = self.show_job_search_interface()
            search, customize, apply, ask = self.show_action_buttons(
                search_params, settings)

            # Handle button actions with enhanced queries using session state
            if search and st.session_state.search_params:
                params = st.session_state.search_params
                companies_str = ', '.join(params['companies'])
                query = f"""
                Find {params['keywords']} jobs at {companies_str} in {params['location']} 
                with {params['experience']} experience level. 
                Search for up to {settings['max_jobs']} jobs.
                """
                self.run_agent_query(query, settings['provider'])

            if customize and st.session_state.search_params:
                params = st.session_state.search_params
                companies_str = ', '.join(params['companies'])
                query = f"""
                Find {params['keywords']} jobs at {companies_str} in {params['location']} 
                with {params['experience']} experience level.
                Then you must customize my resume for each found job that matches my preferences.
                Create tailored resumes highlighting relevant skills and experience.
                """

                self.run_agent_query(query, settings['provider'])

            if apply and st.session_state.search_params:
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text("🤖 Applying Jobs...")
                progress_bar.progress(50)
                asyncio.run(initiate_job_application())
                status_text.text("✅ Applications submitted!")
                progress_bar.progress(100)

            if ask and st.session_state.search_params:
                params = st.session_state.search_params
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text("🤖 Asking referrals...")
                progress_bar.progress(50)
                asyncio.run(automate_browser_referrals())
                status_text.text("✅ Referrals Asked")
                progress_bar.progress(100)

        with tab3:
            self.show_enhanced_stats()
            self.show_customized_resumes()

        with tab4:
            self.show_application_history()


if __name__ == "__main__":
    ui = AutoApplyUI()
    ui.run()
