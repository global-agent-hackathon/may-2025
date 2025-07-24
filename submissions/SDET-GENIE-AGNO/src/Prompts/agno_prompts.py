import re
from typing import Dict, Any
import json

import re
from typing import Dict, Any
import json
import streamlit as st

from src.Agents.agents import (
    gherkhin_agent, # Import gherkhin_agent
    code_gen_agent,
    manual_test_case_agent,# Import the new agent
    user_story_enhancement_agent)

from src.Utilities.utils import (
    extract_selectors_from_history,
    analyze_actions)

def generate_gherkin_scenarios(manual_test_cases_markdown: str) -> str:
    """Generate Gherkin scenarios from manual test cases using the QA agent"""
    try:
        # The QA agent's description, instructions, and expected_output handle the Gherkin generation logic.
        # We need to provide the manual test cases as the input to the agent's run method.
        run_response = gherkhin_agent.run(manual_test_cases_markdown)
        # Extract the content from the agent's response
        gherkin_content = extract_code_content(run_response.content)
        return gherkin_content
    except Exception as e:
        st.error(f"Error generating Gherkin scenarios: {str(e)}")
        raise

def generate_manual_test_cases(user_story: str) -> str:
    """Generate manual test cases from a user story using the manual test case agent"""
    try:
        run_response = manual_test_case_agent.run(user_story)
        # The manual test case agent is expected to return markdown
        manual_test_cases_content = extract_code_content(run_response.content)
        return manual_test_cases_content
    except Exception as e:
        st.error(f"Error generating manual test cases: {str(e)}")
        raise

def enhance_user_story(user_story: str) -> str:
    """Enhance a raw user story using the user story enhancement agent"""
    try:
        run_response = user_story_enhancement_agent.run(user_story)
        # The agent is expected to return the enhanced user story text
        enhanced_story_content = run_response.content
        return enhanced_story_content
    except Exception as e:
        st.error(f"Error enhancing user story: {str(e)}")
    raise

def extract_code_content(text: str) -> str:
    """Extract code from markdown code blocks if present"""
    # Look for content between triple backticks with optional language identifier
    code_block_pattern = re.compile(r"```(?:python|gherkin|javascript|java|robot|markdown)?\n(.*?)```", re.DOTALL)
    match = code_block_pattern.search(text)

    if match:
        return match.group(1).strip()
    return text.strip()

def generate_selenium_pytest_bdd(gherkin_steps: str, history_data: Dict[str, Any]) -> str:
    """Generate a single Python file with Selenium PyTest BDD automation code using the code generation agent"""

    # Extract feature name from Gherkin (optional, for context)
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    feature_name = feature_match.group(1).strip() if feature_match else "Automated Test"

    # Extract selectors and actions
    selectors = extract_selectors_from_history(history_data)
    actions = analyze_actions(history_data)

    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"

    # Create prompt for Selenium PyTest BDD code
    # The code generation agent's description, instructions, and expected_output handle the code generation logic.
    # We provide the Gherkin steps and execution details as context.
    code_file_prompt = f"""
    Generate Selenium PyTest BDD code based on the following:

    Gherkin Steps:
    ```gherkin
    {gherkin_steps}
    ```

    Agent Execution Details:
    - Base URL: {base_url}
    - Element Selectors: {json.dumps(selectors, indent=2)}
    - Actions Performed: {json.dumps(actions, indent=2)}
    - Extracted Content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
    """

    try:
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)

        return code_content

    except Exception as e:
        st.error(f"Error generating Selenium PyTest BDD code: {str(e)}")
        raise

