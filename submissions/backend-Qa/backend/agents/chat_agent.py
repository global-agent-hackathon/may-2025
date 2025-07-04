import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ChatAgent:
    def __init__(self):
        # Get API key from environment
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not found in environment variables")
            self.api_key = "dummy_key"  # Placeholder for testing
            
        # Set the API key for OpenAI
        openai.api_key = self.api_key
        
        # Default model to use
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
    def generate_response(self, request_data):
        """
        Generate a response to a chat message using OpenAI's API.
        
        Args:
            request_data (dict): Dictionary containing the request data including:
                - requirement: The user's message
                - context: Optional context for the conversation
                
        Returns:
            dict: Response containing status, content, and message
        """
        try:
            # Extract data from request
            user_message = request_data.get('requirement', '')
            context = request_data.get('context', 'QA Testing')
            
            if not user_message:
                return {
                    'status': 'error',
                    'message': 'No message provided'
                }
            
            # Create system message with context
            system_message = f"You are a helpful assistant specializing in {context}. Provide concise, accurate, and helpful responses."
            
            # Call OpenAI API
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                # Extract response content
                response_content = response.choices[0].message.content.strip()
                
                return {
                    'status': 'success',
                    'content': response_content,
                    'message': 'Response generated successfully'
                }
                
            except Exception as e:
                print(f"Error calling OpenAI API: {str(e)}")
                
                # Fallback response if API call fails
                fallback_response = self._generate_fallback_response(user_message, context)
                
                return {
                    'status': 'success',
                    'content': fallback_response,
                    'message': 'Generated fallback response due to API error'
                }
                
        except Exception as e:
            print(f"Error in chat agent: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error generating response: {str(e)}'
            }
            
    def _generate_fallback_response(self, user_message, context):
        """Generate a fallback response when the API call fails"""
        
        # Simple keyword-based response
        keywords = {
            'help': "I'm here to help with your QA testing needs. What specific assistance do you need?",
            'test': "Testing is a critical part of the software development lifecycle. What kind of tests are you working on?",
            'gherkin': "Gherkin is a language that helps you describe software behavior without detailing how that behavior is implemented.",
            'selenium': "Selenium is a popular tool for automating web browsers, often used for testing web applications.",
            'playwright': "Playwright is a framework for Web Testing and Automation that allows testing across all modern browsers.",
            'cypress': "Cypress is a front end testing tool built for the modern web, making asynchronous testing simple.",
            'behave': "Behave is a BDD (Behavior-Driven Development) testing framework for Python.",
            'feature': "Feature files in Gherkin describe a single feature of the system using scenarios and steps.",
            'scenario': "Scenarios in Gherkin describe a specific business situation using steps with Given, When, Then format."
        }
        
        # Check for keywords in user message
        for keyword, response in keywords.items():
            if keyword.lower() in user_message.lower():
                return response
                
        # Default fallback response
        return f"I understand you're asking about {context}. Could you provide more details so I can assist you better?"
