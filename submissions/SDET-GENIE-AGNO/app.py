import pandas as pd
import streamlit as st
import sys
import asyncio
import os
import re
from dotenv import load_dotenv

from browser_use import Browser, Agent as BrowserAgent
from src.Utilities.utils import controller
from langchain_google_genai import ChatGoogleGenerativeAI

from src.Prompts.agno_prompts import (
    generate_selenium_pytest_bdd,
    generate_playwright_python,
    generate_cypress_js,
    generate_robot_framework,
    generate_java_selenium,
    generate_gherkin_scenarios,
    enhance_user_story,
    generate_manual_test_cases
)

from src.Prompts.browser_prompts import (
    generate_browser_task
)
# from src.Utilities.run_self_healing_demo import run_self_healing_demo
# # Load environment variables
load_dotenv()

# Handle Windows asyncio policy
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


# Dictionary mapping framework names to their generation functions
FRAMEWORK_GENERATORS = {
    "Selenium + PyTest BDD (Python)": generate_selenium_pytest_bdd,
    "Playwright (Python)": generate_playwright_python,
    "Cypress (JavaScript)": generate_cypress_js,
    "Robot Framework": generate_robot_framework,
    "Selenium + Cucumber (Java)": generate_java_selenium
}

# Dictionary mapping framework names to their file extensions
FRAMEWORK_EXTENSIONS = {
    "Selenium + PyTest BDD (Python)": "py",
    "Playwright (Python)": "py",
    "Cypress (JavaScript)": "js",
    "Robot Framework": "robot",
    "Selenium + Cucumber (Java)": "java"
}

# Framework descriptions
framework_descriptions = {
    "Selenium + PyTest BDD (Python)": "Popular Python testing framework combining Selenium WebDriver with PyTest BDD for behavior-driven development. Best for Python developers who want strong test organization and reporting.",
    "Playwright (Python)": "Modern, powerful browser automation framework with built-in async support and cross-browser testing capabilities. Excellent for modern web applications and complex scenarios.",
    "Cypress (JavaScript)": "Modern, JavaScript-based end-to-end testing framework with real-time reloading and automatic waiting. Perfect for front-end developers and modern web applications.",
    "Robot Framework": "Keyword-driven testing framework that uses simple, tabular syntax. Great for teams with mixed technical expertise and for creating readable test cases.",
    "Selenium + Cucumber (Java)": "Robust combination of Selenium WebDriver with Cucumber for Java, supporting BDD. Ideal for Java teams and enterprise applications."
}

