from typing import List, Optional
from flet import Ref
import flet as ft

resultContainersRef: List[Optional[Ref[ft.Column]]] = []
searchBarRef: Optional[Ref[ft.TextField]] = None
