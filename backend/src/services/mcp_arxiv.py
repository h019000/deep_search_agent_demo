"""Service responsible for interacting with ArXiv MCP server."""

import os
import json
import logging
from typing import Any, Tuple, Optional
from hello_agents.tools.builtin.protocol_tools import MCPTool

logger = logging.getLogger(__name__)

# Cache the tool instance
_ARXIV_TOOL = None

def get_arxiv_tool():
    """Lazy initialize the arxiv MCP tool."""
    global _ARXIV_TOOL
    if _ARXIV_TOOL is None:
        arxiv_mcp_url = os.environ.get("ARXIV_MCP_URL")
        if arxiv_mcp_url:
            mcp_config = {"transport": "sse", "url": arxiv_mcp_url}
            _ARXIV_TOOL = MCPTool(name="arxiv_mcp", server_command=mcp_config)
            logger.info(f"Initialized ArXiv MCP Tool with SSE transport: {arxiv_mcp_url}")
        else:
            # We assume it runs from `backend` directory, but agent might be started anywhere.
            import sys
            from pathlib import Path
            # Path to the __init__.py of arxiv_mcp_server
            src_dir = Path(__file__).resolve().parent.parent
            mcp_server_path = src_dir / "mcp_server" / "arxiv-mcp-server" / "src" / "arxiv_mcp_server" / "__init__.py"
            _ARXIV_TOOL = MCPTool(
                name="arxiv_mcp",
                server_command=["python", str(mcp_server_path)]
            )
            logger.info(f"Initialized ArXiv MCP Tool with Stdio transport: {mcp_server_path}")
    return _ARXIV_TOOL

def dispatch_arxiv_search(query: str, max_results: int = 5) -> dict[str, Any]:
    """Execute ArXiv search via MCP Tool."""
    logger.info("Dispatching ArXiv search query: %s", query)
    try:
        tool = get_arxiv_tool()
    except Exception as e:
        logger.error("Failed to initialize ArXiv tool: %s", e)
        return {"error": f"Tool init failed: {e}"}

    try:
        res = tool.run({
            "tool_name": "search_papers",
            "arguments": {
                "query": query,
                "max_results": max_results
            }
        })
        return parse_mcp_output(res)
    except Exception as e:
        logger.exception("ArXiv search failed: %s", e)
        return {"error": str(e)}

def parse_mcp_output(res: str) -> dict[str, Any]:
    """Fallback parsing, expects JSON inside the string."""
    try:
        import re
        # Look for JSON payload in the string
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {"raw_output": res}
    except Exception:
        return {"raw_output": res}

def prepare_arxiv_context(search_result: dict[str, Any]) -> tuple[str, str]:
    """Build context from arxiv response."""
    if "error" in search_result:
        return f"ArXiv Error: {search_result['error']}", f"ArXiv Error: {search_result['error']}"
    
    papers = search_result.get("papers", [])
    if not papers and "raw_output" in search_result:
        return "Raw ArXiv Results", search_result["raw_output"]
        
    if not papers:
        return "No ArXiv papers found.", "No ArXiv papers found."
        
    sources = []
    contexts = []
    
    sources.append("### ArXiv Papers:")
    contexts.append("### ArXiv Paper Abstracts:")
    for idx, paper in enumerate(papers):
        title = paper.get("title", "Unknown Title")
        authors = ", ".join(paper.get("authors", []))
        published = paper.get("published", "")
        url = paper.get("url", "")
        abstract = paper.get("abstract", "No abstract available.")
        
        source_str = f"{idx+1}. [{title}]({url}) - {authors} ({published})"
        sources.append(source_str)
        
        ctx_str = f"**Title**: {title}\n**Authors**: {authors}\n**Published**: {published}\n**URL**: {url}\n**Abstract**: {abstract}"
        contexts.append(ctx_str)
        
    return "\n".join(sources), "\n\n".join(contexts)

