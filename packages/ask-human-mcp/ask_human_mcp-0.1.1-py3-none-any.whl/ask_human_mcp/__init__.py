"""Ask-Human MCP Server

A Model Context Protocol server that enables AI agents to escalate
questions to humans instead of hallucinating answers.
"""

__version__ = "0.1.1"
__author__ = "Mason Yarbrough"
__email__ = "mason@kallro.com"

from .server import main

__all__ = ["main"]
