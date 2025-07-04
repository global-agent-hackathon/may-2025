import os
import re
import csv
import random
import string
import time
import pandas as pd
from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv

load_dotenv()

class ManualTestCaseGenerator:
    def __init__(self):
        """Initialize the Manual Test Case Generator with automatic settings"""
        # Optimized model configuration for better performance
        self.agent = Agent(
            model=Groq(
                id="deepseek-r1-distill-llama-70b",  # Keep the same model for output consistency
                temperature=0.7,
                max_tokens=2048,  # Increased max tokens to accommodate larger responses
                top_p=0.9,
                presence_penalty=0.1,
                frequency_penalty=0.1
            ),
            instructions="""You are a QA expert specializing in manual test case creation. Generate comprehensive manual test cases from user stories.
            Rules:
            1. Create detailed test cases with clear steps
            2. Include positive, negative, and edge cases
            3. Generate multiple test data variations
            4. Format output as specified
            5. Output ONLY the test cases, nothing else""",
            markdown=False
        )
        
        # Default timeout for API calls (in seconds)
        self.default_timeout = 60
        
        # Create base directories
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.test_cases_dir = os.path.join(self.base_dir, 'test_cases')
        os.makedirs(self.test_cases_dir, exist_ok=True)

    def _generate_from_user_story(self, user_story: str) -> dict:
        """
        Generate manual test cases from a user story with automatic settings
        
        Args:
            user_story: The user story to generate test cases from
            
        Returns:
            Dictionary containing:
            - status: 'success' or 'error'
            - test_cases: List of generated test cases
            - filename: Name of the generated CSV file
            - file_path: Full path to the generated CSV file
            - count: Number of test cases generated
        """
        try:
            # Validate input
            if not user_story or not isinstance(user_story, str):
                return self._error_response("Invalid user story provided")
                
            # Automatic settings
            iterations = self._determine_iterations(user_story)
            feature_name = self._generate_feature_name(user_story)
            
            print(f"Generating test cases for user story (iterations: {iterations})...")
            
            # Generate test cases
            test_cases = self._generate_test_cases(user_story, iterations)
            
            # Create output file
            output_file = os.path.join(self.test_cases_dir, f"{feature_name}.csv")
            saved_file = self._save_to_csv(test_cases, output_file)
            
            return {
                'status': 'success',
                'test_cases': test_cases,
                'filename': os.path.basename(saved_file),
                'file_path': saved_file,
                'count': len(test_cases)
            }
            
        except Exception as e:
            return self._error_response(f"Error generating test cases: {str(e)}")

    def generate_from_user_story(self, user_story: str) -> dict:
        """
        Generate manual test cases from a user story with automatic settings
        This is an alias method to maintain compatibility with agent_router.py
        
        Args:
            user_story: The user story to generate test cases from
            
        Returns:
            Dictionary containing test case generation results
        """
        return self._generate_from_user_story(user_story)
        
    def _determine_iterations(self, user_story: str) -> int:
        """
        Automatically determine number of improvement iterations based on user story complexity
        Optimized to reduce iterations for better performance
        
        Args:
            user_story: The user story to analyze
            
        Returns:
            Number of iterations (1-2)
        """
        word_count = len(user_story.split())
        if word_count < 50: return 1
        return 2  # Maximum of 2 iterations to reduce API calls while maintaining quality

    def _generate_feature_name(self, user_story: str) -> str:
        """
        Generate a sanitized feature name from the user story
        
        Args:
            user_story: The user story to generate name from
            
        Returns:
            Sanitized feature name
        """
        # Extract first few meaningful words
        words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', user_story)][:3]
        name = '_'.join(words) if words else 'test_cases'
        
        # Sanitize and truncate
        name = re.sub(r'[^\w\-]', '_', name)
        return name[:50]

    def _generate_test_cases(self, user_story: str, iterations: int) -> list:
        """
        Generate and iteratively improve test cases with timeout handling
        
        Args:
            user_story: The user story to generate from
            iterations: Number of improvement iterations
            
        Returns:
            List of parsed test cases
        """
        print(f"Starting test case generation for user story...")
        
        # Enhanced initial prompt with more specific requirements
        initial_prompt = f"""Convert this user story into detailed manual test cases with CONCRETE, SPECIFIC test data values:

{user_story}

For each test case, provide:
1. Test Case ID (format: TC_[number])
2. Description
3. Detailed Test Steps
4. 5 DIFFERENT Test Data sets (each must contain ACTUAL VALUES, not descriptions)
5. Expected Results for each data set

TEST DATA REQUIREMENTS:
- Each test data set must contain SPECIFIC VALUES that can be directly used in testing
- Never use generic descriptions like "valid data" or "invalid credentials"
- Always provide complete, concrete examples

Test Data Format Examples:
GOOD:
- "Username: admin@example.com, Password: Admin123!"
- "Age: 17 (below minimum allowed)"
- "Search term: 'café@123' (special characters)"
- "Credit card: 4111 1111 1111 1111 (test Visa number)"
- "File: empty.pdf (0 byte file)"

BAD:
- "Valid credentials"
- "Invalid data"
- "Edge case values"
- "Special characters"
- "Empty values"

Output format for each test case (include exactly these headers):
Test Case ID: [ID]
Description: [description]
Test Steps:
1. [step 1]
2. [step 2]
...
Test Data Set 1: [CONCRETE VALUES - e.g., "Username: test_user, Password: Pass123!"]
Test Data Set 2: [CONCRETE EDGE CASE VALUES - e.g., "Username: a, Password: 1"]
Test Data Set 3: [CONCRETE INVALID VALUES - e.g., "Username: <script>, Password: ' OR '1'='1"]
Test Data Set 4: [CONCRETE SPECIAL CHARACTER VALUES - e.g., "Username: jöhn.dœ@例.com, Password: P@$$wörd"]
Test Data Set 5: [CONCRETE EMPTY/NULL VALUES - e.g., "Username: (empty), Password: (empty)"]
Expected Result: [detailed expected result for each data set]"""

        # Initial generation with timeout handling
        try:
            print("Generating initial test cases...")
            response = self.agent.run(initial_prompt, timeout=self.default_timeout)
            content = response.content.strip() if response and response.content else ""
            
            if not content:
                print("Initial generation failed or returned empty content")
                return self._default_test_case()
                
            print(f"Initial test cases generated successfully")
        except Exception as e:
            print(f"Error during initial test case generation: {str(e)}")
            return self._default_test_case()
        
        # Enhanced iterative improvement with timeout handling
        for i in range(iterations - 1):
            try:
                print(f"Starting improvement iteration {i+1}...")
                content = self._improve_test_cases(content)
                print(f"Improvement iteration {i+1} completed")
            except Exception as e:
                print(f"Error during improvement iteration {i+1}: {str(e)}")
                # Continue with what we have so far rather than failing completely
                break
        
        # Parse and return
        print("Parsing final test cases...")
        parsed_cases = self._parse_test_cases(content)
        
        if not parsed_cases:
            print("Parsing failed, returning default test case")
            return self._default_test_case()
            
        print(f"Successfully generated {len(parsed_cases)} test cases")
        return parsed_cases

    def _improve_test_cases(self, content: str) -> str:
        """
        Improve existing test cases with focus on concrete test data
        Includes timeout handling and fallback mechanism
        
        Args:
            content: Current test cases content
            
        Returns:
            Improved test cases content
        """
        # Simplified prompt to reduce processing time while maintaining quality
        prompt = f"""Review and improve these test cases with STRICT FOCUS on making test data CONCRETE and SPECIFIC:
{content}

Required Improvements:
1. REPLACE ALL generic test data descriptions with ACTUAL VALUES
2. Ensure each test data set contains COMPLETE, USABLE VALUES
3. Make values realistic and representative of real-world scenarios

Examples of Required Improvements:
BAD: "Valid credentials"
GOOD: "Username: jane.doe@company.com, Password: Str0ngP@ss!2023"

BAD: "Invalid date"
GOOD: "Date: 31/02/2023 (invalid February date)"

BAD: "Special characters"
GOOD: "Search term: 'café@123_テスト' (mixed special chars)"

Output ONLY the improved test cases in the same format, with ALL test data sets containing CONCRETE VALUES."""

        try:
            # Add timeout to prevent indefinite waiting
            response = self.agent.run(prompt, timeout=self.default_timeout)
            improved_content = response.content.strip() if response and response.content else content
            
            # Fallback mechanism: if improved content is empty or much shorter than original,
            # it likely failed - return original content
            if not improved_content or len(improved_content) < len(content) * 0.5:
                print("Improvement returned suspiciously short content, using original content")
                return content
                
            return improved_content
        except Exception as e:
            print(f"Error during test case improvement: {str(e)}")
            # Return original content if improvement fails
            return content

    def _parse_test_cases(self, content: str) -> list:
        """
        Parse generated text into structured test cases with strict validation
        
        Args:
            content: Generated test cases text
            
        Returns:
            List of parsed test case dictionaries
        """
        if not content:
            return []
            
        test_case_blocks = re.split(r'\n\s*\n', content.strip())
        parsed_cases = []
        
        for block in test_case_blocks:
            case = {
                'Test Case ID': '',
                'Description': '',
                'Test Steps': '',
                'Test Data Set 1': '',
                'Test Data Set 2': '',
                'Test Data Set 3': '',
                'Test Data Set 4': '',
                'Test Data Set 5': '',
                'Expected Result': ''
            }
            
            current_field = None
            data_set_count = 0
            
            for line in block.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Field detection with strict validation
                if line.startswith('Test Case ID:'):
                    case['Test Case ID'] = line[13:].strip()
                elif line.startswith('Description:'):
                    case['Description'] = line[12:].strip()
                elif line.startswith('Test Steps:'):
                    current_field = 'Test Steps'
                elif line.startswith('Test Data Set 1:'):
                    current_field = 'Test Data Set 1'
                    data_set_count += 1
                    line = line[16:].strip()  # Remove the prefix
                elif line.startswith('Test Data Set 2:'):
                    current_field = 'Test Data Set 2'
                    data_set_count += 1
                    line = line[16:].strip()
                elif line.startswith('Test Data Set 3:'):
                    current_field = 'Test Data Set 3'
                    data_set_count += 1
                    line = line[16:].strip()
                elif line.startswith('Test Data Set 4:'):
                    current_field = 'Test Data Set 4'
                    data_set_count += 1
                    line = line[16:].strip()
                elif line.startswith('Test Data Set 5:'):
                    current_field = 'Test Data Set 5'
                    data_set_count += 1
                    line = line[16:].strip()
                elif line.startswith('Expected Result:'):
                    current_field = 'Expected Result'
                elif current_field:
                    if case[current_field]:
                        case[current_field] += '\n' + line
                    else:
                        case[current_field] = line
            
            # Validate that we got concrete test data
            if data_set_count < 5:
                for i in range(1, 6):
                    if f'Test Data Set {i}' not in case or not case[f'Test Data Set {i}']:
                        case[f'Test Data Set {i}'] = f"Missing concrete test data set {i}"
            
            if case['Test Case ID']:
                parsed_cases.append(case)
            
        return parsed_cases or self._default_test_case()
    
    def _default_test_case(self) -> list:
        """Return a default test case when generation fails"""
        print("Returning default test case due to generation failure")
        return [{
            'Test Case ID': 'TC_001',
            'Description': 'Default test case - generation failed',
            'Test Steps': '1. Check system response\n2. Verify expected behavior',
            'Test Data Set 1': 'Sample data 1',
            'Test Data Set 2': 'Sample data 2',
            'Test Data Set 3': 'Sample data 3',
            'Test Data Set 4': 'Sample data 4',
            'Test Data Set 5': 'Sample data 5',
            'Expected Result': 'System behaves as expected'
        }]

    def _save_to_csv(self, test_cases: list, output_file: str) -> str:
        """
        Save test cases to CSV file
        
        Args:
            test_cases: List of test case dictionaries
            output_file: Full path to output file
            
        Returns:
            Path to the saved file
        """
        if not test_cases:
            test_cases = self._default_test_case()
            
        # Ensure CSV extension
        if not output_file.lower().endswith('.csv'):
            output_file += '.csv'
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write CSV
        fieldnames = [
            'Test Case ID', 'Description', 'Test Steps',
            'Test Data Set 1', 'Test Data Set 2', 'Test Data Set 3',
            'Test Data Set 4', 'Test Data Set 5', 'Expected Result'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(test_cases)
            
        return output_file

    def _error_response(self, message: str) -> dict:
        """
        Create a standardized error response
        
        Args:
            message: Error message
            
        Returns:
            Error response dictionary
        """
        print(f"Error: {message}")
        return {
            'status': 'error',
            'message': message,
            'test_cases': self._default_test_case(),
            'filename': 'error_test_cases.csv',
            'file_path': '',
            'count': 0
        }