def generate_playwright_python(gherkin_steps: str, history_data: Dict[str, Any]) -> str:
    """Generate a single Python file with Playwright automation code using the code generation agent"""

    # Extract feature name from Gherkin (optional, for context)
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    feature_name = feature_match.group(1).strip() if feature_match else "Automated Test"

    # Extract selectors and actions
    selectors = extract_selectors_from_history(history_data)
    actions = analyze_actions(history_data)

    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"

    # Create prompt for Playwright code
    # The code generation agent's description, instructions, and expected_output handle the code generation logic.
    # We provide the Gherkin steps and execution details as context.
    code_file_prompt = f"""
    Generate Playwright Python code based on the following:

    Gherkin Steps:
    ```gherkin
    {gherkin_steps}
    ```

    Agent Execution Details:
    - Base URL: {base_url}
    - Element Selectors: {json.dumps(selectors, indent=2)}
    - Actions Performed: {json.dumps(actions, indent=2)}
    - Extracted Content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
    """

    try:
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)

        return code_content

    except Exception as e:
        st.error(f"Error generating Playwright code: {str(e)}")
        raise

def generate_cypress_js(gherkin_steps: str, history_data: Dict[str, Any]) -> str:
    """Generate a single JavaScript file with Cypress automation code using the code generation agent"""

    # Extract feature name from Gherkin (optional, for context)
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    feature_name = feature_match.group(1).strip() if feature_match else "Automated Test"

    # Extract selectors and actions
    selectors = extract_selectors_from_history(history_data)
    actions = analyze_actions(history_data)

    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"

    # Create prompt for Cypress code
    # The code generation agent's description, instructions, and expected_output handle the code generation logic.
    # We provide the Gherkin steps and execution details as context.
    code_file_prompt = f"""
    Generate Cypress JavaScript code based on the following:

    Gherkin Steps:
    ```gherkin
    {gherkin_steps}
    ```

    Agent Execution Details:
    - Base URL: {base_url}
    - Element Selectors: {json.dumps(selectors, indent=2)}
    - Actions Performed: {json.dumps(actions, indent=2)}
    - Extracted Content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
    """

    try:
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)

        return code_content

    except Exception as e:
        st.error(f"Error generating Cypress code: {str(e)}")
        raise

def generate_robot_framework(gherkin_steps: str, history_data: Dict[str, Any]) -> str:
    """Generate Robot Framework test file using the code generation agent"""

    # Extract feature name from Gherkin (optional, for context)
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    feature_name = feature_match.group(1).strip() if feature_match else "Automated Test"

    # Extract selectors and actions
    selectors = extract_selectors_from_history(history_data)
    actions = analyze_actions(history_data)

    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"

    # Create prompt for Robot Framework code
    # The code generation agent's description, instructions, and expected_output handle the code generation logic.
    # We provide the Gherkin steps and execution details as context.
    code_file_prompt = f"""
    Generate Robot Framework code based on the following:

    Gherkin Steps:
    ```gherkin
    {gherkin_steps}
    ```

    Agent Execution Details:
    - Base URL: {base_url}
    - Element Selectors: {json.dumps(selectors, indent=2)}
    - Actions Performed: {json.dumps(actions, indent=2)}
    - Extracted Content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
    """

    try:
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)

        return code_content

    except Exception as e:
        st.error(f"Error generating Robot Framework code: {str(e)}")
        raise

def generate_java_selenium(gherkin_steps: str, history_data: Dict[str, Any]) -> str:
    """Generate a Java file with Selenium and Cucumber automation code using the code generation agent"""

    # Extract feature name from Gherkin (optional, for context)
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    feature_name = feature_match.group(1).strip() if feature_match else "Automated Test"

    # Extract selectors and actions
    selectors = extract_selectors_from_history(history_data)
    actions = analyze_actions(history_data)

    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"

    # Create prompt for Java Selenium Cucumber code
    # The code generation agent's description, instructions, and expected_output handle the code generation logic.
    # We provide the Gherkin steps and execution details as context.
    code_file_prompt = f"""
    Generate Java Selenium Cucumber code based on the following:

    Gherkin Steps:
    ```gherkin
    {gherkin_steps}
    ```

    Agent Execution Details:
    - Base URL: {base_url}
    - Element Selectors: {json.dumps(selectors, indent=2)}
    - Actions Performed: {json.dumps(actions, indent=2)}
    - Extracted Content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
    """

    try:
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)

        return code_content

    except Exception as e:
        st.error(f"Error generating Java Selenium Cucumber code: {str(e)}")
        raise
