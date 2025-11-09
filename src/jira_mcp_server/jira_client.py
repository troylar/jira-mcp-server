"""Jira REST API client (T018-T019)"""

from typing import Any, Dict, List

import httpx

from jira_mcp_server.config import JiraConfig


class JiraClient:
    """HTTP client for Jira REST API v2.

    Handles authentication, requests, and error handling for all Jira API interactions.
    """

    def __init__(self, config: JiraConfig):
        """Initialize Jira client.

        Args:
            config: JiraConfig with URL and authentication token
        """
        self.base_url = config.jira_url
        self.timeout = config.timeout
        self._token = config.jira_token

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication.

        Returns:
            Dictionary of HTTP headers
        """
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle HTTP error responses with actionable messages.

        Args:
            response: HTTP response object

        Raises:
            ValueError: With context-specific error message
        """
        status = response.status_code

        if status == 401:
            raise ValueError("Authentication failed. Check your JIRA_MCP_TOKEN is valid and hasn't expired.")
        elif status == 403:
            raise ValueError("Permission denied. Your token doesn't have access to this resource.")
        elif status == 404:
            raise ValueError(f"Resource not found. The requested {self._get_resource_type(response)} does not exist.")
        elif status == 429:
            raise ValueError("Rate limit exceeded. Too many requests to Jira API. Please wait before retrying.")
        elif status == 400:
            # Parse validation errors from response
            try:
                error_data = response.json()
                errors = error_data.get("errors", {})
                messages = error_data.get("errorMessages", [])

                if errors:
                    error_str = ", ".join(f"{field}: {msg}" for field, msg in errors.items())
                    raise ValueError(f"Validation error: {error_str}")
                elif messages:
                    raise ValueError(f"Validation error: {', '.join(messages)}")
            except (ValueError, KeyError) as e:
                # Re-raise ValueError from validation, catch only JSON parsing errors
                if "Validation error" in str(e):
                    raise
                pass

            raise ValueError(f"Bad request: {response.text[:200]}")
        else:
            raise ValueError(f"Jira API error ({status}): {response.text[:200]}")

    def _get_resource_type(self, response: httpx.Response) -> str:
        """Determine resource type from URL for better error messages.

        Args:
            response: HTTP response object

        Returns:
            Resource type string (e.g., "issue", "project")
        """
        url = str(response.request.url)
        if "/issue/" in url:
            return "issue"
        elif "/project/" in url:
            return "project"
        elif "/filter/" in url:
            return "filter"
        else:
            return "resource"

    def health_check(self) -> Dict[str, Any]:
        """Verify connectivity to Jira instance (T019).

        Returns:
            Dictionary with connection status and server info

        Raises:
            ValueError: If connection fails or authentication error
        """
        url = f"{self.base_url}/rest/api/2/serverInfo"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self._get_headers())

                if response.status_code != 200:
                    self._handle_error(response)

                server_info = response.json()
                return {
                    "connected": True,
                    "server_version": server_info.get("version", "unknown"),
                    "base_url": server_info.get("baseUrl", self.base_url),
                }

        except httpx.TimeoutException:
            raise ValueError(
                f"Connection timeout. Could not reach Jira at {self.base_url} within {self.timeout} seconds."
            )
        except httpx.NetworkError as e:
            raise ValueError(f"Network error connecting to Jira: {str(e)}")

    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get issue details by key.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")

        Returns:
            Issue data dictionary

        Raises:
            ValueError: If issue not found or API error
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self._get_headers())

                if response.status_code != 200:
                    if response.status_code == 404:
                        raise ValueError(f"Issue {issue_key} not found.")
                    self._handle_error(response)

                return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise ValueError(f"Timeout getting issue {issue_key}")

    def create_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new issue.

        Args:
            issue_data: Issue fields and metadata

        Returns:
            Created issue data with key and ID

        Raises:
            ValueError: If validation fails or API error
        """
        url = f"{self.base_url}/rest/api/2/issue"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=self._get_headers(), json=issue_data)

                if response.status_code not in (200, 201):
                    self._handle_error(response)

                return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise ValueError("Timeout creating issue")

    def update_issue(self, issue_key: str, update_data: Dict[str, Any]) -> None:
        """Update an existing issue.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            update_data: Fields to update

        Raises:
            ValueError: If issue not found or validation fails
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.put(url, headers=self._get_headers(), json=update_data)

                if response.status_code not in (200, 204):
                    self._handle_error(response)

        except httpx.TimeoutException:
            raise ValueError(f"Timeout updating issue {issue_key}")

    def get_project_schema(self, project_key: str, issue_type: str) -> List[Dict[str, Any]]:
        """Get field schema for a project and issue type.

        Args:
            project_key: Project key
            issue_type: Issue type name

        Returns:
            List of field definitions

        Raises:
            ValueError: If project not found or API error
        """
        url = f"{self.base_url}/rest/api/2/issue/createmeta"
        params = {
            "projectKeys": project_key,
            "issuetypeNames": issue_type,
            "expand": "projects.issuetypes.fields",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self._get_headers(), params=params)

                if response.status_code != 200:
                    self._handle_error(response)

                data = response.json()
                projects = data.get("projects", [])

                if not projects:
                    raise ValueError(f"Project {project_key} not found or no issue types available")

                issue_types = projects[0].get("issuetypes", [])
                if not issue_types:
                    raise ValueError(f"Issue type {issue_type} not found in project {project_key}")

                fields = issue_types[0].get("fields", {})
                return [{"key": k, **v} for k, v in fields.items()]

        except httpx.TimeoutException:
            raise ValueError(f"Timeout getting schema for {project_key}/{issue_type}")

    def search_issues(self, jql: str, max_results: int = 100, start_at: int = 0) -> Dict[str, Any]:
        """Search issues using JQL.

        Args:
            jql: JQL query string
            max_results: Maximum results to return
            start_at: Starting offset for pagination

        Returns:
            Search results with issues and pagination info

        Raises:
            ValueError: If JQL invalid or API error
        """
        url = f"{self.base_url}/rest/api/2/search"
        data = {"jql": jql, "maxResults": max_results, "startAt": start_at}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=self._get_headers(), json=data)

                if response.status_code != 200:
                    self._handle_error(response)

                return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise ValueError("Timeout executing search query")
