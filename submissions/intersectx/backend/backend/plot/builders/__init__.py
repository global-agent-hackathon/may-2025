from abc import ABC, abstractmethod

from backend.agents.netlify import NetlifyAgent
from backend.plot.types import ChartData


class IBuilder(ABC):
    def __init__(self, netlify_agent: NetlifyAgent):
        self.netlify_agent = netlify_agent

    @abstractmethod
    async def plot(self, chart_data: ChartData, company_name: str) -> str:
        """
        Generate a plot from ChartData, upload it as HTML via FilesService, and return the public URL.
        """
        pass
