from typing import List, Type
from ..base import LocalTool
from .read import ReadTool
from .write import WriteTool
from .edit import EditTool
from .bash import BashTool
from .ls import LSTool
from .glob import GlobTool
from .grep import GrepTool
from .summary import SummaryTool
from .ask_for_clarification import AskForClarificationTool
from .web_fetch import WebFetchTool
from .duckduckgo_search import DuckDuckGoSearchTool


def get_predefined_tools() -> List[Type[LocalTool]]:
    """Get all predefined tool classes"""
    return [
        ReadTool,
        WriteTool, 
        EditTool,
        BashTool,
        LSTool,
        GlobTool,
        GrepTool,
        SummaryTool,
        AskForClarificationTool,
        WebFetchTool,
        DuckDuckGoSearchTool,
    ]