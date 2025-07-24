from browser_use import Browser, Agent as BrowserAgent, Controller, ActionResult

import re

from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# Set up custom controller actions
controller = Controller()

class JobDetails(BaseModel):
    title: str
    company: str
    job_link: str
    salary: Optional[str] = None

@controller.action(
    'Save job details which you found on page',
    param_model=JobDetails
)
async def save_job(params: JobDetails, browser: Browser):
    print(f"Saving job: {params.title} at {params.company}")
    # Access browser if needed
    page = browser.get_current_page()
    await page.goto(params.job_link)
    return ActionResult(success=True, extracted_content=f"Saved job: {params.title} at {params.company}", include_in_memory=True)

class ElementOnPage(BaseModel):
    index: int
    xpath: Optional[str] = None

@controller.action("Get XPath of element using index", param_model=ElementOnPage)
async def get_xpath_of_element(params: ElementOnPage, browser: Browser):
    session = await browser.get_session()
    state = session.cached_state
    if params.index not in state.selector_map:
        return ActionResult(error="Element not found")
    element_node = state.selector_map[params.index]
    xpath = element_node.xpath
    if xpath is None:
        return ActionResult(error="Element not found, try another index")
    return ActionResult(extracted_content="The xpath of the element is "+xpath, include_in_memory=True)

class ElementProperties(BaseModel):
    index: int
    property_name: str = "innerText"

@controller.action("Get element property", param_model=ElementProperties)
async def get_element_property(params: ElementProperties, browser: Browser):
    page = browser.get_current_page()
    session = await browser.get_session()
    state = session.cached_state
    
    if params.index not in state.selector_map:
        return ActionResult(error="Element not found")
    
    element_node = state.selector_map[params.index]
    element = await page.query_selector(element_node.selector)
    
    if element is None:
        return ActionResult(error="Element not found on page")
    
    try:
        property_value = await element.get_property(params.property_name)
        json_value = await property_value.json_value()
        return ActionResult(
            extracted_content=f"Element {params.index} {params.property_name}: {json_value}",
            include_in_memory=True
        )
    except Exception as e:
        return ActionResult(error=f"Error getting property: {str(e)}")

class ElementAction(BaseModel):
    index: int
    action: str = "click"  # click, hover, focus, etc.
    value: Optional[str] = None  # For actions like fill

@controller.action("Perform element action", param_model=ElementAction)
async def perform_element_action(params: ElementAction, browser: Browser):
    page = browser.get_current_page()
    session = await browser.get_session()
    state = session.cached_state
    
    if params.index not in state.selector_map:
        return ActionResult(error="Element not found")
    
    element_node = state.selector_map[params.index]
    element = await page.query_selector(element_node.selector)
    
    if element is None:
        return ActionResult(error="Element not found on page")
    
    # Capture detailed element information before performing action
    element_details = await get_detailed_element_info(element, element_node, page)
    
    try:
        if params.action == "click":
            await element.click()
            return ActionResult(
                extracted_content=f"Clicked element {params.index}\nElement Details: {element_details}",
                include_in_memory=True
            )
        elif params.action == "hover":
            await element.hover()
            return ActionResult(
                extracted_content=f"Hovered over element {params.index}\nElement Details: {element_details}",
                include_in_memory=True
            )
        elif params.action == "fill" and params.value is not None:
            await element.fill(params.value)
            return ActionResult(
                extracted_content=f"Filled element {params.index} with '{params.value}'\nElement Details: {element_details}",
                include_in_memory=True
            )
        else:
            return ActionResult(error=f"Unsupported action: {params.action}")
    except Exception as e:
        return ActionResult(error=f"Error performing action: {str(e)}")

class ElementDetails(BaseModel):
    index: int

