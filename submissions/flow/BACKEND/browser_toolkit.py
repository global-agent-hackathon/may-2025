import os
import json
import urllib.request
from langchain_openai import ChatOpenAI
from agno.tools import Toolkit
from browser_use import Agent, Browser, BrowserConfig, BrowserContextConfig


class BrowserUseToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="browser_toolkit")
        self.llm = ChatOpenAI(model='gpt-4o')
        self.active_agent = None  # Track the active browser agent
        self.register(self.execute_browser_task)

    async def execute_browser_task(self, task_description: str):
        """Execute browser tasks without closing the session"""
        try:
            # Create a new agent only if none exists
            if self.active_agent is None:
                context_config = BrowserContextConfig(
                    wait_for_network_idle_page_load_time=10000,
                    highlight_elements=False,
                    viewport_expansion=500,
                    _force_keep_context_alive=True,  # THIS IS CRUCIAL
                    save_downloads_path=os.path.join(os.path.expanduser('~'), 'downloads')
                )
                
                browser_config = BrowserConfig(
                    headless=False,
                    disable_security=True,
                    cdp_url="http://localhost:9222",
                    new_context_config=context_config,
                    _force_keep_browser_alive=True,  # THIS IS CRUCIAL
                )
                
                # Initialize browser with our persistent config
                browser = Browser(config=browser_config)
                
                # Create new context and new tab
                browser_context = await browser.new_context()
                await browser_context.create_new_tab("about:blank")
                
                self.active_agent = Agent(
                    llm=self.llm,
                    task=task_description,
                    browser_context=browser_context
                )
            else:
                # Reuse the existing agent with a new task
                self.active_agent.task = task_description
            
            result = await self.active_agent.run()
            return str(result)  # Return result without closing
            
        except Exception as e:
            # Optionally reset agent on failure (or keep it alive)
            # self.active_agent = None
            return f"Task failed: {str(e)}"

    async def close_session(self):
        """Manually close the browser when needed"""
        if self.active_agent and hasattr(self.active_agent, 'close'):
            await self.active_agent.close()
            self.active_agent = None
            return True
        return False