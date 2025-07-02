from typing import Literal, Any, Optional
from pydantic import BaseModel

PlotKind = Literal["line", "bar", "pie", "area"]


class ChartData(BaseModel):
    data: Any  # Typically a list of dicts or DataFrame
    title: Optional[str] = None
    x: Optional[str] = None
    y: Optional[str] = None
    kind: PlotKind
    # Optionally, add more fields (color, labels, etc.)


# Add more type definitions as needed
