import os
import time
import tiktoken
import json
from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv

load_dotenv()

class TestGeneratorAgent:
    def __init__(self):
        try:
            # Initialize token counter for debugging
            self.tokenizer = tiktoken.get_encoding("cl100k_base")  # Using OpenAI's encoding as an approximation
            self.max_input_tokens = 8192  # Default max input tokens
            self.max_output_tokens = 1024  # Default max output tokens
            
            self.agent = Agent(
                model=Groq(
                    id="deepseek-r1-distill-llama-70b",
                    temperature=0.6,
                    max_tokens=1024,
                    top_p=0.95
                ),
                instructions='''You are a BDD test expert specializing in automated testing. Generate comprehensive Gherkin feature files for any type of project.
        
        Follow these rules:
        1. Use Feature, Background (if needed), Scenario format
        2. Each scenario must have Given, When, Then steps that are clear and automatable
        3. Cover all major aspects of the feature:
           - Core functionality and workflows
           - Data validation and edge cases
           - Error scenarios and exception handling
           - API integrations if applicable
           - Database operations if relevant
           - UI interactions for frontend features
           - Performance considerations
        4. Make steps reusable and maintainable:
           - Use clear, consistent terminology
           - Keep steps atomic and focused
           - Use parameterization for test data
           - Include proper validation points
        5. Consider different testing types:
           - Functional testing
           - Integration testing
           - Security testing
           - Performance testing
           - Usability testing
        6. Include scenarios for:
           - Happy paths
           - Boundary conditions
           - Error conditions
           - Data variations
           - State transitions
           - Concurrent operations
           
        IMPORTANT - HANDLING MULTIPLE USER STORIES:
        1. If the input contains multiple user stories, create scenarios for EACH user story
        2. Don't skip any user stories - ensure ALL stories in the input are covered
        3. For each user story, create at least one complete scenario with Given/When/Then
        4. If you can't process all stories due to length constraints, focus on quality over quantity
           
        IMPORTANT - HANDLING PARTIAL INPUTS:
        1. If you receive input marked as a chunk or partial requirement, focus ONLY on generating scenarios relevant to that specific chunk
        2. For partial inputs, do not try to create a complete feature file - just generate relevant scenarios
        3. If the input indicates it's part of a larger document (e.g., "Chunk 2 of 5"), adapt your response to focus on that section only
        4. Always ensure each scenario is complete with Given/When/Then, even for partial inputs
        
        OUTPUT FORMATTING:
        1. Start with Feature: line followed by a clear feature name
        2. Include user story in As a/I want to/So that format when possible
        3. Use proper indentation for all Gherkin elements
        4. Group related scenarios together
        5. Use tags to categorize scenarios (@happy_path, @error_case, etc.)
        6. ALWAYS complete your scenarios - never leave a scenario without proper Given/When/Then steps
        7. NEVER truncate your output in the middle of a scenario''',
                markdown=False
            )
        except Exception as e:
            print(f"Error initializing agent: {str(e)}")
            self.agent = None

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string"""
        if not text:
            return 0
        return len(self.tokenizer.encode(text))
    
    def is_truncated(self, text: str, max_tokens: int) -> bool:
        """Check if text is likely truncated based on token count and content"""
        token_count = self.count_tokens(text)
        # Check if we're close to the max tokens (within 5%)
        close_to_limit = token_count > max_tokens * 0.95
        
        # Check for abrupt endings (no proper punctuation at the end)
        abrupt_ending = False
        if text and not text.rstrip().endswith(('.', '!', '?', ':', ';')):
            abrupt_ending = True
            
        # Check for incomplete Gherkin structure
        incomplete_structure = False
        if 'Scenario:' in text and not 'Then ' in text.split('Scenario:')[-1]:
            incomplete_structure = True
            
        return close_to_limit and (abrupt_ending or incomplete_structure)
    
    def clean_gherkin_content(self, content: str) -> str:
        """Clean up the generated content to remove thinking process and keep only Gherkin"""
        # Remove common markdown and thinking indicators
        content = content.replace('```gherkin', '').replace('```', '')
        content = content.replace('<think>', '').replace('</think>', '')
        content = content.replace('<div class="think">', '').replace('</div>', '')
        
        # Look for Feature: as the start of actual Gherkin content
        if 'Feature:' in content:
            # Find the first occurrence of 'Feature:'
            feature_index = content.find('Feature:')
            # Only keep content from 'Feature:' onwards
            content = content[feature_index:]
        
        return content.strip()

    def evaluate_and_improve(self, content: str, original_prompt: str = "") -> str:
        """Evaluate and improve the generated test cases"""
        if not self.agent:
            return content

        try:
            # Add the original prompt to provide context for improvement
            context = f"Original requirement: {original_prompt}\n\n" if original_prompt else ""
            
            eval_prompt = f"""{context}Improve this Gherkin feature file:

