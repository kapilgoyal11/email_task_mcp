"""
MCP tools for the email_task_mcp server.
"""
import smtplib
from email.message import EmailMessage

from storage import load_tasks, save_tasks
from config import SMTP_EMAIL, SMTP_APP_PASSWORD
from security import sanitize_header, HeaderInjectionError, RateLimiter


def add_task(description: str, due_date: str | None = None) -> dict:
    """Add a new task to the local task list.

    Args:
        description: What the task is (required).
        due_date: Optional due date, as free text (e.g. "2026-09-25").

    Returns:
        A dict confirming what was added and the new task count.
    """
    description = description.strip()
    if not description:
        return {"status": "error", "message": "Task description cannot be empty."}

    tasks = load_tasks()
    task = {"id": len(tasks) + 1, "description": description, "due_date": due_date, "done": False}
    tasks.append(task)
    save_tasks(tasks)

    return {"status": "success", "task": task, "total_tasks": len(tasks)}


# Max 5 sends per 60 seconds — generous for a demo, tight enough to
# make the exploit test fail obviously when exceeded.
_email_rate_limiter = RateLimiter(max_calls=5, window_seconds=60)


def send_email(recipient_email: str, subject: str, body: str) -> dict:
    """Send an email with the given subject and body.

    Args:
        recipient_email: Destination email address.
        subject: Email subject line.
        body: Email body text.

    Returns:
        A dict indicating success or a safe, non-revealing error message.
    """
    if not _email_rate_limiter.allow():
        return {
            "status": "error",
            "message": "Rate limit exceeded: max 5 emails per 60 seconds. Try again shortly.",
        }

    try:
        recipient_email = sanitize_header(recipient_email, "recipient_email")
        subject = sanitize_header(subject, "subject")
    except HeaderInjectionError as e:
        return {"status": "error", "message": str(e)}

    msg = EmailMessage()
    msg["From"] = SMTP_EMAIL
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            server.send_message(msg)
    except smtplib.SMTPException:
        # Error Disclosure caution: never return the raw exception
        # (it could reveal the account, server internals, or leak
        # credential-related details) to the MCP client/LLM.
        return {"status": "error", "message": "Failed to send email. Please try again later."}

    return {"status": "success", "message": f"Email sent to {recipient_email}"}