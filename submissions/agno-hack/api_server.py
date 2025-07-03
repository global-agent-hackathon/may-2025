import os
import json
import asyncio
import sys
import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Agno imports
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools import tool

# Browser-use imports
from langchain_google_genai import ChatGoogleGenerativeAI
import browser_use
from browser_use import Browser, BrowserConfig, Controller, ActionResult
from browser_use.browser.context import BrowserContextConfig

# Load environment variables
load_dotenv()

# FastAPI app initialization
app = FastAPI(
    title="Website Testing Agent API",
    description="AI-powered website testing and automation API",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fetch the Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found in .env file or environment variables.")

# Create operation_logs directory and serve static files
logs_dir = Path("./operation_logs")
screenshots_dir = logs_dir / "screenshots"
logs_dir.mkdir(exist_ok=True)
screenshots_dir.mkdir(exist_ok=True)

# Mount static files for serving screenshots
app.mount("/screenshots", StaticFiles(directory=str(screenshots_dir)), name="screenshots")

# Pydantic models for API requests and responses
class ScreenshotInstruction(BaseModel):
    step_description: str
    filename: str

class TestInstructions(BaseModel):
    target_url: str
    task_description: str
    screenshot_instructions: List[ScreenshotInstruction]

class TaskStatus(BaseModel):
    task_id: str
    status: str  # "pending", "running", "completed", "failed"
    progress: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class ExecutionResult(BaseModel):
    task_id: str
    success: bool
    timestamp: str
    task_details: Dict
    execution_steps: List[Dict]
    screenshots: List[str]
    error: Optional[str] = None
    log_file: Optional[str] = None

class AnalysisResult(BaseModel):
    task_id: str
    analysis_report: Dict
    recommendations: List[str]
    compliance_check: Dict

# In-memory storage for task status (use Redis/DB in production)
task_storage = {}

class BrowserExecutor:
    """Direct browser automation executor using browser-use library."""
    
    def __init__(self):
        self.logs_dir = Path("./operation_logs")
        self.screenshots_dir = Path("./operation_logs/screenshots")
        self.logs_dir.mkdir(exist_ok=True)
        self.screenshots_dir.mkdir(exist_ok=True)
        
    def setup_detailed_logging(self, task_id: str):
        """Setup comprehensive logging for the agent execution."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = self.logs_dir / f"detailed_agent_log_{task_id}_{timestamp}.txt"
        
        # Create a custom logger
        logger = logging.getLogger(f"agent_{task_id}")
        logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger, log_file_path
    
    def capture_stdout_stderr(self, task_id: str):
        """Capture stdout and stderr to log everything the agent outputs."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stdout_log_path = self.logs_dir / f"agent_stdout_{task_id}_{timestamp}.txt"
        stderr_log_path = self.logs_dir / f"agent_stderr_{task_id}_{timestamp}.txt"
        
        # Backup original stdout/stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        # Create file objects for capturing output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Custom stdout/stderr that writes to both original and capture
        class TeeOutput:
            def __init__(self, original, capture, log_file):
                self.original = original
                self.capture = capture
                self.log_file = log_file
                
            def write(self, text):
                self.original.write(text)
                self.capture.write(text)
                # Also write to file immediately
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(text)
                    f.flush()
                    
            def flush(self):
                self.original.flush()
                self.capture.flush()
        
        # Redirect stdout and stderr
        sys.stdout = TeeOutput(original_stdout, stdout_capture, stdout_log_path)
        sys.stderr = TeeOutput(original_stderr, stderr_capture, stderr_log_path)
        
        return original_stdout, original_stderr, stdout_capture, stderr_capture, stdout_log_path, stderr_log_path
    
    async def create_browser_agent(self, task: str, task_id: str = None):
        """Create and configure a browser-use agent with Gemini 2.0 Flash."""
        try:
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not configured")
                
            # Initialize Gemini LLM for browser-use
            gemini_llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=GEMINI_API_KEY,
                temperature=0.1
            )
            
            # Configure browser settings for better screenshot capture
            browser_config = BrowserConfig(
                headless=False,  # Run with head for better compatibility
                disable_security=True,  # Disable security features for testing
                keep_alive=True,
                extra_browser_args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "--window-size=1920,1080",
                    "--disable-extensions",
                    "--disable-plugins",
                    # Remove --disable-images and --disable-javascript for better screenshots
                ]
            )
            
            # Configure browser context for better screenshot handling
            context_config = BrowserContextConfig(
                window_size={"width": 1920, "height": 1080},
                wait_for_network_idle_page_load_time=3.0,
                highlight_elements=True,
                viewport_expansion=500,
                save_recording_path=str(self.logs_dir / "recordings"),
                trace_path=str(self.logs_dir / "traces")
            )
            
            # Create browser with config
            browser = Browser(config=browser_config, context_config=context_config)
            
            # Create custom controller for logging functions
            controller = Controller()
            agent_logger = AgentLogger(self.logs_dir, task_id or "unknown")
            
            @controller.action('Log what you are doing right now')
            def log_action(message: str) -> ActionResult:
                """Log what the agent is doing right now."""
                agent_logger.log_thought(f"ACTION: {message}")
                return ActionResult(extracted_content=f"Logged action: {message}")
            
            @controller.action('Log what you observe on the page')
            def log_observation(message: str) -> ActionResult:
                """Log what the agent observes on the page."""
                agent_logger.log_thought(f"OBSERVATION: {message}")
                return ActionResult(extracted_content=f"Logged observation: {message}")
            
            @controller.action('Log your decision-making process')
            def log_decision(message: str) -> ActionResult:
                """Log agent's decision-making process."""
                agent_logger.log_thought(f"DECISION: {message}")
                return ActionResult(extracted_content=f"Logged decision: {message}")
            
            @controller.action('Take a screenshot of current page state')
            async def take_screenshot_now(description: str, page) -> ActionResult:
                """Take a screenshot of current browser state."""
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    screenshot_filename = f"{task_id}_agent_action_{timestamp}.png"
                    screenshot_path = agent_logger.screenshots_dir / screenshot_filename
                    screenshot_url = f"/screenshots/{screenshot_filename}"
                    
                    # Use the page parameter injected by Browser Use framework
                    screenshot_data = await page.screenshot()
                    with open(screenshot_path, 'wb') as f:
                        f.write(screenshot_data)
                    
                    agent_logger.log_thought(f"✅ Screenshot captured via action: {description}")
                    
                    return ActionResult(
                        extracted_content=f"Screenshot saved: {screenshot_filename} - {description}",
                        include_in_memory=True
                    )
                    
                except Exception as e:
                    agent_logger.log_thought(f"❌ Screenshot action error: {str(e)}")
                    return ActionResult(extracted_content=f"Screenshot failed: {str(e)}")
            
            # Create browser-use agent with custom controller
            agent = browser_use.Agent(
                task=task,
                llm=gemini_llm,
                browser=browser,
                use_vision=True,  # Enable vision for screenshots
                save_conversation_path=str(self.logs_dir / "browser_conversation"),
                controller=controller  # Use our custom controller
            )
            
            # Store agent_logger reference for manual screenshot capture
            agent._custom_logger = agent_logger
            
            return agent
            
        except Exception as e:
            raise Exception(f"Error creating browser agent: {e}")
    
    def save_execution_results(self, history, task_details: dict, task_id: str):
        """Save browser execution results and screenshots with better handling."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save execution log
        log_file = self.logs_dir / f"browser_execution_{task_id}_{timestamp}.json"
        
        results = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "task_details": task_details,
            "execution_steps": [],
            "screenshots": [],
            "screenshot_urls": [],  # URLs for frontend access
            "success": False,
            "error": None,
            "full_conversation": [],
            "debug_info": {}
        }
        
        try:
            # Debug the history object structure
            print(f"🔍 Debug - History type: {type(history)}")
            print(f"🔍 Debug - History dir: {dir(history)}")
            
            # Convert history to list if it's not already
            if hasattr(history, '__iter__'):
                history_list = list(history)
            else:
                history_list = [history] if history else []
            
            print(f"🔍 Debug - History list length: {len(history_list)}")
            
            # Store debug info
            results["debug_info"] = {
                "history_type": str(type(history)),
                "history_length": len(history_list),
                "history_attributes": dir(history) if history else []
            }
            
            if history_list:
                for i, step in enumerate(history_list):
                    print(f"🔍 Debug - Step {i+1} type: {type(step)}")
                    print(f"🔍 Debug - Step {i+1} attributes: {dir(step)}")
                    
                    # Extract step information with better attribute checking
                    step_info = {
                        "step_number": i + 1,
                        "action": "N/A",
                        "result": "N/A", 
                        "timestamp": datetime.now().isoformat(),
                        "screenshot_url": None,
                        "raw_step_type": str(type(step)),
                        "step_attributes": dir(step)
                    }
                    
                    # Handle tuple format (appears to be the actual format)
                    if isinstance(step, tuple):
                        print(f"🔍 Debug - Tuple length: {len(step)}")
                        if len(step) >= 2:
                            # Typically (model_output, result) or similar
                            step_info["action"] = str(step[0]) if step[0] else "N/A"
                            step_info["result"] = str(step[1]) if step[1] else "N/A"
                            print(f"✅ Extracted from tuple - Action: {str(step[0])[:100]}...")
                            print(f"✅ Extracted from tuple - Result: {str(step[1])[:100]}...")
                            
                        # Look for additional data in the tuple
                        for j, item in enumerate(step):
                            print(f"🔍 Debug - Tuple item {j}: {type(item)} = {str(item)[:100]}...")
                            
                            # Check if any item has screenshot data
                            if hasattr(item, 'screenshot') and item.screenshot:
                                screenshot_filename = f"{task_id}_step_{i+1}_{timestamp}.png"
                                screenshot_path = self.screenshots_dir / screenshot_filename
                                screenshot_url = f"/screenshots/{screenshot_filename}"
                                
                                try:
                                    # Handle screenshot data
                                    if isinstance(item.screenshot, bytes):
                                        with open(screenshot_path, 'wb') as f:
                                            f.write(item.screenshot)
                                    elif hasattr(item.screenshot, 'save'):
                                        item.screenshot.save(str(screenshot_path))
                                    
                                    step_info["screenshot"] = str(screenshot_path)
                                    step_info["screenshot_url"] = screenshot_url
                                    results["screenshots"].append(str(screenshot_path))
                                    results["screenshot_urls"].append(screenshot_url)
                                    
                                    print(f"✅ Saved screenshot from tuple item {j}: {screenshot_filename}")
                                    break
                                except Exception as e:
                                    print(f"❌ Error saving screenshot from tuple item {j}: {e}")
                    
                    else:
                        # Try different attribute names for browser-use objects
                        action_attrs = ['model_output', 'action', 'input', 'query', 'tool_calls']
                        result_attrs = ['result', 'output', 'response', 'content']
                        timestamp_attrs = ['timestamp', 'time', 'created_at']
                        screenshot_attrs = ['screenshot', 'image', 'screen_capture', 'page_screenshot']
                        
                        # Extract action
                        for attr in action_attrs:
                            if hasattr(step, attr):
                                value = getattr(step, attr)
                                if value:
                                    step_info["action"] = str(value)
                                    print(f"✅ Found action in {attr}: {str(value)[:100]}...")
                                    break
                        
                        # Extract result
                        for attr in result_attrs:
                            if hasattr(step, attr):
                                value = getattr(step, attr)
                                if value:
                                    step_info["result"] = str(value)
                                    print(f"✅ Found result in {attr}: {str(value)[:100]}...")
                                    break
                        
                        # Extract timestamp
                        for attr in timestamp_attrs:
                            if hasattr(step, attr):
                                value = getattr(step, attr)
                                if value:
                                    if hasattr(value, 'isoformat'):
                                        step_info["timestamp"] = value.isoformat()
                                    else:
                                        step_info["timestamp"] = str(value)
                                    print(f"✅ Found timestamp in {attr}: {step_info['timestamp']}")
                                    break
                        
                        # Look for screenshots in various possible locations
                        screenshot_found = False
                        for attr in screenshot_attrs:
                            if hasattr(step, attr):
                                screenshot = getattr(step, attr)
                                if screenshot:
                                    screenshot_filename = f"{task_id}_step_{i+1}_{timestamp}.png"
                                    screenshot_path = self.screenshots_dir / screenshot_filename
                                    screenshot_url = f"/screenshots/{screenshot_filename}"
                                    
                                    try:
                                        # Handle different screenshot formats
                                        if isinstance(screenshot, bytes):
                                            with open(screenshot_path, 'wb') as f:
                                                f.write(screenshot)
                                        elif hasattr(screenshot, 'save'):
                                            # PIL Image or similar
                                            screenshot.save(str(screenshot_path))
                                        elif isinstance(screenshot, str) and screenshot.startswith(('http', '/', 'data:')):
                                            # URL or data URI - try to download/decode
                                            if screenshot.startswith('data:image'):
                                                import base64
                                                header, data = screenshot.split(',', 1)
                                                with open(screenshot_path, 'wb') as f:
                                                    f.write(base64.b64decode(data))
                                            elif screenshot.startswith('/') and os.path.exists(screenshot):
                                                # File path
                                                import shutil
                                                shutil.copy2(screenshot, screenshot_path)
                                        
                                        step_info["screenshot"] = str(screenshot_path)
                                        step_info["screenshot_url"] = screenshot_url
                                        results["screenshots"].append(str(screenshot_path))
                                        results["screenshot_urls"].append(screenshot_url)
                                        screenshot_found = True
                                        
                                        print(f"✅ Saved screenshot from {attr}: {screenshot_filename}")
                                        break
                                        
                                    except Exception as e:
                                        print(f"❌ Error saving screenshot from {attr}: {e}")
                    
                    # Add conversation details if available
                    if step_info["action"] != "N/A":
                        results["full_conversation"].append({
                            "step": i + 1,
                            "model_output": step_info["action"],
                            "timestamp": step_info["timestamp"]
                        })
                    
                    results["execution_steps"].append(step_info)
                
                results["success"] = True
                print(f"✅ Processed {len(history_list)} execution steps with {len(results['screenshots'])} screenshots")
            else:
                print("⚠️ No history items found")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"❌ Error processing browser history: {e}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
        
        # Save results to file
        try:
            with open(log_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            results["log_file"] = str(log_file)
            print(f"✅ Execution results saved to: {log_file}")
        except Exception as e:
            results["error"] = f"Error saving results: {e}"
            print(f"❌ Error saving results file: {e}")
        
        return results
    
    async def execute_task(self, target_url: str, task_description: str, screenshot_instructions: list, task_id: str):
        """Execute browser automation task directly."""
        task_details = {
            "target_url": target_url,
            "task_description": task_description,
            "screenshot_instructions": screenshot_instructions
        }
        
        # Update task status
        task_storage[task_id]["status"] = "running"
        task_storage[task_id]["progress"] = "Setting up logging..."
        
        # Setup comprehensive logging
        logger, detailed_log_path = self.setup_detailed_logging(task_id)
        
        # Setup stdout/stderr capture
        original_stdout, original_stderr, stdout_capture, stderr_capture, stdout_log_path, stderr_log_path = self.capture_stdout_stderr(task_id)
        
        logger.info(f"=== STARTING AGENT EXECUTION FOR TASK {task_id} ===")
        logger.info(f"Target URL: {target_url}")
        logger.info(f"Task Description: {task_description}")
        logger.info(f"Screenshot Instructions: {len(screenshot_instructions)} items")
        
        # Construct detailed task for browser agent with better screenshot instructions
        full_task = f"""
        Navigate to: {target_url}
        
        Task: {task_description}
        
        IMPORTANT INSTRUCTIONS:
        1. Use the log_action() function to log what you are doing at each step (e.g., "I am now navigating to the website", "I am typing in the search box")
        2. Use the log_observation() function to log what you see on the page (e.g., "I can see a search box", "The page loaded with video results")
        3. Use the log_decision() function to log your reasoning (e.g., "I need to search for the term", "I should click on the first result")
        4. Use the take_screenshot_now() function whenever something important happens (page loads, search results appear, etc.)
        
        Please be very detailed in your logging so we can track your progress!
        """
        
        if screenshot_instructions:
            full_task += "\nAdditional Screenshot Requirements:"
            for i, instr in enumerate(screenshot_instructions):
                full_task += f"\n{i+1}. {instr.get('step_description', 'N/A')} (save as {instr.get('filename', f'screenshot_{i+1}.png')})"
        
        full_task += "\n\nRemember to use the custom logging functions throughout your execution!"
        
        logger.info(f"Full Task Prompt: {full_task}")
        
        try:
            # Create browser agent
            task_storage[task_id]["progress"] = "Initializing browser agent..."
            logger.info("Creating browser agent...")
            browser_agent = await self.create_browser_agent(full_task, task_id)
            logger.info("Browser agent created successfully")
            
            # Execute the task
            task_storage[task_id]["progress"] = "Executing automation task..."
            logger.info("Starting agent.run() execution...")
            
            # Capture initial screenshot
            logger.info("Capturing initial screenshot...")
            initial_screenshot_path, initial_screenshot_url = await self.capture_manual_screenshot(browser_agent, task_id, "initial")
            
            # The agent execution will output to our captured stdout/stderr
            history = await browser_agent.run()
            
            # Capture final screenshot
            logger.info("Capturing final screenshot...")
            final_screenshot_path, final_screenshot_url = await self.capture_manual_screenshot(browser_agent, task_id, "final")
            
            logger.info("Agent execution completed")
            logger.info(f"History type: {type(history)}")
            logger.info(f"History length: {len(list(history)) if history else 0}")
            
            # Save results and screenshots
            task_storage[task_id]["progress"] = "Saving results and screenshots..."
            logger.info("Processing execution results...")
            results = self.save_execution_results(history, task_details, task_id)
            
            # Add manual screenshots to results
            if initial_screenshot_path:
                results["screenshots"].append(initial_screenshot_path)
                results["screenshot_urls"].append(initial_screenshot_url)
                logger.info(f"Added initial screenshot: {initial_screenshot_path}")
                
            if final_screenshot_path:
                results["screenshots"].append(final_screenshot_path)
                results["screenshot_urls"].append(final_screenshot_url)
                logger.info(f"Added final screenshot: {final_screenshot_path}")
            
            logger.info("Results processed successfully")
            
            # Close browser
            logger.info("Closing browser...")
            await browser_agent.browser.close()
            logger.info("Browser closed")
            
            # Update task status
            task_storage[task_id]["status"] = "completed"
            task_storage[task_id]["end_time"] = datetime.now().isoformat()
            task_storage[task_id]["results"] = results
            
            # Add log file paths to results
            results["detailed_log_file"] = str(detailed_log_path)
            results["stdout_log_file"] = str(stdout_log_path)
            results["stderr_log_file"] = str(stderr_log_path)
            
            # Add agent thoughts log file
            if hasattr(browser_agent, '_custom_logger'):
                results["agent_thoughts_file"] = str(browser_agent._custom_logger.log_file)
            
            logger.info(f"=== TASK {task_id} COMPLETED SUCCESSFULLY ===")
            
            return results
            
        except Exception as e:
            logger.error(f"ERROR during task execution: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            error_result = {
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "task_details": task_details,
                "success": False,
                "error": str(e),
                "execution_steps": [],
                "screenshots": [],
                "screenshot_urls": [],
                "detailed_log_file": str(detailed_log_path),
                "stdout_log_file": str(stdout_log_path),
                "stderr_log_file": str(stderr_log_path)
            }
            
            # Add agent thoughts log file if available
            if 'browser_agent' in locals() and hasattr(browser_agent, '_custom_logger'):
                error_result["agent_thoughts_file"] = str(browser_agent._custom_logger.log_file)
            
            # Update task status
            task_storage[task_id]["status"] = "failed"
            task_storage[task_id]["end_time"] = datetime.now().isoformat()
            task_storage[task_id]["error"] = str(e)
            task_storage[task_id]["results"] = error_result
            
            logger.info(f"=== TASK {task_id} FAILED ===")
            
            return error_result
            
        finally:
            # Restore original stdout/stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            
            # Log final captured output
            logger.info("=== CAPTURED STDOUT ===")
            logger.info(stdout_capture.getvalue())
            logger.info("=== CAPTURED STDERR ===")
            logger.info(stderr_capture.getvalue())
            logger.info("=== END OF EXECUTION LOG ===")
            
            # Close logger handlers
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)

    async def capture_manual_screenshot(self, browser_agent, task_id: str, step_name: str):
        """Manually capture a screenshot from the browser agent."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_filename = f"{task_id}_{step_name}_{timestamp}.png"
            screenshot_path = self.screenshots_dir / screenshot_filename
            screenshot_url = f"/screenshots/{screenshot_filename}"
            
            # Try to get screenshot from browser using Browser Use's actual API
            if hasattr(browser_agent, 'browser') and browser_agent.browser:
                # Method 1: Try browser_agent.browser.get_current_page()
                try:
                    current_page = await browser_agent.browser.get_current_page()
                    if current_page:
                        screenshot_data = await current_page.screenshot()
                        with open(screenshot_path, 'wb') as f:
                            f.write(screenshot_data)
                        print(f"✅ Manual screenshot captured via get_current_page: {screenshot_filename}")
                        return str(screenshot_path), screenshot_url
                except Exception as e:
                    print(f"❌ Method 1 failed: {e}")
                
                # Method 2: Try accessing browser_context directly
                try:
                    if hasattr(browser_agent.browser, 'browser_context'):
                        pages = browser_agent.browser.browser_context.pages
                        if pages:
                            page = pages[0]  # Get first page
                            screenshot_data = await page.screenshot()
                            with open(screenshot_path, 'wb') as f:
                                f.write(screenshot_data)
                            print(f"✅ Manual screenshot captured via browser_context: {screenshot_filename}")
                            return str(screenshot_path), screenshot_url
                except Exception as e:
                    print(f"❌ Method 2 failed: {e}")
                
                # Method 3: Try browser._browser_context
                try:
                    if hasattr(browser_agent.browser, '_browser_context'):
                        pages = browser_agent.browser._browser_context.pages
                        if pages:
                            page = pages[0]  # Get first page
                            screenshot_data = await page.screenshot()
                            with open(screenshot_path, 'wb') as f:
                                f.write(screenshot_data)
                            print(f"✅ Manual screenshot captured via _browser_context: {screenshot_filename}")
                            return str(screenshot_path), screenshot_url
                except Exception as e:
                    print(f"❌ Method 3 failed: {e}")
            
            print(f"❌ Could not capture manual screenshot: no accessible browser page found")
            return None, None
            
        except Exception as e:
            print(f"❌ Error capturing manual screenshot: {e}")
            return None, None

