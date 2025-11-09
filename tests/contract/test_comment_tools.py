"""Contract tests for comment tools (T060-T061)"""

from unittest.mock import Mock

import pytest

from jira_mcp_server.jira_client import JiraClient
from jira_mcp_server.tools.comment_tools import (
    initialize_comment_tools,
    jira_comment_add,
    jira_comment_list,
)


@pytest.fixture
def mock_client() -> JiraClient:
    """Create a mock JiraClient."""
    return Mock(spec=JiraClient)


class TestCommentToolsContract:
    """Contract tests for comment tools."""

    def test_initialize_comment_tools_sets_client(self, mock_client: JiraClient) -> None:
        """Test that initialize_comment_tools sets up global client."""
        initialize_comment_tools(mock_client)
        # Can't directly test global variable, but should not raise

    def test_jira_comment_add_signature(self, mock_client: JiraClient) -> None:
        """Test jira_comment_add function signature matches contract (T060)."""
        initialize_comment_tools(mock_client)
        mock_client.add_comment.return_value = {
            "id": "10001",
            "body": "Test comment",
            "author": {"displayName": "John Doe"},
            "created": "2025-01-15T10:00:00.000+0000",
        }

        result = jira_comment_add(issue_key="PROJ-123", body="Test comment")

        # Verify function accepts required parameters
        assert "id" in result
        assert "body" in result
        mock_client.add_comment.assert_called_once()

    def test_jira_comment_list_signature(self, mock_client: JiraClient) -> None:
        """Test jira_comment_list function signature matches contract (T061)."""
        initialize_comment_tools(mock_client)
        mock_client.list_comments.return_value = {
            "comments": [
                {
                    "id": "10001",
                    "body": "Comment 1",
                    "author": {"displayName": "John Doe"},
                    "created": "2025-01-15T10:00:00.000+0000",
                }
            ],
            "total": 1,
        }

        result = jira_comment_list(issue_key="PROJ-123")

        # Verify function accepts required parameters
        assert "comments" in result
        assert "total" in result
        mock_client.list_comments.assert_called_once()

    def test_jira_comment_add_returns_dict(self, mock_client: JiraClient) -> None:
        """Test jira_comment_add returns dictionary."""
        initialize_comment_tools(mock_client)
        mock_client.add_comment.return_value = {"id": "10001"}

        result = jira_comment_add(issue_key="PROJ-123", body="Test")

        assert isinstance(result, dict)

    def test_jira_comment_list_returns_dict(self, mock_client: JiraClient) -> None:
        """Test jira_comment_list returns dictionary."""
        initialize_comment_tools(mock_client)
        mock_client.list_comments.return_value = {"comments": [], "total": 0}

        result = jira_comment_list(issue_key="PROJ-123")

        assert isinstance(result, dict)

    def test_jira_comment_add_requires_issue_key(self, mock_client: JiraClient) -> None:
        """Test jira_comment_add requires issue_key parameter."""
        initialize_comment_tools(mock_client)

        with pytest.raises((ValueError, TypeError)):
            jira_comment_add(issue_key="", body="Test")  # type: ignore[arg-type]

    def test_jira_comment_add_requires_body(self, mock_client: JiraClient) -> None:
        """Test jira_comment_add requires body parameter."""
        initialize_comment_tools(mock_client)

        with pytest.raises((ValueError, TypeError)):
            jira_comment_add(issue_key="PROJ-123", body="")  # type: ignore[arg-type]

    def test_jira_comment_list_requires_issue_key(self, mock_client: JiraClient) -> None:
        """Test jira_comment_list requires issue_key parameter."""
        initialize_comment_tools(mock_client)

        with pytest.raises((ValueError, TypeError)):
            jira_comment_list(issue_key="")  # type: ignore[arg-type]

    def test_jira_comment_add_validates_empty_issue_key(self, mock_client: JiraClient) -> None:
        """Test that empty issue key raises ValueError."""
        initialize_comment_tools(mock_client)

        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_comment_add(issue_key="", body="Test")

    def test_jira_comment_add_validates_empty_body(self, mock_client: JiraClient) -> None:
        """Test that empty comment body raises ValueError."""
        initialize_comment_tools(mock_client)

        with pytest.raises(ValueError, match="Comment body cannot be empty"):
            jira_comment_add(issue_key="PROJ-123", body="")

    def test_jira_comment_list_validates_empty_issue_key(self, mock_client: JiraClient) -> None:
        """Test that empty issue key raises ValueError."""
        initialize_comment_tools(mock_client)

        with pytest.raises(ValueError, match="Issue key cannot be empty"):
            jira_comment_list(issue_key="")

    def test_jira_comment_add_handles_api_errors(self, mock_client: JiraClient) -> None:
        """Test jira_comment_add handles API errors gracefully."""
        initialize_comment_tools(mock_client)
        mock_client.add_comment.side_effect = Exception("API error")

        with pytest.raises(ValueError, match="Add comment failed"):
            jira_comment_add(issue_key="PROJ-123", body="Test")

    def test_jira_comment_list_handles_api_errors(self, mock_client: JiraClient) -> None:
        """Test jira_comment_list handles API errors gracefully."""
        initialize_comment_tools(mock_client)
        mock_client.list_comments.side_effect = Exception("API error")

        with pytest.raises(ValueError, match="List comments failed"):
            jira_comment_list(issue_key="PROJ-123")
