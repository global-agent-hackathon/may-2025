import re
from .qa_agent import QAAgent
from .test_generator_agent import TestGeneratorAgent
from .selenium_generator_agent import SeleniumGeneratorAgent
from .chat_agent import ChatAgent
from .manual_testcase_agent import ManualTestCaseGenerator

class AgentRouter:
    def __init__(self):
        self.qa_agent = QAAgent()
        self.test_generator = TestGeneratorAgent()
        self.selenium_generator = SeleniumGeneratorAgent()
        self.chat_agent = ChatAgent()
        self.manual_testcase_generator = ManualTestCaseGenerator()

    def is_valid_request(self, text):
        """Validates if the request text is meaningful enough to process."""
        if not text or not isinstance(text, str):
            return False
            
        # Check if text is too short
        if len(text.strip()) < 5:
            return False
            
        # Check if text is just random characters
        # Count meaningful words (at least 3 letters)
        words = text.split()
        meaningful_words = [w for w in words if len(w) >= 3 and re.match(r'^[a-zA-Z]+$', w)]
        
        # If less than 30% of words are meaningful, reject
        if len(words) >= 3 and len(meaningful_words) / len(words) < 0.3:
            return False
            
        # Check for common test-related keywords
        test_keywords = [
            'test', 'login', 'page', 'user', 'password', 'click', 'button', 
            'input', 'field', 'verify', 'check', 'validate', 'scenario', 
            'feature', 'given', 'when', 'then', 'selenium', 'script', 'generate'
        ]
        
        # If text contains at least one test-related keyword, it's more likely to be valid
        for keyword in test_keywords:
            if keyword.lower() in text.lower():
                return True
                
        # If we get here, do a final length check - longer texts are more likely to be valid
        return len(text.strip()) > 15
    
    def route_request(self, request_data: dict) -> dict:
        try:
            print(f"Received request data: {request_data}")

            if not isinstance(request_data, dict):
                return {'status': 'error', 'message': 'Invalid request format'}

            agent_type = request_data.get('agentType', '').lower()
            print(f"Agent type: {agent_type}")

            requirement = request_data.get('requirement', '')
            text = request_data.get('text', '')
            
            if not requirement and not text:
                return {'status': 'error', 'message': 'No requirement or text provided'}
            
            # Check if this is a chunked request and add context to the requirement
            chunk_info = request_data.get('chunkInfo', None)
            if chunk_info and chunk_info.get('isChunk', False):
                chunk_num = chunk_info.get('chunkNumber', 0)
                total_chunks = chunk_info.get('totalChunks', 0)
                print(f"Processing chunk {chunk_num} of {total_chunks}")
                
                # Add chunk information to the requirement text
                if requirement:
                    request_data['requirement'] = f"[PARTIAL INPUT - CHUNK {chunk_num} OF {total_chunks}]\n\n{requirement}"
                elif text:
                    request_data['text'] = f"[PARTIAL INPUT - CHUNK {chunk_num} OF {total_chunks}]\n\n{text}"
                    
                # Update for logging
                requirement = request_data.get('requirement', '')
                text = request_data.get('text', '')
                
            # Validate the input text
            input_text = requirement or text
            if not self.is_valid_request(input_text):
                return {
                    'status': 'error',
                    'message': 'Please provide a meaningful request related to testing. Your input appears to be random text or too short.'
                }

            if agent_type == 'test_generator' or agent_type == 'gherkin':
                print("Routing to test generator agent")
                return self.test_generator.generate_gherkin(request_data)

            elif agent_type == 'selenium_generator' or agent_type == 'selenium':
                print("Routing to selenium generator agent")
                try:
                    # Check language parameter
                    language = request_data.get('language', 'python').lower()
                    if language == 'java':
                        return {
                            'status': 'error',
                            'message': 'Java Selenium Script Generator is currently under development. Please use Python for Selenium scripts for now.'
                        }
                    
                    result = self.selenium_generator.generate_selenium_script(request_data)
                    print(f"Selenium generator result: {result['status']}")
                    return result
                except Exception as e:
                    print(f"Error in selenium generator: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return {'status': 'error', 'message': f'Error in selenium generator: {str(e)}'}

                    
            elif agent_type == 'playwright':
                print("Routing to playwright generator agent")
                try:
                    # Assuming we have a playwright generator agent
                    # For now, we'll use the selenium generator with a note
                    request_data['note'] = 'Using Selenium format as a base for Playwright'
                    result = self.selenium_generator.generate_selenium_script(request_data)
                    print(f"Playwright generator result: {result['status']}")
                    return result
                except Exception as e:
                    print(f"Error in playwright generator: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return {'status': 'error', 'message': f'Error in playwright generator: {str(e)}'}
                    
            elif agent_type == 'cypress':
                print("Routing to cypress generator agent")
                try:
                    # Assuming we have a cypress generator agent
                    # For now, we'll use the selenium generator with a note
                    request_data['note'] = 'Using Selenium format as a base for Cypress'
                    result = self.selenium_generator.generate_selenium_script(request_data)
                    print(f"Cypress generator result: {result['status']}")
                    return result
                except Exception as e:
                    print(f"Error in cypress generator: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return {'status': 'error', 'message': f'Error in cypress generator: {str(e)}'}
                    
            elif agent_type == 'behave':
                print("Routing to behave generator agent")
                try:
                    # Assuming we have a behave generator agent
                    # For now, we'll use the selenium generator with a note
                    request_data['note'] = 'Using Selenium format as a base for Behave'
                    result = self.selenium_generator.generate_selenium_script(request_data)
                    print(f"Behave generator result: {result['status']}")
                    return result
                except Exception as e:
                    print(f"Error in behave generator: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return {'status': 'error', 'message': f'Error in behave generator: {str(e)}'}
                    
            elif agent_type == 'chat':
                print("Routing to chat agent")
                try:
                    result = self.chat_agent.generate_response(request_data)
                    print(f"Chat agent result: {result['status']}")
                    return result
                except Exception as e:
                    print(f"Error in chat agent: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return {'status': 'error', 'message': f'Error in chat agent: {str(e)}'}

            elif agent_type == 'manual_testcases':
                print("Routing to manual test case generator agent")
                try:
                    # Extract user story from requirement field
                    user_story = ''
                    if 'requirement' in request_data:
                        user_story = request_data['requirement']
                    elif 'user_story' in request_data:
                        user_story = request_data['user_story']
                    elif 'text' in request_data:
                        user_story = request_data['text']
                        
                    if not user_story:
                        return {
                            'status': 'error',
                            'message': 'No user story or requirement provided for manual test case generation'
                        }
                    
                    # Call the new method with just the user story string
                    result = self.manual_testcase_generator.generate_from_user_story(user_story)
                    
                    # Format the response to match the expected format by frontend
                    if 'status' in result and result['status'] == 'success':
                        # Convert test_cases to content format expected by frontend
                        if 'test_cases' in result:
                            content = self._format_test_cases_for_display(result['test_cases'])
                            result['content'] = content
                        
                        # Add message if not present
                        if 'message' not in result:
                            result['message'] = 'Manual test cases generated successfully'
                            
                        # Map file_path to feature_file for compatibility
                        if 'file_path' in result and 'feature_file' not in result:
                            result['feature_file'] = result['file_path']
                    
                    print(f"Manual test case generator result: {result['status']}")
                    return result
                except Exception as e:
                    print(f"Error in manual test case generator: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return {'status': 'error', 'message': f'Error in manual test case generator: {str(e)}'}
                    
            elif agent_type == 'manual_planning':
                print("Routing to manual test planning agent")
                try:
                    # Extract user story from requirement field
                    user_story = ''
                    if 'requirement' in request_data:
                        user_story = request_data['requirement']
                    elif 'user_story' in request_data:
                        user_story = request_data['user_story']
                    elif 'text' in request_data:
                        user_story = request_data['text']
                        
                    if not user_story:
                        return {
                            'status': 'error',
                            'message': 'No user story or requirement provided for test planning'
                        }
                    
                    # Prefix with Test Plan indicator
                    user_story = "Test Plan: " + user_story
                    
                    # Call the new method with just the user story string
                    result = self.manual_testcase_generator.generate_from_user_story(user_story)
                    
                    # Format the response to match the expected format by frontend
                    if 'status' in result and result['status'] == 'success':
                        # Convert test_cases to content format expected by frontend
                        if 'test_cases' in result:
                            content = self._format_test_cases_for_display(result['test_cases'])
                            result['content'] = content
                        
                        # Add message if not present
                        if 'message' not in result:
                            result['message'] = 'Test plan generated successfully'
                            
                        # Map file_path to feature_file for compatibility
                        if 'file_path' in result and 'feature_file' not in result:
                            result['feature_file'] = result['file_path']
                    
                    print(f"Manual test planning result: {result['status']}")
                    return result
                except Exception as e:
                    print(f"Error in manual test planning: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return {'status': 'error', 'message': f'Error in manual test planning: {str(e)}'}
                    
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown agent type: {agent_type}. Supported types: gherkin, selenium, playwright, cypress, behave, chat, manual_testcases, manual_planning'
                }

        except Exception as e:
            print(f"Error in router: {str(e)}")
            return {'status': 'error', 'message': f'Internal error: {str(e)}'}
            
    def _format_test_cases_for_display(self, test_cases):
        """Format test cases for display in the frontend"""
        if not test_cases:
            return "No test cases generated."
            
        formatted_content = ""
        for tc in test_cases:
            formatted_content += f"Test Case ID: {tc.get('Test Case ID', 'TC_Unknown')}\n"
            formatted_content += f"Description: {tc.get('Description', '')}\n"
            formatted_content += f"Test Steps:\n{tc.get('Test Steps', '')}\n"
            formatted_content += f"Test Data Set 1:\n{tc.get('Test Data Set 1', '')}\n"
            formatted_content += f"Expected Result:\n{tc.get('Expected Result', '')}\n\n"
        
        return formatted_content
