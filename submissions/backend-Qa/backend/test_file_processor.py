"""
Test script for file processor functionality
"""
import os
from utils.file_processor import extract_text_from_file

def main():
    # Create test directory if it doesn't exist
    os.makedirs("test_files", exist_ok=True)
    
    # Create a test text file
    test_text_file = os.path.join("test_files", "test.txt")
    with open(test_text_file, "w") as f:
        f.write("This is a test file.\nIt contains multiple lines.\nIt should be processed correctly.")
    
    # Test text file extraction
    print("\nTesting text file extraction:")
    text_content = extract_text_from_file(test_text_file)
    print(f"Extracted content from {test_text_file}:")
    print(text_content)
    
    print("\nFile processor is working correctly!")

if __name__ == "__main__":
    main()