class ResultsAnalyzer:
    """Tool to analyze browser automation results."""
    
    def __init__(self):
        self.logs_dir = Path("./operation_logs")
        self.logs_dir.mkdir(exist_ok=True)
    
    @tool(name="AnalyzeResults", description="Analyze browser automation results and generate comprehensive report")
    def analyze_results(self, execution_results: dict, original_instructions: dict) -> dict:
        """
        Analyze the results of browser automation execution.
        
        Args:
            execution_results: Results from browser execution
            original_instructions: Original test instructions
        
        Returns:
            Analysis and review report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_id = execution_results.get("task_id", "unknown")
        
        review_report = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "original_instructions": original_instructions,
            "execution_summary": {
                "success": execution_results.get("success", False),
                "steps_completed": len(execution_results.get("execution_steps", [])),
                "screenshots_captured": len(execution_results.get("screenshots", [])),
                "error": execution_results.get("error")
            },
            "detailed_analysis": {
                "conversation_length": len(execution_results.get("full_conversation", [])),
                "screenshot_analysis": "Screenshots captured at key moments" if execution_results.get("screenshots") else "No screenshots captured"
            },
            "recommendations": [],
            "compliance_check": {}
        }
        
        # Analyze task completion
        task_desc = original_instructions.get("task_description", "")
        execution_steps = execution_results.get("execution_steps", [])
        
        # Check if target URL was accessed
        target_url = original_instructions.get("target_url", "")
        url_accessed = any("navigate" in step.get("action", "").lower() or 
                          target_url in step.get("action", "") for step in execution_steps)
        
        review_report["compliance_check"]["target_url_accessed"] = url_accessed
        
        # Check screenshot requirements
        required_screenshots = original_instructions.get("screenshot_instructions", [])
        captured_screenshots = execution_results.get("screenshots", [])
        
        review_report["compliance_check"]["screenshots_captured"] = {
            "required": len(required_screenshots),
            "captured": len(captured_screenshots),
            "meets_requirements": len(captured_screenshots) >= len(required_screenshots) if required_screenshots else True
        }
        
        # Generate recommendations
        if not execution_results.get("success", False):
            review_report["recommendations"].append("Task execution failed - check error logs")
        
        if not url_accessed:
            review_report["recommendations"].append(f"Target URL {target_url} may not have been properly accessed")
        
        if required_screenshots and len(captured_screenshots) < len(required_screenshots):
            review_report["recommendations"].append("Not all required screenshots were captured")
        
        if execution_results.get("success", False) and url_accessed:
            review_report["recommendations"].append("Task appears to have completed successfully")
            if captured_screenshots:
                review_report["recommendations"].append(f"Successfully captured {len(captured_screenshots)} screenshots")
        
        # Save review report
        review_file = self.logs_dir / f"review_report_{task_id}_{timestamp}.json"
        try:
            with open(review_file, 'w') as f:
                json.dump(review_report, f, indent=2, default=str)
            review_report["review_file"] = str(review_file)
        except Exception as e:
            review_report["error"] = f"Error saving review report: {e}"
        
        return review_report

# Custom tool for agent logging
class AgentLogger:
    """Custom tool for the browser agent to log information and take screenshots."""
    
    def __init__(self, logs_dir: Path, task_id: str):
        self.logs_dir = logs_dir
        self.task_id = task_id
        self.log_file = logs_dir / f"agent_thoughts_{task_id}.txt"
        self.screenshots_dir = logs_dir / "screenshots"
        self.screenshot_count = 0
        
    def log_thought(self, message: str) -> str:
        """Log agent thoughts and actions to file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
            f.flush()
        
        print(f"🤖 Agent Log: {message}")
        return f"Logged: {message}"
    
    def save_screenshot(self, description: str = "screenshot") -> str:
        """Save a screenshot with description."""
        self.screenshot_count += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.task_id}_manual_{self.screenshot_count}_{timestamp}.png"
        filepath = self.screenshots_dir / filename
        
        self.log_thought(f"Taking screenshot: {description}")
        
        # Return the filename for the agent to know
        return f"Screenshot request saved: {filename} - {description}"
    
    def get_screenshot_path(self, description: str = "screenshot"):
        """Get the path where a screenshot should be saved."""
        self.screenshot_count += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.task_id}_agent_{self.screenshot_count}_{timestamp}.png"
        return self.screenshots_dir / filename, f"/screenshots/{filename}"

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Website Testing Agent API",
        "version": "1.0.0",
        "endpoints": {
            "POST /execute-test": "Execute browser automation test",
            "GET /task-status/{task_id}": "Get task execution status",
            "GET /task-results/{task_id}": "Get task execution results",
            "POST /analyze-results/{task_id}": "Analyze task results",
            "GET /screenshots/{filename}": "Serve screenshot files",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/execute-test", response_model=Dict)
async def execute_test(instructions: TestInstructions, background_tasks: BackgroundTasks):
    """Execute browser automation test."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    # Generate unique task ID
    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # Initialize task status
    task_storage[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "start_time": datetime.now().isoformat(),
        "progress": "Task queued for execution",
        "instructions": instructions.model_dump()
    }
    
    # Execute task in background
    executor = BrowserExecutor()
    background_tasks.add_task(
        executor.execute_task,
        instructions.target_url,
        instructions.task_description,
        [instr.model_dump() for instr in instructions.screenshot_instructions],
        task_id
    )
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Task queued for execution",
        "check_status_url": f"/task-status/{task_id}"
    }

@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """Get task execution status."""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_info = task_storage[task_id]
    return {
        "task_id": task_id,
        "status": task_info["status"],
        "progress": task_info.get("progress"),
        "start_time": task_info.get("start_time"),
        "end_time": task_info.get("end_time"),
        "error": task_info.get("error")
    }

@app.get("/task-results/{task_id}")
async def get_task_results(task_id: str):
    """Get task execution results."""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_info = task_storage[task_id]
    
    if task_info["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail=f"Task is still {task_info['status']}")
    
    return task_info.get("results", {})

@app.post("/analyze-results/{task_id}")
async def analyze_results(task_id: str):
    """Analyze task execution results."""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_info = task_storage[task_id]
    
    if task_info["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task must be completed before analysis")
    
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    try:
        # Create the Agno agent for analysis
        analyzer_agent = Agent(
            model=Gemini(id="gemini-2.0-flash", api_key=GEMINI_API_KEY),
            tools=[ResultsAnalyzer()],
            instructions=[
                "You are a website testing analysis expert.",
                "Your role is to analyze browser automation results and provide comprehensive reports.",
                "Use the AnalyzeResults tool to examine execution outcomes.",
                "Provide detailed findings, compliance checks, and recommendations.",
                "Generate clear, actionable insights from the test execution data."
            ],
            markdown=True,
            show_tool_calls=True,
        )
        
        # Get execution results and original instructions
        execution_results = task_info.get("results", {})
        original_instructions = task_info.get("instructions", {})
        
        # Create prompt for analysis
        prompt = f"""
        Please analyze the following browser automation execution results:
        
        **Original Instructions:**
        {json.dumps(original_instructions, indent=2)}
        
        **Execution Results:**
        {json.dumps(execution_results, indent=2)}
        
        Use the AnalyzeResults tool to perform a comprehensive analysis including:
        1. Execution success/failure assessment
        2. Compliance with original instructions
        3. Screenshot capture validation
        4. Task completion verification
        5. Recommendations for improvement
        
        Provide a detailed analysis report.
        """
        
        # Run analysis
        response = analyzer_agent.run(prompt)
        
        # Store analysis results
        analysis_result = {
            "task_id": task_id,
            "analysis_content": response.content,
            "timestamp": datetime.now().isoformat()
        }
        
        task_storage[task_id]["analysis"] = analysis_result
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/tasks")
async def list_tasks():
    """List all tasks and their statuses."""
    return {
        "tasks": [
            {
                "task_id": task_id,
                "status": info["status"],
                "start_time": info.get("start_time"),
                "end_time": info.get("end_time")
            }
            for task_id, info in task_storage.items()
        ]
    }

@app.get("/agent-thoughts/{task_id}")
async def get_agent_thoughts(task_id: str):
    """Get agent thoughts file content for a task."""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        # Look for agent thoughts file
        thoughts_file_pattern = f"agent_thoughts_{task_id}.txt"
        thoughts_file = None
        
        # Search in logs directory
        logs_dir = Path("./operation_logs")
        for file_path in logs_dir.glob(f"*{thoughts_file_pattern}*"):
            thoughts_file = file_path
            break
        
        if not thoughts_file or not thoughts_file.exists():
            return "No agent thoughts file found for this task."
        
        # Read and return file content
        with open(thoughts_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading agent thoughts: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 