import os
import re
import time
import traceback
from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv

load_dotenv()

class SeleniumGeneratorAgent:
    def __init__(self):
        try:
            self.agent = Agent(
                model=Groq(
                    id="llama-3.3-70b-versatile",
                    temperature=0.7,
                    max_tokens=1024,
                    top_p=0.9,
                    presence_penalty=0.1,
                    frequency_penalty=0.1
                ),
                instructions="""Generate a complete Selenium test script based on Gherkin scenarios. Follow these guidelines:
                1. Include proper imports (selenium webdriver, pytest, etc.)
                2. Use explicit waits with WebDriverWait
                3. Include proper By selectors and assertions
                4. Handle driver setup and cleanup
                5. Add proper error handling
                6. Follow Selenium best practices""",
                markdown=False
            )
        except Exception as e:
            print(f"Error initializing agent: {str(e)}")
            self.agent = None

    def generate_selenium_script(self, request_data: dict) -> dict:
        if not self.agent:
            return {'status': 'error', 'message': 'Agent not properly initialized'}

        try:
            print("Starting Selenium script generation...")
            prompt = request_data.get('requirement', '')
            if not prompt:
                return {'status': 'error', 'message': 'No requirement provided'}

            # Get test name or use default, ensuring it's a string before calling strip()
            test_name_value = request_data.get('testName')
            if test_name_value:
                test_name = str(test_name_value).strip()
            else:
                test_name = f"test_{int(time.time())}"
            if not test_name.endswith('.py'):
                test_name += '.py'

            language = request_data.get('language', 'python').lower()
            
            # Check if the language is supported
            if language != 'python':
                return {
                    'status': 'error', 
                    'message': f'Language "{language}" is not currently supported for Selenium scripts. Only Python is supported at this time.'
                }

            print(f"Generating Selenium script for: {prompt}")
            generation_prompt = f"""Create a Selenium test script for the following scenario: {prompt}

            Requirements:
            1. Use pytest with Selenium WebDriver
            2. Include proper imports and fixtures
            3. Use explicit waits with WebDriverWait
            4. Include proper By selectors and assertions
            5. Handle driver setup and cleanup
            6. Add proper error handling
            7. Follow Selenium best practices
            8. Make sure the code is complete and runnable"""

            response = self.agent.run(generation_prompt)
            content = response.content.replace('<think>', '').replace('</think>', '')
            
            # Extract code from markdown if present
            code_match = re.search(r'```python\n(.+?)```', content, re.DOTALL)
            if code_match:
                content = code_match.group(1).strip()
            else:
                # Try to clean up the content if no code block is found
                content = content.replace('```', '').strip()
            
            # Add default imports if missing to ensure it's a valid Python script
            if not content.startswith('import ') and not content.startswith('from '):
                default_imports = """from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

"""
                content = default_imports + content

            os.makedirs('features', exist_ok=True)
            script_file = os.path.join('features', test_name)
            with open(script_file, 'w') as f:
                f.write(content)

            print(f"Successfully generated Selenium script: {script_file}")
            return {
                'status': 'success',
                'content': content,
                'feature_file': script_file,
                'filename': test_name,
                'message': 'Selenium script generated successfully'
            }

        except Exception as e:
            print(f"Error generating Selenium script: {str(e)}")
            traceback.print_exc()
            return {'status': 'error', 'message': f'Failed to generate Selenium script: {str(e)}'}
