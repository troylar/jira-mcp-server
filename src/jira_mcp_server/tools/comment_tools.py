"""MCP tools for issue comments (T060-T061)"""

from typing import Any, Dict, Optional

from jira_mcp_server.jira_client import JiraClient

# Global client instance (initialized by server)
_client: Optional[JiraClient] = None


def initialize_comment_tools(client: JiraClient) -> None:
    """Initialize comment tools with JiraClient instance.

    Args:
        client: JiraClient instance
    """
    global _client
    _client = client


def jira_comment_add(issue_key: str, body: str) -> Dict[str, Any]:
    """Add a comment to an issue (T060).

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        body: Comment text (supports Jira markup)

    Returns:
        Created comment with ID, author, and timestamp

    Raises:
        ValueError: If issue not found or validation fails

    Example:
        jira_comment_add(
            issue_key="PROJ-123",
            body="This issue is ready for review"
        )
    """
    if not _client:
        raise RuntimeError("Comment tools not initialized")

    if not issue_key or not issue_key.strip():
        raise ValueError("Issue key cannot be empty")

    if not body or not body.strip():
        raise ValueError("Comment body cannot be empty")

    try:
        return _client.add_comment(issue_key=issue_key, body=body)
    except Exception as e:
        raise ValueError(f"Add comment failed: {str(e)}")


def jira_comment_list(issue_key: str) -> Dict[str, Any]:
    """List all comments on an issue (T061).

    Retrieves all comments with author, timestamp, and comment text.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")

    Returns:
        Comments list with total count and comment details

    Raises:
        ValueError: If issue not found or access denied

    Example:
        jira_comment_list(issue_key="PROJ-123")
    """
    if not _client:
        raise RuntimeError("Comment tools not initialized")

    if not issue_key or not issue_key.strip():
        raise ValueError("Issue key cannot be empty")

    try:
        return _client.list_comments(issue_key=issue_key)
    except Exception as e:
        raise ValueError(f"List comments failed: {str(e)}")
