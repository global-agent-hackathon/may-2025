import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Agno imports
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools import tool

# Browser-use imports
from langchain_google_genai import ChatGoogleGenerativeAI
import browser_use
from browser_use import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig

# Load environment variables
load_dotenv()

# Fetch the Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found in .env file or environment variables.")
    print("Please create a .env file with GEMINI_API_KEY='your_actual_api_key'")
    exit(1)

class BrowserExecutor:
    """Direct browser automation executor using browser-use library."""
    
    def __init__(self):
        self.logs_dir = Path("./operation_logs")
        self.screenshots_dir = Path("./operation_logs/screenshots")
        self.logs_dir.mkdir(exist_ok=True)
        self.screenshots_dir.mkdir(exist_ok=True)
        
    async def create_browser_agent(self, task: str):
        """Create and configure a browser-use agent with Gemini 2.0 Flash."""
        try:
            # Initialize Gemini LLM for browser-use
            gemini_llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=GEMINI_API_KEY,
                temperature=0.1
            )
            
            # Configure browser settings
            browser_config = BrowserConfig(
                headless=False,  # Keep visible for debugging
                disable_security=False,
                keep_alive=True,
                extra_browser_args=["--disable-blink-features=AutomationControlled"]
            )
            
            # Configure browser context
            context_config = BrowserContextConfig(
                window_width=1280,
                window_height=1100,
                wait_for_network_idle_page_load_time=2.0,
                highlight_elements=True,
                viewport_expansion=500,
                save_recording_path=str(self.logs_dir / "recordings"),
                trace_path=str(self.logs_dir / "traces")
            )
            
            # Create browser with config
            browser = Browser(config=browser_config)
            
            # Create browser-use agent
            agent = browser_use.Agent(
                task=task,
                llm=gemini_llm,
                browser=browser,
                use_vision=True,
                save_conversation_path=str(self.logs_dir / "browser_conversation")
            )
            
            return agent
            
        except Exception as e:
            print(f"Error creating browser agent: {e}")
            raise
    
    def save_execution_results(self, history, task_details: dict):
        """Save browser execution results and screenshots."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save execution log
        log_file = self.logs_dir / f"browser_execution_{timestamp}.json"
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "task_details": task_details,
            "execution_steps": [],
            "screenshots": [],
            "success": False,
            "error": None
        }
        
        try:
            # Process browser-use history
            if history:
                for i, step in enumerate(history):
                    step_info = {
                        "step_number": i + 1,
                        "action": str(step.model_output) if hasattr(step, 'model_output') else "N/A",
                        "result": str(step.result) if hasattr(step, 'result') else "N/A",
                        "timestamp": step.timestamp.isoformat() if hasattr(step, 'timestamp') else datetime.now().isoformat()
                    }
                    
                    # Save screenshot if available
                    if hasattr(step, 'screenshot') and step.screenshot:
                        screenshot_filename = f"step_{i+1}_{timestamp}.png"
                        screenshot_path = self.screenshots_dir / screenshot_filename
                        
                        try:
                            # Save screenshot data
                            if isinstance(step.screenshot, bytes):
                                with open(screenshot_path, 'wb') as f:
                                    f.write(step.screenshot)
                            else:
                                # If it's a file path or other format
                                step.screenshot.save(str(screenshot_path))
                            
                            step_info["screenshot"] = str(screenshot_path)
                            results["screenshots"].append(str(screenshot_path))
                        except Exception as e:
                            print(f"Error saving screenshot for step {i+1}: {e}")
                    
                    results["execution_steps"].append(step_info)
                
                results["success"] = True
            
        except Exception as e:
            results["error"] = str(e)
            print(f"Error processing browser history: {e}")
        
        # Save results to file
        try:
            with open(log_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            results["log_file"] = str(log_file)
            print(f"✅ Browser execution results saved to: {log_file}")
        except Exception as e:
            print(f"Error saving results file: {e}")
        
        return results
    
    async def execute_task(self, target_url: str, task_description: str, screenshot_instructions: list[dict]):
        """Execute browser automation task directly."""
        task_details = {
            "target_url": target_url,
            "task_description": task_description,
            "screenshot_instructions": screenshot_instructions
        }
        
        # Construct detailed task for browser agent
        full_task = f"""
        Navigate to: {target_url}
        
        Task: {task_description}
        
        Screenshot Requirements:
        """
        
        for i, instr in enumerate(screenshot_instructions):
            full_task += f"\n{i+1}. {instr.get('step_description', 'N/A')} (save as {instr.get('filename', f'screenshot_{i+1}.png')})"
        
        try:
            # Create browser agent
            print("🤖 Creating browser agent with Gemini 2.0 Flash...")
            browser_agent = await self.create_browser_agent(full_task)
            
            # Execute the task
            print("🔄 Executing browser automation task...")
            history = await browser_agent.run()
            
            # Save results and screenshots
            print("💾 Saving execution results...")
            results = self.save_execution_results(history, task_details)
            
            # Close browser
            await browser_agent.browser.close()
            
            return results
            
        except Exception as e:
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "task_details": task_details,
                "success": False,
                "error": str(e),
                "execution_steps": [],
                "screenshots": []
            }
            
            # Save error log
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_file = self.logs_dir / f"browser_error_{timestamp}.json"
            try:
                with open(error_file, 'w') as f:
                    json.dump(error_result, f, indent=2)
                error_result["log_file"] = str(error_file)
            except:
                pass
            
            return error_result

def run_browser_automation(instruction_file_path: str = "instructions.json"):
    """Part 1: Run browser automation and save results."""
    print(f"\n🚀 Part 1: Browser Automation")
    print(f"📁 Reading instructions from: {instruction_file_path}")
    
    # Load instructions from JSON file
    if not os.path.exists(instruction_file_path):
        print(f"❌ ERROR: Instruction file not found at {instruction_file_path}")
        return None
    
    try:
        with open(instruction_file_path, 'r') as f:
            instructions = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in {instruction_file_path}: {e}")
        return None
    except Exception as e:
        print(f"❌ ERROR: Could not read {instruction_file_path}: {e}")
        return None
    
    # Validate required fields
    required_fields = ["target_url", "task_description", "screenshot_instructions"]
    missing_fields = [field for field in required_fields if field not in instructions]
    
    if missing_fields:
        print(f"❌ ERROR: Missing required fields in JSON: {missing_fields}")
        return None
    
    print(f"✅ Instructions loaded successfully")
    print(f"🎯 Target URL: {instructions['target_url']}")
    print(f"📋 Task: {instructions['task_description'][:100]}...")
    
    # Execute browser automation
    executor = BrowserExecutor()
    results = asyncio.run(executor.execute_task(
        instructions['target_url'],
        instructions['task_description'], 
        instructions['screenshot_instructions']
    ))
    
    print(f"✅ Browser automation completed!")
    return results

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
        
        review_report = {
            "timestamp": datetime.now().isoformat(),
            "original_instructions": original_instructions,
            "execution_summary": {
                "success": execution_results.get("success", False),
                "steps_completed": len(execution_results.get("execution_steps", [])),
                "screenshots_captured": len(execution_results.get("screenshots", [])),
                "error": execution_results.get("error")
            },
            "detailed_analysis": {},
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
            "meets_requirements": len(captured_screenshots) >= len(required_screenshots)
        }
        
        # Generate recommendations
        if not execution_results.get("success", False):
            review_report["recommendations"].append("Task execution failed - check error logs")
        
        if not url_accessed:
            review_report["recommendations"].append(f"Target URL {target_url} may not have been properly accessed")
        
        if len(captured_screenshots) < len(required_screenshots):
            review_report["recommendations"].append("Not all required screenshots were captured")
        
        if execution_results.get("success", False) and url_accessed:
            review_report["recommendations"].append("Task appears to have completed successfully")
        
        # Save review report
        review_file = self.logs_dir / f"review_report_{timestamp}.json"
        try:
            with open(review_file, 'w') as f:
                json.dump(review_report, f, indent=2, default=str)
            review_report["review_file"] = str(review_file)
            print(f"✅ Analysis report saved to: {review_file}")
        except Exception as e:
            print(f"Error saving review report: {e}")
        
        return review_report

def run_results_analysis(execution_results: dict, original_instructions: dict):
    """Part 2: Run Agno agent to analyze results."""
    print(f"\n🔍 Part 2: Results Analysis with Agno Agent")
    
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
    
    Provide a detailed markdown report with your findings.
    """
    
    print("🤖 Running analysis with Agno agent...")
    response = analyzer_agent.run(prompt)
    print("\n" + "="*60)
    print("📊 ANALYSIS RESULTS:")
    print("="*60)
    print(response.content)
    print("="*60)
    
    return response

def main():
    """Main execution function."""
    print("🌟 Website Testing Agent - Two-Part Execution")
    print("=" * 60)
    print("📋 Prerequisites:")
    print("  1. GEMINI_API_KEY in .env file")
    print("  2. pip install agno browser-use langchain-google-genai python-dotenv")
    print("  3. Valid instructions.json file")
    print("=" * 60)
    
    # Load original instructions for analysis
    try:
        with open("instructions.json", 'r') as f:
            original_instructions = json.load(f)
    except Exception as e:
        print(f"❌ ERROR: Could not load instructions.json: {e}")
        return
    
    # Part 1: Run browser automation
    execution_results = run_browser_automation()
    
    if execution_results is None:
        print("❌ Browser automation failed, cannot proceed to analysis")
        return
    
    # Part 2: Run results analysis
    analysis_response = run_results_analysis(execution_results, original_instructions)
    
    print(f"\n✅ Complete workflow finished!")
    print(f"📁 Check ./operation_logs/ for all generated files")

if __name__ == "__main__":
    main() 