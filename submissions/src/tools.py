from src.desktop import Desktop
from agno.tools import Toolkit
from typing import Literal
import pyautogui as pg
import pyperclip as pc

pg.FAILSAFE = False
pg.PAUSE = 0.1

class WindowsTools(Toolkit):
    def __init__(self,**kwargs):
        self.desktop=Desktop()
        tools=[self.state_tool,self.clipboard_tool,self.click_tool,self.launch_tool,
        self.type_tool,self.key_tool,self.wait_tool,self.shortcut_tool,self.move_tool,
        self.scroll_tool,self.drag_tool]
        super().__init__(name='windows_tools',tools=tools,**kwargs)

    def state_tool(self)->str:
        """
        To get the current state of the desktop

        Returns:
            str : The current state of the desktop
        
        Example:
        >>> state_tool()
        """
        desktop_state=self.desktop.get_state()
        interactive_elements=desktop_state.tree_state.interactive_elements_to_string()
        informative_elements=desktop_state.tree_state.informative_elements_to_string()
        apps=desktop_state.apps_to_string()
        active_app=desktop_state.active_app_to_string()
        return f'Active App:\n{active_app}\n\nOpened Apps:\n{apps}\n\nList of Interactive Elements:\n{interactive_elements}\nList of Informative Elements:\n{informative_elements}'

    def powershell_tool(self,command: str) -> str:
        """
        To execute a PowerShell command.

        Args:
            command (str): PowerShell command to execute.


        Returns:
            str: Status message and result of the operation.
        
        Example:
        >>> powershell_tool("Get-Process") 
        """
        response,status=self.desktop.execute_command(command)
        return f'Status Code: {status}\nResponse: {response}'

    def launch_tool(self,name: str) -> str:
        """
        To launch an application present in the Start menu.

        Args:
            name (str): Name of the application to launch.

        Returns:
            str: Status message indicating the result of the operation.
        
        Example:
        >>> launch_tool("Google Chrome")
        """
        _,status=self.desktop.launch_app(name)
        if status!=0:
            return f'Failed to launch {name.title()}.'
        else:
            return f'Launched {name.title()}.'

    def clipboard_tool(self,mode: Literal['copy', 'paste'], text: str = None) -> str:
        """
        To copy or paste text from the system clipboard.

        Args:
            mode (Literal['copy', 'paste']): Mode to either copy or paste.
            text (str, optional): Text to copy to clipboard. Defaults to None.

        Returns:
            str: Status message indicating the result of the operation.
        
        Example:
        >>> clipboard_tool("copy","Hello World")
        >>> clipboard_tool("paste")
        """
        if mode == 'copy':
            if text:
                pc.copy(text)
                return f'Copied to clipboard: {text}'
            else:
                return 'No text provided to copy.'
        elif mode == 'paste':
            return f'Pasted from clipboard: {pc.paste()}'
        else:
            return 'Invalid mode or missing text for copy.'

    def click_tool(self,x: int, y: int, button: Literal['left', 'right', 'middle'] = 'left', clicks: int = 1) -> str:
        """
        To click on an element at the specified coordinates.

        Args:
            x (int): X-coordinate to click on.
            y (int): Y-coordinate to click on.
            button (Literal['left', 'right', 'middle'], optional): Mouse button to use. Defaults to 'left'.
            clicks (int, optional): Number of clicks. Defaults to 1.

        Returns:
            str: Status message indicating the result of the operation.
        
        Example:
        >>> click_tool(100, 200, "right", 1)
        """
        pg.click(x=x, y=y, button=button, clicks=clicks, duration=0.5, tween=pg.easeInOutQuad)
        num_clicks = {1: 'Single', 2: 'Double', 3: 'Triple'}
        return f'Clicked {num_clicks.get(clicks)} {button} at ({x}, {y}).'

    def type_tool(self,x: int, y: int, text: str, clear: bool = False) -> str:
        """
        To type text at the specified coordinates.

        Args:
            x (int): X-coordinate to click on.
            y (int): Y-coordinate to click on.
            text (str): Text to type.
            clear (bool, optional): Whether to clear the field before typing. Defaults to False.

        Returns:
            str: Status message indicating the result of the operation.
        
        Example:
        >>> type_tool(100, 200, "Hello World", True)
        """
        pg.click(x=x, y=y)
        if clear:
            pg.hotkey('ctrl', 'a')
            pg.press('backspace')
        pg.typewrite(text)
        return f'Typed "{text}" on element at ({x}, {y}).'

    def scroll_tool(self, direction: Literal['up', 'down'] = '', amount: int = 0) -> str:
        """
        To scroll the screen in the specified direction.

        Args:
            direction (Literal['up', 'down'], optional): Direction to scroll. Defaults to ''.
            amount (int, optional): Amount to scroll. Defaults to 0.

        Returns:
            str: Status message indicating the result of the operation.
        
        Example:
        >>> scroll_tool("up", 100)  
        """
        if direction == 'up':
            pg.scroll(amount)
        elif direction == 'down':
            pg.scroll(-amount)
        else:
            return 'Invalid direction.'
        return f'Scrolled {direction} by {amount}.'

    def drag_tool(self, x1: int, y1: int, x2: int, y2: int) -> str:
        """
        To drag an element from one location to another.

        Args:
            x1 (int): X-coordinate of the starting location.
            y1 (int): Y-coordinate of the starting location.
            x2 (int): X-coordinate of the ending location.
            y2 (int): Y-coordinate of the ending location.

        Returns:
            str: Status message indicating the result of the operation.
        
        Example:
        >>> drag_tool(100, 200, 300, 400)
        """
        pg.moveTo(x1, y1, duration=0.5, tween=pg.easeInOutQuad)
        pg.dragTo(x2, y2, duration=0.5, tween=pg.easeInOutQuad)
        return f'Dragged from ({x1}, {y1}) to ({x2}, {y2}).'

    def move_tool(self, x: int, y: int) -> str:
        """
        To move the mouse pointer to the specified coordinates.

        Args:
            x (int): X-coordinate to move to.
            y (int): Y-coordinate to move to.

        Returns:
            str: Status message indicating the result of the operation.
        
        Example:
        >>> move_tool(100, 200)
        """
        pg.moveTo(x, y, duration=0.5, tween=pg.easeInOutQuad)
        return f'Moved mouse pointer to ({x}, {y}).'

    def shortcut_tool(self, shortcut: list[str]) -> str:
        """
        To perform a keyboard shortcut.

        Args:
            shortcut (list[str]): List of keys to press.

        Returns:
            str: Status message indicating the result of the operation.
        
        Example:
        >>> shortcut_tool(["ctrl", "c"])
        """
        pg.hotkey(*shortcut)
        return f'Pressed {" + ".join(shortcut)}.'

    def key_tool(self, key: str = '') -> str:
        """
        To press a specific key on the keyboard.

        Args:
            key (str, optional): Key to press. Defaults to ''.

        Returns:
            str: Status message indicating the result of the operation.
        
        Example:
        >>> key_tool("enter")
        """
        pg.press(key)
        return f'Pressed the key {key}.'

    def wait_tool(self, duration: int) -> str:
        """
        To wait for the specified duration.

        Args:
            duration (int): Duration to wait in seconds.

        Returns:
            str: Status message indicating the result of the operation.
        
        Example:
        >>> wait_tool(5)
        """
        pg.sleep(duration)
        return f'Waited for {duration} seconds.'

