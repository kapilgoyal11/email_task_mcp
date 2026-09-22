# email_task_mcp

An MCP server built for the "Applied AI for Technical Teams" course assignment (ENMGT 4405). Domain: **Personal Productivity**. Implements two tools and one prompt, plus two security best practices with working exploit demonstrations.

## What this server does

- **`add_task`** — adds a task (description + optional due date) to a local task list.
- **`send_email`** — sends a real email via Gmail SMTP, given a recipient, subject, and body.
- **`weekly_status_prompt`** — an MCP prompt that reads the current task list and generates an instruction for the LLM to draft (and send) a status-update email summarizing tasks as Completed/In Progress.

## Architecture

```
Claude Desktop  →  MCP Client  →  server.py (stdio transport)
                                        │
                        ┌───────────────┼────────────────┐
                        ▼               ▼                ▼
                 add_task tool   send_email tool   weekly_status_prompt
                        │               │
                        ▼               ▼
                  tasks.json      Gmail SMTP (smtp.gmail.com:465)
                  (pathlib)       credentials from .env
                                        │
                                        ▼
                          security.py: header sanitization
                                       + rate limiting
```

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or another virtual environment tool
- A Gmail account with 2-Step Verification enabled and an [App Password](https://myaccount.google.com/apppasswords) generated for it

## Setup

1. **Clone the repo and enter the directory:**
```bash
   git clone https://github.com/kapilgoyal11/email_task_mcp.git
   cd email_task_mcp
```

2. **Create and activate a virtual environment:**
```bash
   uv venv
   source .venv/bin/activate
```

3. **Install dependencies:**
```bash
   uv pip install -r requirements.txt
```

4. **Set up secrets:** copy `.env.example` to `.env` and fill in your real values:
```bash
   cp .env.example .env
```
   Edit `.env`:
```
   SMTP_EMAIL=your_gmail_address@gmail.com
   SMTP_APP_PASSWORD=your_16_character_app_password
```
   `.env` is git-ignored and never committed.

5. **Run the server directly** (to confirm it starts with no errors):
```bash
   python server.py
```
   It should hang with no output — that means it's running and waiting for a client over stdio. `Ctrl+C` to stop.

## Connecting to Claude Desktop

Add the following to your `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`) under the `mcpServers` key, alongside any existing configuration already in that file:

```json
"mcpServers": {
  "email_task_mcp": {
    "command": "/absolute/path/to/email_task_mcp/.venv/bin/python",
    "args": ["/absolute/path/to/email_task_mcp/server.py"]
  }
}
```

Replace the two paths with your own absolute paths (`pwd` and `which python` from inside the activated venv). Fully quit and reopen Claude Desktop afterward. The server should appear as a connector named `email_task_mcp`, with `add_task` and `send_email` listed as tools and `weekly_status_prompt` as an available prompt.

## Using the tools

- **`add_task`**: `description` (required), `due_date` (optional, free text). Appends to `tasks.json`.
- **`send_email`**: `recipient_email`, `subject`, `body` — all required. Sends a real email via your configured Gmail account.
- **`weekly_status_prompt`**: takes `recipient_email`, pulls the current task list, and generates a ready-made instruction for drafting and sending a status update.

## Security best practices implemented

### 1. Input sanitization (header injection prevention)

`send_email`'s `recipient_email` and `subject` fields are checked for `\r`/`\n` characters before being used to build the email message, preventing an attacker from injecting extra headers (e.g., a hidden `Bcc:`).

**Exploit demonstration** (`exploits/test_header_injection.py`): attempts to inject `Bcc: attacker@evil.com` via the subject line. Result: request is rejected before any email is sent.

### 2. Rate limiting

`send_email` is limited to 5 calls per 60-second sliding window (`security.py`, `RateLimiter`), preventing the tool from being used to send spam.

**Exploit demonstration** (`exploits/test_rate_limit.py`): fires 7 rapid `send_email` calls. Result: the first 5 succeed, the last 2 are rejected with a rate-limit error.

## Limitations

- The rate limiter's state is in-memory and per-process — it resets if the server restarts, and wouldn't hold up across multiple server instances.
- `add_task` has no equivalent input-sanitization check, since it only writes to a local JSON file with no header/command construction involved.
- No persistence beyond a flat JSON file — not suitable for concurrent access from multiple clients.

## Code citations

- `server.py`: the `MCPServer` pattern (formerly `FastMCP` in `mcp` v1) is adapted from the official MCP Python SDK v2 migration guide: https://py.sdk.modelcontextprotocol.io/v2/migration/#fastmcp-renamed-to-mcpserver