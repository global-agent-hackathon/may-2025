import yaml
import json
import base64
import asyncio
from agent import browser_use, browser
from pathlib import Path
from datetime import datetime

async def execute_test_file(test_file_path: str):
    print(f"\nExecuting tests from: {test_file_path}")
    results = []
    
    with open(test_file_path, "r") as f:
        test_config = yaml.safe_load(f)

    hooks = test_config.get("hooks", {})
    tests = test_config.get("tests", [])
    
    for test in tests:
        print(f"\nExecuting test: {test['name']}")
        
        test_result = {
            "file_name": str(Path(test_file_path).name),
            "test_name": test['name'],
            "test_id": test['id']
        }
        
        browser_use_instructions = (
            f"{hooks.get('beforeEach', '')}\n"
            f"{test['instructions']}\n"
            f"{hooks.get('afterEach', '')}"
        ).strip()
        
        try:
            response = await browser_use(browser_use_instructions)
            screenshots = response.screenshots()
            
            if screenshots:
                screenshot_dir = Path("data/screenshots")
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = screenshot_dir / f"{test['id']}.png"
                with open(screenshot_path, "wb") as f:
                    f.write(base64.b64decode(screenshots[-1]))
                print(f"Screenshot saved: {screenshot_path}")
            
            if response.has_errors():
                print("Some errors occurred!")
                print("Errors:", response.errors)
                test_result["result"] = {"status": "error", "message": str(response.errors)}
            else:
                final_result = response.final_result()
                print("Test Result:", final_result)
                # Ensure we store a serializable version of the result
                if hasattr(final_result, 'dict'):
                    test_result["result"] = final_result.dict()
                elif hasattr(final_result, '__dict__'):
                    test_result["result"] = final_result.__dict__
                else:
                    test_result["result"] = {"status": "completed", "message": str(final_result)}
                
        except Exception as e:
            error_msg = str(e)
            print(f"Error executing test {test['name']}: {error_msg}")
            test_result["result"] = {"status": "error", "message": error_msg}
            
        results.append(test_result)
    
    return results

async def main():
    tests_dir = Path("tests")
    if not tests_dir.exists():
        raise FileNotFoundError("Tests directory not found!")
        
    yaml_files = list(tests_dir.glob("*.yml")) + list(tests_dir.glob("*.yaml"))
    
    if not yaml_files:
        raise FileNotFoundError("No YAML test files found in tests directory!")
    
    all_results = []
    try:
        for test_file in yaml_files:
            results = await execute_test_file(str(test_file))
            all_results.extend(results)
    finally:
        await browser.close()
    
    report_dir = Path("data/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nJSON report saved: {report_file}")

if __name__ == "__main__":
    asyncio.run(main()) 