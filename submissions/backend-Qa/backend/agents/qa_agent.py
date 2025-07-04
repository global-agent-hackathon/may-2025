import os
import re
from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv

load_dotenv()

class QAAgent:
    def __init__(self):
        try:
            self.agent = Agent(
                model=Groq(
                    id="mixtral-8x7b-32768",  # Using the same model as before
                    temperature=0.7,
                    max_tokens=4000,
                    top_p=0.95
                ),
                instructions="""You are a QA automation expert. Generate Selenium test scripts.
                Follow these rules:
                1. Use Python with Selenium WebDriver
                2. Include proper waits and error handling
                3. Follow Page Object Model when appropriate
                4. Add clear comments and docstrings
                5. Handle edge cases and errors""",
                markdown=False
            )
        except Exception as e:
            print(f"Error initializing agent: {str(e)}")
            self.agent = None

    def generate_selenium_script(self, request_data: dict) -> dict:
        if not self.agent:
            return {'status': 'error', 'message': 'Agent not properly initialized'}
            
        try:
            requirement = request_data.get('requirement', '')
            if not requirement:
                return {'status': 'error', 'message': 'No requirement provided'}
                
            test_name = request_data.get('testName', 'test_default').strip()
            if not test_name.endswith('.py'):
                test_name += '.py'

            language = request_data.get('language', 'python').lower()
            if language != 'python':
                return {
                    'status': 'error',
                    'message': 'Currently only Python is supported for Selenium scripts'
                }

            prompt = f"""Generate a Selenium test script in Python for the following requirement:
            {requirement}

            Include:
            1. Proper setup and teardown
            2. WebDriverWait for elements
            3. Try-except blocks for error handling
            4. Clear comments and docstrings
            5. Page Object Model if appropriate"""

            response = self.agent.run(prompt)
            content = response.content.replace('<think>', '').replace('</think>', '')
            
            # Extract code from markdown if present
            code_match = re.search(r'```python\n(.+?)```', content, re.DOTALL)
            if code_match:
                content = code_match.group(1).strip()
            else:
                # Try to clean up the content if no code block is found
                content = content.replace('```', '').strip()

            os.makedirs('test_scripts', exist_ok=True)
            script_file = os.path.join('test_scripts', test_name)
            with open(script_file, 'w') as f:
                f.write(content)

            return {
                'status': 'success',
                'script_file': script_file,
                'content': content,
                'filename': test_name,
                'message': 'Selenium test script generated successfully'
            }

        except Exception as e:
            print(f"Error generating Selenium script: {str(e)}")
            return {'status': 'error', 'message': str(e)}
