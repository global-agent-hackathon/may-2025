# This file makes the search directory a Python package

from .search_pdf import PDFSearcher
from .search_web import WebSearcher

__all__ = ["PDFSearcher", "WebSearcher"]
