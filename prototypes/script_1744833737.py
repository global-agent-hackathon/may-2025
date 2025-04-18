Based on your request, I'll provide a simple Python script that prints "Hello World". This is a straightforward script, suitable for beginners or as a basic example of Python syntax.

Here's the Python script:

```python
# hello_world.py
# A simple script that prints "Hello World" to the console.

def print_hello_world():
    """
    This function prints "Hello World" to the standard output.
    """
    print("Hello World")

if __name__ == "__main__":
    print_hello_world()
```

### Explanation:
1. **Function `print_hello_world`**: This function, when called, executes the `print()` function to output the string "Hello World".
2. **`if __name__ == "__main__"`**: This line checks if the script is being run directly (not imported as a module in another script). If it is run directly, it calls the `print_hello_world()` function.

### How to run the script:
1. Save the above code in a file named `hello_world.py`.
2. Open your command-line interface (CLI).
3. Navigate to the directory where you saved `hello_world.py`.
4. Run the script by typing `python hello_world.py` and press Enter.

You should see "Hello World" printed in the console. This script is compatible with both Python 2 and Python 3 environments.