import os
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig, Controller
from browser_use.browser.context import BrowserContext, BrowserContextConfig
from dotenv import load_dotenv
from views import TestResult
from secrets import sensitive_data
from pathlib import Path
import shutil

load_dotenv()

data_dir = Path("data")

if data_dir.exists():
    shutil.rmtree(data_dir)

subdirs = [
    "recordings",
    "conversations",
    "screenshots",
    "reports"
]

for subdir in subdirs:
    dir_path = data_dir / subdir
    dir_path.mkdir(parents=True, exist_ok=True)

browser_config = BrowserConfig(
    headless=False,
)

context_config = BrowserContextConfig(
    save_recording_path="data/recordings"
)

browser = Browser(config=browser_config)

controller = Controller(output_model=TestResult)

async def browser_use(task):
    context = BrowserContext(browser=browser, config=context_config)
    agent = Agent(
        task=task,
        llm=ChatGoogleGenerativeAI(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-2.5-flash-preview-04-17"),
        browser_context=context,
        sensitive_data=sensitive_data,
        controller=controller,
        save_conversation_path="data/conversations/conversations",
        extend_system_message="Note that you are an expert Software Tester. The task provided to you is a test case that you must carefully execute. Follow the instructions step-by-step, verify each action, and accurately perform the test."
    )
    response = await agent.run()
    await context.close()
    return response 