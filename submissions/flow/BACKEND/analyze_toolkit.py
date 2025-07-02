import asyncio
import json
import urllib.request
from typing import Optional, List
from agno.tools import tool
from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig
from langchain_openai import ChatOpenAI

class AnalyzeToolkit:
    """Toolkit for analyzing Elements in browser tabs using robust context switching."""
    
    def __init__(self):
        self.tools = [self.analyze_current_tab]

    async def analyze_current_tab(self, prompt: str = None) -> dict:
        try:
            response = urllib.request.urlopen('http://localhost:9222/json')
            tabs = json.loads(response.read())
            active_tab = None
            for tab in tabs:
                # Skip extension popups and new tab pages
                if (tab.get('type') == 'page' and 
                    tab.get('url') != 'chrome://newtab/' and 
                    not tab.get('url', '').startswith('chrome-extension://')):
                    active_tab = tab
                    break

            if not active_tab:
                return {
                    "success": False,
                    "message": "No active tab found. Please open a webpage in Chrome first.",
                    "data": None
                }

            browser_config = BrowserConfig(
                headless=False,
                disable_security=True,
                cdp_url="http://localhost:9222",
            )
            context_config = BrowserContextConfig(
                wait_for_network_idle_page_load_time=10000,
                highlight_elements=False,
                viewport_expansion=500,
                _force_keep_context_alive=True,
                disable_security=True,
            )
            browser_config.new_context_config = context_config
            browser_config.extra_browser_args = [
                "--disable-extensions",
                "--disable-background-networking",
                "--disable-sync",
                "--disable-translate",
                "--disable-default-apps",
                "--disable-popup-blocking",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-device-discovery-notifications"
            ]
            browser = Browser(config=browser_config)
            try:
                browser_context = await browser.new_context()
                try:
                    tabs_info = await browser_context.get_tabs_info()
                    target_tab_id = None
                    for tabinfo in tabs_info:
                        if tabinfo.url == active_tab['url']:
                            target_tab_id = tabinfo.page_id
                            break
                    if target_tab_id is not None:
                        await browser_context.switch_to_tab(target_tab_id)
                        page = await browser_context.get_current_page()
                    else:
                        await browser_context.close()
                        return {
                            "success": False,
                            "message": "Active tab not found in browser context. Please ensure the tab is open and active.",
                            "data": None
                        }
                    try:
                        await page.wait_for_load_state('networkidle')
                    except Exception as e:
                        await browser_context.close()
                        return {
                            "success": False,
                            "message": f"Page failed to load: {str(e)}",
                            "data": None
                        }
                    agent = Agent(
                        task=prompt or "Describe in detail the image currently displayed in this tab. Do not navigate, click, or interact. Only describe what you see.",
                        llm=ChatOpenAI(model='gpt-4o'),
                        browser_context=browser_context,
                        use_vision=True
                    )
                    history = await agent.run()
                    if history and history.history:
                        final_result = history.final_result()
                        if final_result:
                            await browser_context.close()
                            return {
                                "success": True,
                                "message": "Successfully analyzed images in the active tab.",
                                "data": final_result
                            }
                        # Explicitly return after success to stop agent
                        return
                    await browser_context.close()
                    return {
                        "success": False,
                        "message": "No analysis was generated or no images found in the active tab.",
                        "data": None
                    }
                except Exception as e:
                    await browser_context.close()
                    return {
                        "success": False,
                        "message": f"Error analyzing page: {str(e)}",
                        "data": None
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Error getting active tab: {str(e)}",
                    "data": None
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting active tab: {str(e)}",
                "data": None
            }

    async def run_analysis(self) -> dict:
        return await self.analyze_current_tab() 