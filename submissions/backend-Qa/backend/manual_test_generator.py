import os
import sys
import time
from agents.manual_testcase_agent import ManualTestCaseGenerator

def main():
    """
    Command-line interface for the Manual Test Case Generator
    """
    try:
        print("=" * 50)
        print("Manual Test Case Generator")
        print("=" * 50)
        
        # Get input from user
        prompt = input("Enter your requirement or user story: ")
        
        if not prompt:
            print("Error: No requirement provided")
            return
            
        # Initialize the generator
        generator = ManualTestCaseGenerator()
        
        # Generate test cases
        print("\nGenerating manual test cases...")
        start_time = time.time()
        
        # Add "Test Plan: " prefix if not already present to ensure correct processing
        if not prompt.startswith("Test Plan:"):
            prompt = "Test Plan: " + prompt
            
        result = generator.generate_from_user_story(prompt)
        
        end_time = time.time()
        
        if result['status'] == 'success':
            print(f"\nGeneration completed in {end_time - start_time:.2f} seconds")
            print(f"Generated {result['count']} test cases")
            print(f"Saved to: {result['file_path']}")
            
            # Display the first test case as a sample
            if result['test_cases'] and len(result['test_cases']) > 0:
                print("\nSample test case:")
                print("-" * 50)
                tc = result['test_cases'][0]
                print(f"Test Case ID: {tc.get('Test Case ID', 'Unknown')}")
                print(f"Description: {tc.get('Description', 'No description')}")
                print(f"Test Steps:\n{tc.get('Test Steps', 'No steps')}")
                print(f"Test Data Set 1:\n{tc.get('Test Data Set 1', 'No data')}")
                print(f"Expected Result:\n{tc.get('Expected Result', 'No expected result')}")
                
                print("\nAll test cases have been saved to the CSV file.")
        else:
            print(f"\nError: {result.get('message', 'Unknown error')}")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
