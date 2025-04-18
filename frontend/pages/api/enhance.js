import { exec } from 'child_process';
import path from 'path';
import util from 'util';

const execPromise = util.promisify(exec);

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method Not Allowed' });
  }

  const { prompt } = req.body;

  if (!prompt) {
    return res.status(400).json({ message: 'Prompt is required' });
  }

  // Adjust the path to your Python executable and script as needed
  const pythonExecutable = 'python'; // Or 'python3', or absolute path
  // Assuming generate.py is in the 'backend' directory relative to project root
  const scriptPath = path.resolve(process.cwd(), '..', 'backend', 'generate.py'); 
  // Escape the prompt for shell command execution
  const escapedPrompt = prompt.replace(/'/g, "'\\''"); 

  try {
    // Execute the Python script, passing the prompt as a command-line argument
    // The script should print the enhanced prompt to stdout
    const command = `${pythonExecutable} ${scriptPath} --enhance '${escapedPrompt}'`;
    console.log(`Executing command: ${command}`); // Log the command for debugging

    const { stdout, stderr } = await execPromise(command, { timeout: 30000 }); // 30 second timeout

    if (stderr) {
      console.error(`Python script error: ${stderr}`);
      // Don't return internal errors directly to the client for security
      return res.status(500).json({ message: 'Error enhancing prompt' });
    }

    // Assuming the Python script prints *only* the enhanced prompt to stdout
    const enhancedPrompt = stdout.trim();
    
    console.log(`Enhanced prompt received: ${enhancedPrompt}`); // Log success
    res.status(200).json({ enhancedPrompt });

  } catch (error) {
    console.error(`Execution error: ${error}`);
    // Distinguish between script errors (stderr) and execution errors (catch block)
    if (error.stderr) {
       console.error(`Python script error (from catch): ${error.stderr}`);
    }
    res.status(500).json({ message: 'Failed to execute enhancement script' });
  }
} 