@controller.action("Get detailed element information", param_model=ElementDetails)
async def get_element_details(params: ElementDetails, browser: Browser):
    page = browser.get_current_page()
    session = await browser.get_session()
    state = session.cached_state
    
    if params.index not in state.selector_map:
        return ActionResult(error="Element not found")
    
    element_node = state.selector_map[params.index]
    element = await page.query_selector(element_node.selector)
    
    if element is None:
        return ActionResult(error="Element not found on page")
    
    element_details = await get_detailed_element_info(element, element_node, page)
    
    # Format the element details in a more structured way for better display
    formatted_details = {
        "Element Index": params.index,
        "Basic Information": {
            "Tag": element_details.get("tag", ""),
            "ID": element_details.get("id", ""),
            "Name": element_details.get("name", ""),
            "Type": element_details.get("type", ""),
            "Class": element_details.get("class", ""),
            "Placeholder": element_details.get("placeholder", ""),
            "Value": element_details.get("value", ""),
            "Text": element_details.get("text", ""),
            "Is Visible": element_details.get("is_visible", False)
        },
        "Selectors": {
            "Absolute XPath": element_details.get("absolute_xpath", ""),
            "Relative XPath": element_details.get("relative_xpath", ""),
            "CSS Selector": element_details.get("css_selector", ""),
            "XPath Variations": element_details.get("xpath_variations", []),
            "CSS Variations": element_details.get("css_variations", [])
        },
        "Dimensions": element_details.get("dimensions", {}),
        "All Attributes": element_details.get("attributes", {})
    }
    
    return ActionResult(
        extracted_content=formatted_details,
        include_in_memory=True
    )

async def get_detailed_element_info(element, element_node, page):
    """Extract detailed information about an element for automation script generation"""
    try:
        # Get tag name
        tag_name = await page.evaluate("(element) => element.tagName.toLowerCase()", element)
        
        # Get element attributes
        attributes = await page.evaluate("""
        (element) => {
            const attrs = {};
            for (const attr of element.attributes) {
                attrs[attr.name] = attr.value;
            }
            return attrs;
        }
        """, element)
        
        # Extract common attributes
        element_id = attributes.get('id', '')
        class_name = attributes.get('class', '')
        name_attr = attributes.get('name', '')
        placeholder = attributes.get('placeholder', '')
        value = attributes.get('value', '')
        type_attr = attributes.get('type', '')
        
        # Get absolute XPath
        absolute_xpath = element_node.xpath if element_node.xpath else ''
        
        # Generate relative XPath based on ID, class, or other attributes
        relative_xpath = ''
        if element_id:
            relative_xpath = f"//{tag_name}[@id='{element_id}']"
        elif name_attr:
            relative_xpath = f"//{tag_name}[@name='{name_attr}']"
        elif class_name:
            relative_xpath = f"//{tag_name}[@class='{class_name}']"
        elif placeholder:
            relative_xpath = f"//{tag_name}[@placeholder='{placeholder}']"
        
        # Generate additional XPath variations for better selector options
        xpath_variations = []
        if element_id:
            xpath_variations.append(f"//*[@id='{element_id}']")
        if name_attr:
            xpath_variations.append(f"//*[@name='{name_attr}']")
        if placeholder:
            xpath_variations.append(f"//*[@placeholder='{placeholder}']")
        if type_attr and value:
            xpath_variations.append(f"//{tag_name}[@type='{type_attr}' and @value='{value}']")
        
        # Generate CSS selector
        css_selector = ''
        if element_id:
            css_selector = f"#{element_id}"
        elif class_name:
            # Convert space-separated classes to CSS class selector format
            css_classes = '.'.join(class_name.split())
            css_selector = f"{tag_name}.{css_classes}"
        elif name_attr:
            css_selector = f"{tag_name}[name='{name_attr}']"
        elif placeholder:
            css_selector = f"{tag_name}[placeholder='{placeholder}']"
        
        # Generate additional CSS selector variations
        css_variations = []
        if element_id:
            css_variations.append(f"#{element_id}")
        if class_name:
            css_classes = '.'.join(class_name.split())
            css_variations.append(f".{css_classes}")
        if name_attr:
            css_variations.append(f"[name='{name_attr}']")
        if placeholder:
            css_variations.append(f"[placeholder='{placeholder}']")
        
        # Get element text content
        text_content = await page.evaluate("(element) => element.textContent.trim()", element)
        
        # Get element dimensions and position
        bounding_box = await page.evaluate("""
        (element) => {
            const rect = element.getBoundingClientRect();
            return {
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height
            };
        }
        """, element)
        
        # Check if element is visible
        is_visible = await element.is_visible()
        
        # Format the detailed information
        details = {
            "tag": tag_name,
            "id": element_id,
            "class": class_name,
            "name": name_attr,
            "type": type_attr,
            "placeholder": placeholder,
            "value": value,
            "text": text_content[:50] + ('...' if len(text_content) > 50 else ''),
            "absolute_xpath": absolute_xpath,
            "relative_xpath": relative_xpath,
            "xpath_variations": xpath_variations,
            "css_selector": css_selector,
            "css_variations": css_variations,
            "dimensions": bounding_box,
            "is_visible": is_visible,
            "attributes": attributes
        }
        
        return details
    except Exception as e:
        return {"error": f"Failed to get element details: {str(e)}"}