{content}

IMPORTANT: Output ONLY the improved feature file in Gherkin format.
Start with 'Feature:' and use proper Gherkin keywords.
Do not include any explanations or thoughts.

Add scenarios for:
1. Missing edge cases and error conditions
2. Data validation and boundary tests
3. Security and performance tests
4. Integration tests with external systems
5. Concurrent operations and state changes"""

            response = self.agent.run(eval_prompt)
            improved_content = response.content
            
            # Clean up the response
            improved_content = self.clean_gherkin_content(improved_content)
            
            return improved_content
        except Exception as e:
            print(f"Error during improvement: {str(e)}")
            return content

    def generate_gherkin(self, request_data: dict) -> dict:
        if not self.agent:
            return {'status': 'error', 'message': 'Agent not properly initialized'}

        try:
            # Get the prompt from either requirement or text field
            prompt = request_data.get('requirement', '')
            if not prompt:
                prompt = request_data.get('text', '')
                
            if not prompt:
                return {'status': 'error', 'message': 'No requirement provided'}
            
            # Log token count for debugging
            input_token_count = self.count_tokens(prompt)
            print(f"DEBUG - Input token count: {input_token_count} tokens")
            
            # Check if input is likely to be truncated
            input_truncated = input_token_count > self.max_input_tokens
            if input_truncated:
                print(f"WARNING - Input may be truncated! {input_token_count} tokens exceeds limit of {self.max_input_tokens}")

            # Get feature name or use default
            feature_name_value = request_data.get('featureName')
            if feature_name_value:
                feature_name = str(feature_name_value).strip()
            else:
                feature_name = f"feature_{int(time.time())}"
                
            if not feature_name.endswith('.feature'):
                feature_name += '.feature'

            print(f"Generating test cases for: {prompt[:100]}...")
            
            # Get the number of iterations for improvement
            iterations = request_data.get('iterations', 2)
            try:
                iterations = int(iterations)
                iterations = max(1, min(3, iterations))  # Ensure between 1-3
            except (ValueError, TypeError):
                iterations = 2

            # Create a log file for token debugging
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"token_debug_{int(time.time())}.json")
            
            # Initialize token debug info
            token_debug = {
                "input": {
                    "total_tokens": input_token_count,
                    "truncated": input_truncated,
                    "max_tokens": self.max_input_tokens
                },
                "prompts": [],
                "responses": []
            }
            
            # Step 1: Generate feature header and basic structure
            header_prompt = f"""Generate ONLY the Feature header and description for: {prompt}
            Include Feature name, user story (As a, I want to, So that), and Background if needed.
            Do NOT include any scenarios yet.
            Example format:
            Feature: Name
              As a ...
              I want to ...
              So that ...

              Background:
                Given ...
            """
            
            header_prompt_tokens = self.count_tokens(header_prompt)
            token_debug["prompts"].append({
                "name": "header",
                "tokens": header_prompt_tokens,
                "truncated": header_prompt_tokens > self.max_input_tokens
            })
            print(f"DEBUG - Header prompt: {header_prompt_tokens} tokens")
            
            response = self.agent.run(header_prompt)
            feature_header = self.clean_gherkin_content(response.content)
            header_response_tokens = self.count_tokens(response.content)
            header_truncated = self.is_truncated(response.content, self.max_output_tokens)
            token_debug["responses"].append({
                "name": "header",
                "tokens": header_response_tokens,
                "truncated": header_truncated
            })
            print(f"DEBUG - Header response: {header_response_tokens} tokens, truncated: {header_truncated}")
            
            # Step 2: Generate scenarios in batches to avoid token limits
            scenarios_prompt = f"""Generate 3-4 essential Gherkin scenarios for: {prompt}
            Do NOT include the Feature header or description.
            Start directly with @tags and Scenario: for each scenario.
            Focus on the most important core functionality and happy paths.
            Example format:
              @tag
              Scenario: Name
                Given ...
                When ...
                Then ...
            """
            
            scenarios_prompt_tokens = self.count_tokens(scenarios_prompt)
            token_debug["prompts"].append({
                "name": "scenarios",
                "tokens": scenarios_prompt_tokens,
                "truncated": scenarios_prompt_tokens > self.max_input_tokens
            })
            print(f"DEBUG - Scenarios prompt: {scenarios_prompt_tokens} tokens")
            
            response = self.agent.run(scenarios_prompt)
            core_scenarios = self.clean_gherkin_content(response.content)
            scenarios_response_tokens = self.count_tokens(response.content)
            scenarios_truncated = self.is_truncated(response.content, self.max_output_tokens)
            token_debug["responses"].append({
                "name": "scenarios",
                "tokens": scenarios_response_tokens,
                "truncated": scenarios_truncated
            })
            print(f"DEBUG - Scenarios response: {scenarios_response_tokens} tokens, truncated: {scenarios_truncated}")
            
            # Step 3: Generate edge cases and error scenarios
            edge_cases_prompt = f"""Generate 3-4 additional Gherkin scenarios for: {prompt}
            Focus ONLY on edge cases, validation errors, and security concerns.
            Do NOT include the Feature header or description.
            Start directly with @tags and Scenario: for each scenario.
            Example format:
              @tag
              Scenario: Name
                Given ...
                When ...
                Then ...
            """
            
            edge_cases_prompt_tokens = self.count_tokens(edge_cases_prompt)
            token_debug["prompts"].append({
                "name": "edge_cases",
                "tokens": edge_cases_prompt_tokens,
                "truncated": edge_cases_prompt_tokens > self.max_input_tokens
            })
            print(f"DEBUG - Edge cases prompt: {edge_cases_prompt_tokens} tokens")
            
            response = self.agent.run(edge_cases_prompt)
            edge_scenarios = self.clean_gherkin_content(response.content)
            edge_cases_response_tokens = self.count_tokens(response.content)
            edge_cases_truncated = self.is_truncated(response.content, self.max_output_tokens)
            token_debug["responses"].append({
                "name": "edge_cases",
                "tokens": edge_cases_response_tokens,
                "truncated": edge_cases_truncated
            })
            print(f"DEBUG - Edge cases response: {edge_cases_response_tokens} tokens, truncated: {edge_cases_truncated}")
            
            # Combine all parts
            content = feature_header
            if not content.endswith('\n'):
                content += '\n\n'
            else:
                content += '\n'
                
            content += core_scenarios
            
            if not content.endswith('\n'):
                content += '\n\n'
            else:
                content += '\n'
                
            content += edge_scenarios
            
            # Calculate combined content token count
            combined_content_tokens = self.count_tokens(content)
            token_debug["combined"] = {
                "tokens": combined_content_tokens,
                "truncated": False  # Will be updated after improvement
            }
            print(f"DEBUG - Combined content: {combined_content_tokens} tokens")
            
            # Iteratively improve the combined content if needed
            if iterations > 0:
                print(f"Evaluating and improving test cases...")
                improve_prompt = f"Original requirement: {prompt}\n\nImprove this Gherkin feature file:\n\n{content}"
                improve_prompt_tokens = self.count_tokens(improve_prompt)
                token_debug["prompts"].append({
                    "name": "improve",
                    "tokens": improve_prompt_tokens,
                    "truncated": improve_prompt_tokens > self.max_input_tokens
                })
                print(f"DEBUG - Improvement prompt: {improve_prompt_tokens} tokens")
                
                content = self.evaluate_and_improve(content, prompt)
                
                improved_content_tokens = self.count_tokens(content)
                improved_truncated = self.is_truncated(content, self.max_output_tokens)
                token_debug["responses"].append({
                    "name": "improve",
                    "tokens": improved_content_tokens,
                    "truncated": improved_truncated
                })
                token_debug["combined"]["tokens"] = improved_content_tokens
                token_debug["combined"]["truncated"] = improved_truncated
                print(f"DEBUG - Improved content: {improved_content_tokens} tokens, truncated: {improved_truncated}")
            
            # Format the content properly
            lines = content.split('\n')
            formatted_lines = []
            current_section = None
                
            for line in lines:
                line = line.strip()
                if not line:
                    formatted_lines.append('')
                    continue
                    
                if line.startswith('Feature:'):
                    formatted_lines.append(line)
                    current_section = 'feature'
                elif line.startswith('As a') or line.startswith('I want') or line.startswith('So that'):
                    formatted_lines.append(line)
                elif line.startswith('Scenario:') or line.startswith('Scenario Outline:'):
                    if formatted_lines and formatted_lines[-1] != '':
                        formatted_lines.append('')
                    formatted_lines.append('  ' + line)
                    current_section = 'scenario'
                elif line.startswith('Given') or line.startswith('When') or line.startswith('Then') or line.startswith('And') or line.startswith('But'):
                    formatted_lines.append('    ' + line)
                elif line.startswith('|'):
                    formatted_lines.append('      ' + line)
                elif line.startswith('Examples:'):
                    formatted_lines.append('    ' + line)
                elif line.startswith('@'):
                    if formatted_lines and formatted_lines[-1] != '':
                        formatted_lines.append('')
                    formatted_lines.append('  ' + line)
                elif line.startswith('Background:'):
                    if formatted_lines and formatted_lines[-1] != '':
                        formatted_lines.append('')
                    formatted_lines.append('  ' + line)
                    current_section = 'background'
                elif line:
                    if current_section == 'feature':
                        formatted_lines.append(line)
                    else:
                        formatted_lines.append('    ' + line)
            
            content = '\n'.join(formatted_lines)
            
            # Save the feature file
            os.makedirs('features', exist_ok=True)
            feature_file = os.path.join('features', feature_name)
            with open(feature_file, 'w') as f:
                f.write(content)
                
            # Save token debug info to log file
            with open(log_file, 'w') as f:
                json.dump(token_debug, f, indent=2)
                
            # Add token debug info to response
            return {
                'status': 'success',
                'content': content,
                'feature_file': feature_file,
                'filename': feature_name,
                'message': 'Test cases generated successfully',
                'token_debug': {
                    'input_tokens': input_token_count,
                    'output_tokens': token_debug["combined"]["tokens"],
                    'input_truncated': input_truncated,
                    'output_truncated': token_debug["combined"]["truncated"],
                    'log_file': log_file
                }
            }

        except Exception as e:
            print(f"Error during generation: {str(e)}")
            # Fallback to a very simple generation
            basic_content = f"Feature: {feature_name.replace('.feature', '')}\n\n"
            basic_content += "  Scenario: Basic functionality\n"
            basic_content += "    Given the system is ready\n"
            basic_content += "    When the user performs the requested action\n"
            basic_content += "    Then the expected result should occur\n\n"
            basic_content += "  Scenario: Error handling\n"
            basic_content += "    Given the system is ready\n"
            basic_content += "    When invalid input is provided\n"
            basic_content += "    Then an appropriate error message should be displayed"
            
            os.makedirs('features', exist_ok=True)
            feature_file = os.path.join('features', feature_name)
            with open(feature_file, 'w') as f:
                f.write(basic_content)
                
            return {
                'status': 'success',
                'content': basic_content,
                'feature_file': feature_file,
                'filename': feature_name,
                'message': 'Basic test cases generated (fallback mode)'
            }

# Add this if you want to enable command-line usage
def main():
    try:
        agent = TestGeneratorAgent()
        prompt = input("Enter your requirement: ")
        name = input("Enter feature name (without .feature): ")
        iterations = int(input("Number of improvement iterations (1-3, default 2): ") or "2")
        iterations = max(1, min(3, iterations))  # Ensure between 1-3
        
        request_data = {
            'requirement': prompt,
            'featureName': name,
            'iterations': iterations
        }
        
        result = agent.generate_gherkin(request_data)
        
        if result['status'] == 'success':
            print(f"\nGenerated and improved: {result['feature_file']}")
            print("\nFinal test cases:")
            print("=" * 50)
            print(result['content'])
        else:
            print(f"Error: {result['message']}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()