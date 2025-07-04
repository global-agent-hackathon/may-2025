from typing import Optional
import flet as ft
from flet import Ref

currentIndex = 0
itemIndex = 0

removeFocus: Optional[Ref[ft.TextField]] = None