# Helper functions for code generation
def extract_selectors_from_history(history_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract element selectors from agent history"""
    selectors = {}
    xpath_pattern = re.compile(r"The xpath of the element is (.*)")
    element_details_pattern = re.compile(r"Element Details: \{(.+?)\}")
    
    for content in history_data.get('extracted_content', []):
        if isinstance(content, str):
            # Extract XPath from direct XPath actions
            match = xpath_pattern.search(content)
            if match:
                xpath = match.group(1)
                name = "element_" + str(len(selectors) + 1)
                selectors[name] = xpath
                continue
                
            # Extract from detailed element information
            details_match = element_details_pattern.search(content)
            if details_match:
                try:
                    # Try to parse the JSON-like string
                    details_str = '{' + details_match.group(1) + '}'
                    # Clean up the string for proper JSON parsing
                    details_str = details_str.replace("'", "\"")
                    details = json.loads(details_str)
                    
                    # Use the best selector available
                    selector = None
                    if details.get("id"):
                        selector = details.get("css_selector")
                    elif details.get("relative_xpath"):
                        selector = details.get("relative_xpath")
                    elif details.get("absolute_xpath"):
                        selector = details.get("absolute_xpath")
                    
                    if selector:
                        name = f"element_{len(selectors) + 1}"
                        selectors[name] = selector
                except Exception as e:
                    print(f"Error parsing element details: {e}")
    
    return selectors

def analyze_actions(history_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze the actions performed by the agent to create step implementations"""
    actions = []
    element_details_pattern = re.compile(r"Element Details: (\{.+?\})")
    
    for i, action_name in enumerate(history_data.get('action_names', [])):
        action_info = {
            "name": action_name,
            "index": i,
            "type": "unknown",
            "element_details": None
        }
        
        # Determine action type
        if "navigate" in action_name.lower() or "goto" in action_name.lower():
            action_info["type"] = "navigation"
        elif "click" in action_name.lower():
            action_info["type"] = "click"
        elif "type" in action_name.lower() or "fill" in action_name.lower() or "enter" in action_name.lower():
            action_info["type"] = "input"
        elif "check" in action_name.lower() or "verify" in action_name.lower() or "assert" in action_name.lower():
            action_info["type"] = "verification"
        elif "get xpath" in action_name.lower():
            action_info["type"] = "xpath"
        elif "get detailed element information" in action_name.lower():
            action_info["type"] = "element_details"
        elif "save job details" in action_name.lower():
            action_info["type"] = "custom_save"
        
        # Extract element details if available in the content
        if i < len(history_data.get('extracted_content', [])):
            content = history_data.get('extracted_content', [])[i]
            if isinstance(content, str):
                details_match = element_details_pattern.search(content)
                if details_match:
                    try:
                        details_str = details_match.group(1)
                        # Clean up the string for proper JSON parsing
                        details_str = details_str.replace("'", "\"")
                        details = json.loads(details_str)
                        action_info["element_details"] = details
                    except Exception as e:
                        print(f"Error parsing element details in action analysis: {e}")
        
        actions.append(action_info)
    
    return actions
