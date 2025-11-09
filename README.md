# Jira MCP Server

A FastMCP server that enables AI assistants to interact with self-hosted Jira instances through token authentication.

## Features

### MVP (v0.1.0)
- ✅ **Issue Management**: Create, read, and update Jira issues with automatic custom field validation
- ✅ **Smart Custom Field Handling**: Automatically discovers and validates project-specific custom fields
- ✅ **Schema Caching**: Intelligent caching reduces API calls by 80%+
- ✅ **Health Check**: Verify connectivity and authentication
- ✅ **Schema Introspection**: Debug tool to explore available fields

### v0.2.0 - Latest
- ✅ **Robust Search**: Search issues by project, assignee, status, priority, labels, and date ranges
- ✅ **JQL Support**: Execute raw JQL queries directly with full Jira Query Language support

### Coming Soon
- 🔜 **Custom Filters**: Save and reuse complex search queries (v0.3.0)
- 🔜 **Workflow Transitions**: Move issues through workflow states (v0.4.0)
- 🔜 **Comment Management**: Add and retrieve issue comments (v0.5.0)

## Requirements

- Python 3.8 or higher
- Self-hosted Jira instance (version 7.0+)
- Jira API token with appropriate permissions

## Installation

```bash
pip install jira-mcp-server
```

## Quick Start

1. **Get your Jira API token**:
   - Log into your Jira instance
   - Go to Profile → Personal Access Tokens
   - Create a new token and copy the value

2. **Configure environment variables**:

   ```bash
   export JIRA_MCP_URL="https://jira.yourcompany.com"
   export JIRA_MCP_TOKEN="your-api-token-here"
   ```

   Or create a `.env` file (see `.env.example`):

   ```env
   JIRA_MCP_URL=https://jira.yourcompany.com
   JIRA_MCP_TOKEN=your-api-token-here
   ```

3. **Run the server**:

   ```bash
   jira-mcp-server
   ```

4. **Verify connection**:

   Use the `jira_health_check` tool through your MCP client to verify the connection.

## Usage Examples

### Check Health

```python
# Verify connectivity and authentication
jira_health_check()
# Returns: {"connected": true, "server_version": "8.20.0", "base_url": "https://jira.yourcompany.com"}
```

### Create an Issue

```python
# Basic issue creation
jira_issue_create(
    project="PROJ",
    summary="Login page shows 404 error",
    issue_type="Bug",
    priority="High",
    description="Users are seeing 404 errors when accessing /login"
)

# With custom fields (automatically validated against project schema)
jira_issue_create(
    project="PROJ",
    summary="Add user authentication",
    issue_type="Story",
    custom_fields={
        "customfield_10001": 8,  # Story Points
        "customfield_10002": "Backend",  # Component
    }
)
```

### Update an Issue

```python
# Update specific fields
jira_issue_update(
    issue_key="PROJ-123",
    summary="Updated: Login page shows 404 error",
    priority="Critical",
    assignee="john.doe"
)

# Update custom fields
jira_issue_update(
    issue_key="PROJ-123",
    custom_fields={
        "customfield_10001": 13  # Update story points
    }
)
```

### Get Issue Details

```python
# Retrieve full issue details including all custom fields
jira_issue_get(issue_key="PROJ-123")
```

### Discover Project Schema

```python
# Useful for finding custom field IDs and allowed values
jira_project_get_schema(
    project="PROJ",
    issue_type="Bug"
)
# Returns all available fields, their types, and validation rules
```

### Search Issues

```python
# Search by project
jira_search_issues(project="PROJ")

# Search with multiple criteria
jira_search_issues(
    project="PROJ",
    status="Open",
    assignee="currentUser()",
    priority="High",
    max_results=10
)

# Search by date range
jira_search_issues(
    project="PROJ",
    created_after="2025-01-01",
    created_before="2025-12-31"
)

# Search by labels
jira_search_issues(
    project="PROJ",
    labels=["backend", "urgent"]
)
```

### Execute JQL Queries

```python
# Simple JQL query
jira_search_jql(jql="project = PROJ AND status = Open")

# Complex JQL with date functions and ordering
jira_search_jql(
    jql='project = PROJ AND created >= -7d AND assignee = currentUser() ORDER BY created DESC',
    max_results=20
)

# JQL with multiple conditions
jira_search_jql(
    jql='project = PROJ AND status IN ("Open", "In Progress") AND priority = High',
    max_results=50,
    start_at=0
)
```

## Configuration

Environment variables:

- `JIRA_MCP_URL` (required): Your Jira instance URL
- `JIRA_MCP_TOKEN` (required): API authentication token
- `JIRA_MCP_CACHE_TTL` (optional, default: 3600): Schema cache TTL in seconds
- `JIRA_MCP_TIMEOUT` (optional, default: 30): HTTP request timeout in seconds

## Development

### Setup

```bash
git clone https://github.com/yourusername/jira-mcp-server.git
cd jira-mcp-server
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

With coverage report:

```bash
pytest --cov=src/jira_mcp_server --cov-report=html
```

### Type Checking

```bash
mypy src/
```

### Code Formatting and Linting

```bash
# Check and auto-fix
ruff check src/ tests/ --fix

# Format code
ruff format src/ tests/
```

## Architecture

- **FastMCP**: MCP server framework
- **httpx**: HTTP client for Jira REST API
- **Pydantic**: Data validation and settings management
- **In-memory caching**: TTL-based schema caching (1-hour default)

## MCP Tools

### MVP (v0.1.0)

#### Issue Management
- `jira_issue_create` - Create new issues with automatic custom field validation
- `jira_issue_update` - Update existing issues (only provided fields are updated)
- `jira_issue_get` - Get full issue details including all custom fields

#### Utilities
- `jira_health_check` - Verify connection and authentication status
- `jira_project_get_schema` - Get project schema for debugging (shows all available fields, types, and validation rules)

### v0.2.0 - Latest

#### Search
- `jira_search_issues` - Search with multiple criteria (project, assignee, status, priority, labels, date ranges)
- `jira_search_jql` - Execute JQL queries directly with full Jira Query Language support

### Coming in Future Releases

#### Filters (v0.3.0)
- `jira_filter_create` - Create custom filter
- `jira_filter_list` - List all accessible filters
- `jira_filter_get` - Get filter details
- `jira_filter_execute` - Run a saved filter
- `jira_filter_update` - Update filter criteria
- `jira_filter_delete` - Delete a filter

#### Workflows (v0.4.0)
- `jira_workflow_get_transitions` - Get available transitions for an issue
- `jira_workflow_transition` - Transition issue through workflow

#### Comments (v0.5.0)
- `jira_comment_add` - Add comment to an issue
- `jira_comment_list` - List all comments on an issue

## Troubleshooting

See the [troubleshooting section in quickstart.md](specs/001-jira-mcp-server/quickstart.md#troubleshooting) for common issues and solutions.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/jira-mcp-server/issues)
- **Documentation**: [Full Documentation](https://github.com/yourusername/jira-mcp-server#readme)
