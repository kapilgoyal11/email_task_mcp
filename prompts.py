"""
MCP prompt for the email_task_mcp server.

A prompt is a reusable instruction template exposed to the MCP client —
distinct from a tool (which performs an action) and a resource (which
exposes raw data). This one turns the current task list into an
instruction the LLM can use to draft a status update email, tying the
add_task and send_email tools together into one workflow.
"""
from storage import load_tasks


def build_weekly_status_prompt(recipient_email: str) -> str:
    tasks = load_tasks()

    if not tasks:
        task_lines = "(No tasks currently tracked.)"
    else:
        task_lines = "\n".join(
            f"- {t['description']}"
            + (f" (due {t['due_date']})" if t.get("due_date") else "")
            + (" [DONE]" if t.get("done") else "")
            for t in tasks
        )

    return (
        f"Draft a concise, professional status-update email to {recipient_email} "
        f"summarizing the following tasks. Group them into 'Completed' and "
        f"'In Progress' sections. After drafting it, use the send_email tool "
        f"to actually send it.\n\nCurrent tasks:\n{task_lines}"
    )