def main():

    st.set_page_config(page_title="SDET-GENIE", layout="wide")

    # Apply custom CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    /* General App Styling */
    .stApp {
        font-family: 'Poppins', sans-serif;
        background-color: #87CEEB; /* Sky blue background */
        color: #333333;
        padding: 2rem;
    }

    /* Navigation Bar Styling */
    .header {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 1rem 2rem;
        background-color: #4682B4; /* Steel blue for header */
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        margin-bottom: 2rem;
    }

    .header-item {
        color: #FFFFFF;
        font-size: 1.1rem;
        font-weight: 600;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        text-align: center;
        transition: background 0.3s ease, transform 0.3s ease;
    }

    .header-item:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-3px);
    }

    /* Button Styling */
    .stButton > button {
        background-color: #4682B4; /* Steel blue for buttons */
        color: #FFFFFF;
        font-size: 1rem;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        border: none;
        transition: background 0.3s ease, transform 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #5F9EA0; /* Cadet blue on hover */
        transform: scale(1.05);
    }

    /* Input Fields Styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #F0F8FF; /* Alice blue for input fields */
        border: 1px solid #4682B4;
        color: #333333;
        border-radius: 8px;
        padding: 0.6rem;
        transition: border 0.3s ease, box-shadow 0.3s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #4682B4;
        box-shadow: 0 0 8px rgba(70, 130, 180, 0.6);
    }

    /* Form Controls Styling */
    .stRadio > div {
        background-color: #F0F8FF;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    .stRadio > div:hover {
        background-color: #E6F3FF;
    }

    /* Grid Layout Styling */
    .stContainer {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
    }

    /* Footer Styling */
    .footer {
        text-align: center;
        padding: 1rem;
        background-color: #4682B4;
        border-radius: 10px;
        margin-top: 3rem;
        box-shadow: 0 -4px 15px rgba(0, 0, 0, 0.2);
        color: white;
    }

    .main-title {
        text-align: center;
        font-family: 'Poppins', sans-serif;
        font-size: 45px;
        font-weight: 600;
        color: #333333;
        padding: 10px 0;
        margin-bottom: 20px;
        border-bottom: 2px solid #4682B4;
        width: 100%;
        box-sizing: border-box;
    }

    .subtitle {
        font-family: 'Poppins', sans-serif;
        font-size: 24px;
        color: #333333;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 400;
    }

    .card {
        background-color: #F0F8FF;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(70, 130, 180, 0.3);
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }

    .code-container {
        background-color: #F8F8FF;
        border-radius: 10px;
        padding: 20px;
        box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
    }

    .glow-text {
        color: #4682B4;
    }

    .sidebar-heading {
        background-color: #4682B4;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
        color: white;
    }

    .status-success {
        background-color: #90EE90;
        color: #333333;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 15px 0;
    }

    .status-error {
        background-color: #FFA07A;
        color: #333333;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 15px 0;
    }

    .tab-container {
        background-color: #F0F8FF;
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }

    .download-btn {
        background-color: #4682B4;
        color: white;
        text-align: center;
        padding: 12px 20px;
        border-radius: 30px;
        font-weight: 600;
        display: block;
        margin: 20px auto;
        width: fit-content;
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .download-btn:hover {
        background-color: #5F9EA0;
        transform: scale(1.05);
        box-shadow: 0 12px 20px rgba(0, 0, 0, 0.15);
    }

    .fade-in {
        animation: fadeIn 1.5s ease-in-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* Spinner styling */
    .stSpinner > div > div {
        border-color: #4682B4 #4682B4 transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Custom Header
    st.markdown('<div class="header fade-in"><span class="header-item">AI Agents powered by AGNO and BROWSER-USE</span></div>', unsafe_allow_html=True)

    # Main Title with custom styling
    st.markdown('<h1 class="main-title fade-in">QA - AGENTS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle fade-in">User Stories to Automated Tests : The Future of QA Automation using AI Agents</p>', unsafe_allow_html=True)
    # Sidebar styling
    with st.sidebar:
        st.markdown('<div class="sidebar-heading"><a href="https://www.waigenie.tech/" target="_blank" style="color: white; text-decoration: none;">WAIGENIE</a></div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-heading">Avilable Frameworks</div>', unsafe_allow_html=True)
        selected_framework = st.selectbox(
            "Select framework:",
            list(FRAMEWORK_GENERATORS.keys()),
            index=0
        )
        #New About WaiGenie section with tabs
        with st.expander("About WaiGenie"):
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "Vision & Mission",
                "Features",
                "How It Works",
                "Workflow",
                "Benefits"
            ])

            with tab1:
                st.subheader("Our Vision")
                st.write("Revolutionizing Quality Assurance with AI-powered solutions that empower teams to deliver flawless software at unprecedented speeds.")

                st.subheader("Our Mission")
                st.write("Empower QA teams with cutting-edge AI solutions tailored for enterprise needs, enabling them to deliver high-quality software faster and more efficiently than ever before.")

            with tab2:
                st.markdown("#### 🧠 AI-Powered Test Generation")
                st.write("Generate comprehensive test scenarios using advanced AI algorithms.")
                st.markdown("#### 🔍 Intelligent Element Inspector")
                st.write("Automatically identify and analyze web elements with precision.")
                st.markdown("#### 📝 Gherkin Feature Generator")
                st.write("Transform user stories into clear, concise Gherkin feature files.")
                st.markdown("#### 💻 Automated Code Generation")
                st.write("Generate test automation scripts in multiple languages automatically.")
                st.markdown("#### 🤖 Web Agent Explorer")
                st.write("Leverage AI to automatically explore and test complex user journeys.")
                st.markdown("#### 📊 Advanced Analytics")
                st.write("Gain insights into your testing processes and identify areas for improvement.")

            with tab3:
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.markdown("### 1")
                with col2:
                    st.markdown("#### Sign Up")
                    st.write("Create your WaiGenie account and set up your organization profile.")
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.markdown("### 2")
                with col2:
                    st.markdown("#### Connect")
                    st.write("Integrate WaiGenie with your existing QA tools and workflows.")
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.markdown("### 3")
                with col2:
                    st.markdown("#### Analyze")
                    st.write("Let our AI analyze your application and generate test scenarios.")
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.markdown("### 4")
                with col2:
                    st.markdown("#### Optimize")
                    st.write("Continuously improve your QA process with AI-driven insights.")

            with tab4:
                st.subheader("AI-Powered QA Workflow")
                st.markdown("#### 1. QA Agent")
                st.write("• Converts user stories into Gherkin scenarios")
                st.write("• Generates positive and negative test cases")
                st.markdown("#### 2. Browser Agent")
                st.write("• Executes Gherkin scenarios in a browser")
                st.write("• Captures detailed DOM information")
                st.write("• Records element details like XPaths")
                st.markdown("#### 3. Code Generation Agent")
                st.write("• Transforms scenarios into automation scripts")
                st.write("• Includes necessary imports and dependencies")
                st.write("• Handles errors and provides helper functions")

            with tab5:
                st.write("• 90% reduction in time-to-test")
                st.write("• Enhanced test coverage")
                st.write("• Consistent code implementation")
                st.write("• Lower maintenance overhead")
                st.write("• Bridges skill gaps")
                st.write("• Preserves testing knowledge")
            # Add contact button and separator
            st.markdown("---")
            email = "richardsongunde@waigenie.tech"
            gmail_link = f"https://mail.google.com/mail/?view=cm&fs=1&to={email}"
            st.markdown(
                f'<a href="{gmail_link}" target="_blank"><button style="width: 100%; background: linear-gradient(90deg, #6A0572, #240046); color: white; padding: 0.6rem 1.2rem; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s ease;">Contact Us</button></a>',
                unsafe_allow_html=True
            )
            # Add logo and branding at the bottom
            st.markdown("""
            <div style="text-align: center; margin-top: 30px;">
                <img src="https://www.waigenie.tech/logo.png" style="width: 96px; height: auto; margin-bottom: 10px;">
                <img src="https://www.waigenie.tech/logotext.svg" style="width: 180px; height: auto; display: block; margin: 0 auto;">
                <p style="font-size: 0.75rem; color: #E6E6FA; margin-top: 10px;">© 2025 www.waigenie.tech. All rights reserved.</p>
            </div>
            """, unsafe_allow_html=True)

        # Add YouTube demo button
        youtube_url = "https://youtu.be/qH30GvQebqg?feature=shared"
        st.markdown(
            f'<a href="{youtube_url}" target="_blank"><button style="width: 100%; background: linear-gradient(90deg, #FF0000, #CC0000); color: white; padding: 0.6rem 1.2rem; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s ease;">▶️ YouTube Demo</button></a>',
            unsafe_allow_html=True
        )

    # Main content area with card styling
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    st.markdown('<h3 class="glow-text">Enter User Story</h3>', unsafe_allow_html=True)
    user_story = st.text_area(
        "",
        placeholder="e.g., As a user, I want to log in with valid credentials so that I can access my account."
    )
    st.markdown('</div>', unsafe_allow_html=True)
    # Buttons with better layout
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        enhance_story_btn = st.button("✨ Enhance User Story")
    with col2:
        generate_manual_btn = st.button("📝 Generate Manual Test Cases")
    with col3:
        generate_gherkin_btn = st.button(" Generate Gherkin")
    with col4:
        execute_btn = st.button("▶️ Execute Steps")
    with col5:
        generate_code_btn = st.button("💻 Generate Code")
    with col6:
        self_healing_btn = st.button("🔧 Self-Healing")

    # User Story Enhancement Section
    if enhance_story_btn and user_story:
        with st.spinner("Enhancing user story..."):
            # Call the user story enhancement agent
            enhanced_user_story = enhance_user_story(user_story)
            st.session_state.enhanced_user_story = enhanced_user_story
            st.markdown('<div class="status-success fade-in">User story enhanced successfully!</div>', unsafe_allow_html=True)

    # Display enhanced user story if available
    if "enhanced_user_story" in st.session_state:
        st.markdown('<div class="card code-container fade-in">', unsafe_allow_html=True)
        st.markdown('<h3 class="glow-text">Enhanced User Story</h3>', unsafe_allow_html=True)
        st.text_area(
            "Review and edit the enhanced user story:",
            value=st.session_state.enhanced_user_story,
            height=300,
            key="enhanced_user_story_editor"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Manual Test Case Generation Section
    if generate_manual_btn: # No longer requires user_story directly
        if "enhanced_user_story" not in st.session_state:
             st.markdown('<div class="status-error">Please enhance the user story first.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("Generating manual test cases..."):
                # Call the manual test case generation function with the enhanced user story
                manual_test_cases_markdown = generate_manual_test_cases(st.session_state.enhanced_user_story)

                # Parse the markdown table into a pandas DataFrame
                # Assuming the agent returns a markdown table with headers:
                # | Test Case ID | Test Case Title | Description | Preconditions | Test Steps | Expected Result | Test Data | Priority | Status | Postconditions |
                # |---|---|---|---|---|---|---|---|---|---|
                # | TC_US_[ID]_001 | ... | ... | ... | ... | 1. ...\n2. ... | ... | ... | ... | ... |
                lines = manual_test_cases_markdown.strip().split('\n')
                # Find the header and separator lines
                header_line = None
                separator_line = None
                for i, line in enumerate(lines):
                    if '| Test Case ID' in line:
                        header_line = i
                    elif line.startswith('|---'):
                        separator_line = i
                        break # Assume the first separator after header is the correct one

                if header_line is not None and separator_line is not None:
                    header = [h.strip() for h in lines[header_line].strip('|').split('|')]
                    data_lines = lines[separator_line + 1:]
                    data = []
                    for line in data_lines:
                        if line.strip().startswith('|'):
                            # Split by '|' and strip whitespace, remove first and last empty strings
                            row_data = [cell.strip() for cell in line.strip('|').split('|')]
                            data.append(row_data)

                    manual_test_cases_data = pd.DataFrame(data, columns=header).to_dict('records')

                    st.session_state.manual_test_cases = manual_test_cases_data
                    st.session_state.edited_manual_test_cases = manual_test_cases_data # Initialize edited state

                    st.markdown('<div class="status-success fade-in">Manual test cases generated successfully!</div>', unsafe_allow_html=True)
                else:
                     st.markdown('<div class="status-error fade-in">Failed to parse manual test cases from agent output.</div>', unsafe_allow_html=True)
                     st.write("Agent Output:", manual_test_cases_markdown) # Display agent output for debugging

    # Display manual test cases editor
    if "manual_test_cases" in st.session_state:
        st.markdown('<div class="card code-container fade-in">', unsafe_allow_html=True)
        st.markdown('<h3 class="glow-text">Your Manual Test Cases</h3>', unsafe_allow_html=True)

        # Display editable dataframe
        edited_df = st.data_editor(
            pd.DataFrame(st.session_state.edited_manual_test_cases),
            key="manual_test_case_editor",
            num_rows="dynamic"
        )

        # Add a save button for manual test cases
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("💾 Save Manual Changes", key="save_manual_changes_btn"):
                st.session_state.edited_manual_test_cases = edited_df.to_dict('records')
                st.session_state.manual_changes_saved = True
                st.rerun()

        # Display save status for manual test cases
        with col2:
            if "manual_changes_saved" in st.session_state and st.session_state.manual_changes_saved:
                st.markdown('<div class="status-success" style="margin: 0;">Manual test case changes saved successfully!</div>', unsafe_allow_html=True)
                st.session_state.manual_changes_saved = False # Reset the flag
            # Note: Checking for unsaved changes in data_editor is more complex, skipping for now.

        st.markdown('</div>', unsafe_allow_html=True)

    # Gherkin Generation Section
    if generate_gherkin_btn: # No longer requires user_story directly
        if "edited_manual_test_cases" not in st.session_state:
             st.markdown('<div class="status-error">Please generate manual test cases first.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("Generating Gherkin scenarios from manual test cases..."):
                # Call the Gherkin agent with the edited manual test cases
                # Convert the list of dicts back to a readable format for the agent
                manual_test_cases_text = ""
                if st.session_state.edited_manual_test_cases:
                    manual_test_cases_text = pd.DataFrame(st.session_state.edited_manual_test_cases).to_markdown(index=False)

                generated_steps = generate_gherkin_scenarios(manual_test_cases_text) # Pass manual test cases

                # Initialize both generated_steps and edited_steps in session state
                st.session_state.generated_steps = generated_steps
                st.session_state.edited_steps = generated_steps

            st.markdown('<div class="status-success fade-in">Gherkin scenarios generated successfully!</div>', unsafe_allow_html=True)

    # Display scenarios editor (whether newly generated or from session state)
    if "edited_steps" in st.session_state:
        st.markdown('<div class="card code-container fade-in">', unsafe_allow_html=True)
        st.markdown('<h3 class="glow-text">Your Gherkin Scenarios</h3>', unsafe_allow_html=True)

        # Display editable text area with the current edited steps
        edited_steps = st.text_area(
            "Edit scenarios if needed:",
            value=st.session_state.edited_steps,
            height=300,
            key="scenario_editor"
        )

        # Add a save button and show status
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("💾 Save Changes", key="save_changes_btn"):
                st.session_state.edited_steps = edited_steps
                st.session_state.changes_saved = True
                st.rerun()

        # Display save status
        with col2:
            if "changes_saved" in st.session_state and st.session_state.changes_saved:
                st.markdown('<div class="status-success" style="margin: 0;">Changes saved successfully!</div>', unsafe_allow_html=True)
                # Reset the flag after displaying
                st.session_state.changes_saved = False
            elif edited_steps != st.session_state.edited_steps:
                st.markdown('<div style="color: #FFA500; font-weight: bold;">* You have unsaved changes</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Test Execution Section
    if execute_btn:
        if "edited_steps" not in st.session_state:
            st.markdown('<div class="status-error">Please generate Gherkin scenarios first.</div>', unsafe_allow_html=True)
        else:
            # Check if there are unsaved changes and warn the user
            if "scenario_editor" in st.session_state and st.session_state.get("scenario_editor", "") != st.session_state.edited_steps:
                st.warning("You have unsaved changes. Please save your changes before executing steps.")
            else:
                with st.spinner("Executing test steps..."):
                    # Display the scenarios that will be executed
                    st.markdown('<div class="card code-container fade-in">', unsafe_allow_html=True)
                    st.markdown('<h4 class="glow-text">Executing Scenarios:</h4>', unsafe_allow_html=True)
                    st.code(st.session_state.edited_steps, language="gherkin")
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Use the edited steps for execution
                    steps_to_execute = st.session_state.edited_steps
            # Modify the execute_test function to store more detailed information
            async def execute_test(steps: str):
                try:
                    browser = Browser()

                    async with await browser.new_context() as context:
                        # Parse the Gherkin content to extract scenarios
                        scenarios = []
                        current_scenario = []
                        for line in steps.split('\n'):
                            if line.strip().startswith('Scenario:'):
                                if current_scenario:
                                    scenarios.append('\n'.join(current_scenario))
                                current_scenario = [line]
                            elif current_scenario:
                                current_scenario.append(line)
                        if current_scenario:
                            scenarios.append('\n'.join(current_scenario))

                        # Execute each scenario separately
                        all_results = []
                        all_actions = []
                        all_extracted_content = []
                        element_xpath_map = {}

                        for scenario in scenarios:
                            browser_agent = BrowserAgent(
                                task=generate_browser_task(scenario),
                                llm=ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key=os.environ.get("GOOGLE_API_KEY")),
                                browser=browser,
                                use_vision=True,
                                controller=controller,
                            )

                            # Execute and collect results
                            history = await browser_agent.run()
                            history.save_to_file("agent_history.json")
                            result = history.final_result()
                            if isinstance(result, str):
                                # Convert string result to JSON format
                                result = {"status": result, "details": "Execution completed"}
                            all_results.append(result)

                            # Log all model actions for debugging
                            st.write("Debug - Model Actions:", history.model_actions())

                            # Process model actions to extract element details
                            for i, action_data in enumerate(history.model_actions()):
                                action_name = history.action_names()[i] if i < len(history.action_names()) else "Unknown Action"

                                # Create a detail record for each action
                                action_detail = {
                                    "name": action_name,
                                    "index": i,
                                    "element_details": {}
                                }

                                # Check if this is a get_xpath_of_element action
                                if "get_xpath_of_element" in action_data:
                                    element_index = action_data["get_xpath_of_element"].get("index")
                                    action_detail["element_details"]["index"] = element_index

                                    # Check if the interacted_element field contains XPath information
                                    if "interacted_element" in action_data and action_data["interacted_element"]:
                                        element_info = action_data["interacted_element"]

                                        # Extract XPath from the DOMHistoryElement string
                                        xpath_match = re.search(r"xpath='([^']+)'", str(element_info))
                                        if xpath_match:
                                            xpath = xpath_match.group(1)
                                            element_xpath_map[element_index] = xpath
                                            action_detail["element_details"]["xpath"] = xpath

                                # Check if this is an action on an element
                                elif any(key in action_data for key in ["input_text", "click_element", "perform_element_action"]):
                                    # Find the action parameters
                                    for key in ["input_text", "click_element", "perform_element_action"]:
                                        if key in action_data:
                                            action_params = action_data[key]
                                            if "index" in action_params:
                                                element_index = action_params["index"]
                                                action_detail["element_details"]["index"] = element_index

                                                # If we have already captured the XPath for this element, add it
                                                if element_index in element_xpath_map:
                                                    action_detail["element_details"]["xpath"] = element_xpath_map[element_index]

                                                # Also check interacted_element
                                                if "interacted_element" in action_data and action_data["interacted_element"]:
                                                    element_info = action_data["interacted_element"]
                                                    xpath_match = re.search(r"xpath='([^']+)'", str(element_info))
                                                    if xpath_match:
                                                        xpath = xpath_match.group(1)
                                                        element_xpath_map[element_index] = xpath
                                                        action_detail["element_details"]["xpath"] = xpath

                                all_actions.append(action_detail)

                            # Also extract from content if available
                            for content in history.extracted_content():
                                all_extracted_content.append(content)

                                # Look for XPath information in extracted content
                                if isinstance(content, str):
                                    xpath_match = re.search(r"The xpath of the element is (.+)", content)
                                    if xpath_match:
                                        xpath = xpath_match.group(1)
                                        # Try to match with an element index from previous actions
                                        index_match = re.search(r"element (\d+)", content)
                                        if index_match:
                                            element_index = int(index_match.group(1))
                                            element_xpath_map[element_index] = xpath

                        # Save combined history to session state
                        st.session_state.history = {
                            "urls": history.urls(),
                            "action_names": history.action_names(),
                            "detailed_actions": all_actions,
                            "element_xpaths": element_xpath_map,
                            "extracted_content": all_extracted_content,
                            "errors": history.errors(),
                            "model_actions": history.model_actions(),
                            "execution_date": st.session_state.get("execution_date", "Unknown")
                        }

                        # Display test execution details
                        st.markdown('<div class="status-success fade-in">Test execution completed!</div>', unsafe_allow_html=True)

                        # Display key information in tabs
                        st.markdown('<div class="tab-container fade-in">', unsafe_allow_html=True)
                        tab1, tab2, tab3, tab4 = st.tabs(["Results", "Actions", "Elements", "Details"])
                        with tab1:
                            for i, result in enumerate(all_results):
                                st.markdown(f'<h4 class="glow-text">Scenario {i+1}</h4>', unsafe_allow_html=True)
                                st.json(result)

                        with tab2:
                            st.markdown('<h4 class="glow-text">Actions Performed</h4>', unsafe_allow_html=True)
                            for i, action in enumerate(all_actions):
                                action_text = f"{i+1}. {action['name']}"
                                if 'element_details' in action and action['element_details']:
                                    if 'xpath' in action['element_details']:
                                        action_text += f" (XPath: {action['element_details']['xpath']})"
                                    elif 'index' in action['element_details']:
                                        action_text += f" (Element index: {action['element_details']['index']})"
                                st.write(action_text)

                        with tab3:
                            st.markdown('<h4 class="glow-text">Element Details</h4>', unsafe_allow_html=True)
                            if element_xpath_map:
                                # Create a dataframe for better visualization
                                import pandas as pd
                                element_df = pd.DataFrame([
                                    {"Element Index": index, "XPath": xpath}
                                    for index, xpath in element_xpath_map.items()
                                ])
                                st.dataframe(element_df)
                            else:
                                st.info("No element XPaths were captured during test execution.")

                                # Display raw DOM information for debugging
                                st.markdown('<h4 class="glow-text">Raw DOM Information</h4>', unsafe_allow_html=True)
                                for i, action_data in enumerate(history.model_actions()):
                                    if "interacted_element" in action_data and action_data["interacted_element"]:
                                        st.write(f"Action {i}: {history.action_names()[i] if i < len(history.action_names()) else 'Unknown'}")
                                        st.code(str(action_data["interacted_element"]))

                        with tab4:
                            st.markdown('<h4 class="glow-text">Extracted Content</h4>', unsafe_allow_html=True)
                            for content in all_extracted_content:
                                st.write(content)
                        st.markdown('</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.markdown(f'<div class="status-error">An error occurred during test execution: {str(e)}</div>', unsafe_allow_html=True)

            st.session_state.execution_date = "February 26, 2025"
            asyncio.run(execute_test(steps_to_execute))  # Use steps_to_execute instead of generated_steps
    # Code Generation Section
    if generate_code_btn:
        if "edited_steps" not in st.session_state or "history" not in st.session_state:
            st.markdown('<div class="status-error">Please generate and execute Gherkin scenarios first.</div>', unsafe_allow_html=True)
        else:
            with st.spinner(f"Generating {selected_framework} automation code..."):
                try:
                    # Get the appropriate generator function
                    generator_function = FRAMEWORK_GENERATORS[selected_framework]

                    # Generate automation code using the edited steps instead of generated_steps
                    automation_code = generator_function(
                        st.session_state.edited_steps,  # Use edited_steps instead of generated_steps
                        st.session_state.history
                    )

                    # Store in session state
                    st.session_state.automation_code = automation_code

                    # Display code
                    st.markdown('<div class="card code-container fade-in">', unsafe_allow_html=True)
                    st.markdown(f'<h3 class="glow-text">Generated {selected_framework} Automation Code</h3>', unsafe_allow_html=True)

                    # Use appropriate language for syntax highlighting
                    code_language = "python"
                    if selected_framework == "Cypress (JavaScript)":
                        code_language = "javascript"
                    elif selected_framework == "Robot Framework":
                        code_language = "robot"
                    elif selected_framework == "Selenium + Cucumber (Java)":
                        code_language = "java"

                    st.code(automation_code, language=code_language)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Extract feature name for file naming - use edited_steps instead of generated_steps
                    feature_name = "automated_test"
                    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", st.session_state.edited_steps)
                    if feature_match:
                        feature_name = feature_match.group(1).strip().replace(" ", "_").lower()

                    # Get appropriate file extension
                    file_ext = FRAMEWORK_EXTENSIONS[selected_framework]

                    # Add download button
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.download_button(
                            label=f"📥 Download {selected_framework} Code",
                            data=automation_code,
                            file_name=f"{feature_name}_automation.{file_ext}",
                            mime="text/plain",
                        )

                    st.markdown('<div class="status-success fade-in">Automation code generated successfully!</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.markdown(f'<div class="status-error">Error generating {selected_framework} code: {str(e)}</div>', unsafe_allow_html=True)

    # Footer
    st.markdown('<div class="footer fade-in">© 2025 WAIGENIE | AI-Powered Test Automation</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()


## USER-STORY

# as a user i want to login into https://www.saucedemo.com/ with user name "standard_user", password "secret_sauce" and add this product to cart "Sauce Labs Bolt T-Shirt'
