"""
Entry point for the MCP server. Registers tools/prompts (added in
later steps) and runs over stdio so Claude Desktop can launch it as
a subprocess.

FastMCP was renamed to MCPServer in mcp v2 — adapted from the official
migration guide:
https://py.sdk.modelcontextprotocol.io/v2/migration/#fastmcp-renamed-to-mcpserver
"""
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("email_task_mcp")

from tools import add_task as _add_task

@mcp.tool()
def add_task(description: str, due_date: str | None = None) -> dict:
    """Add a new task to the user's task list, with an optional due date."""
    return _add_task(description, due_date)

from tools import send_email as _send_email

@mcp.tool()
def send_email(recipient_email: str, subject: str, body: str) -> dict:
    """Send an email to a recipient with the given subject and body."""
    return _send_email(recipient_email, subject, body)

from prompts import build_weekly_status_prompt

@mcp.prompt()
def weekly_status_prompt(recipient_email: str) -> str:
    """Generate a prompt for drafting a task status-update email to a recipient."""
    return build_weekly_status_prompt(recipient_email)

if __name__ == "__main__":
    mcp.run()