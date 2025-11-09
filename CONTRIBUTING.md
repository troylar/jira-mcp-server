# Contributing to Jira MCP Server

Thank you for your interest in contributing to the Jira MCP Server! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.10 or higher (for development)
- Git
- A Jira instance for testing (can use a free Atlassian Cloud trial)

### Initial Setup

1. **Fork and clone the repository**:

   ```bash
   git clone https://github.com/yourusername/jira-mcp-server.git
   cd jira-mcp-server
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:

   ```bash
   pip install -e ".[dev]"
   ```

4. **Configure environment variables** for testing:

   Create a `.env` file (see `.env.example`):

   ```env
   JIRA_MCP_URL=https://your-test-jira.com
   JIRA_MCP_TOKEN=your-test-token
   JIRA_MCP_CACHE_TTL=3600
   JIRA_MCP_TIMEOUT=30
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

Follow the code style and testing guidelines below.

### 3. Run Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/unit/test_config.py

# Run with verbose output
pytest -v

# Run fast (without coverage)
pytest --no-cov
```

**All tests must pass and coverage must remain at 100%.**

### 4. Code Quality Checks

```bash
# Type checking
mypy src/

# Linting and formatting
ruff check src/ tests/ --fix
ruff format src/ tests/
```

All checks must pass before submitting a PR.

### 5. Commit Your Changes

Use conventional commit messages:

```
feat: add support for attachments
fix: resolve caching issue with custom fields
docs: update installation instructions
test: add tests for schema validation
refactor: simplify error handling logic
```

### 6. Push and Create Pull Request

```bash
git push origin your-branch-name
```

Then create a pull request on GitHub.

## Code Style Guidelines

### Python Style

- **Line length**: 120 characters maximum
- **Type hints**: Required for all functions and methods
- **Docstrings**: Required for all public functions, classes, and methods
- **Formatting**: Use ruff for formatting and linting

### Type Hints

All functions must have complete type hints:

```python
def create_issue(
    project: str,
    summary: str,
    issue_type: str = "Task",
) -> Dict[str, Any]:
    """Create a Jira issue.

    Args:
        project: Project key
        summary: Issue summary
        issue_type: Type of issue

    Returns:
        Created issue data
    """
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def validate_field(value: Any, schema: FieldSchema) -> bool:
    """Validate a field value against its schema.

    Args:
        value: The value to validate
        schema: Field schema with type and validation rules

    Returns:
        True if valid, False otherwise

    Raises:
        FieldValidationError: If validation fails with details
    """
    pass
```

## Testing Guidelines

### Test Organization

- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests with mocked HTTP calls
- `tests/contract/` - Contract tests for MCP tool interfaces

### Writing Tests

1. **Test-Driven Development (TDD)**: Write tests before implementation
2. **100% Coverage Required**: All code must be covered by tests
3. **Use descriptive test names**:

```python
def test_create_issue_validates_required_fields() -> None:
    """Test that create_issue rejects requests missing required fields."""
    pass
```

4. **Follow the AAA pattern** (Arrange, Act, Assert):

```python
def test_schema_cache_expiration() -> None:
    """Test that cached schemas expire after TTL."""
    # Arrange
    cache = SchemaCache(ttl_seconds=1)
    schema = [FieldSchema(...)]

    # Act
    cache.set("PROJ", "Task", schema)
    time.sleep(2)
    result = cache.get("PROJ", "Task")

    # Assert
    assert result is None
```

### Test Coverage

Use `pragma: no cover` sparingly and only for:
- FastMCP decorator wrappers that can't be tested directly
- Code that explicitly loads from environment (pydantic-settings)

All business logic must be testable and tested.

## Architecture Guidelines

### Project Structure

```
src/jira_mcp_server/
├── __init__.py          # Package initialization
├── config.py            # Configuration (pydantic-settings)
├── models.py            # Pydantic models
├── jira_client.py       # HTTP client for Jira API
├── schema_cache.py      # TTL-based caching
├── validators.py        # Field validation logic
├── server.py            # FastMCP server and tool registration
└── tools/
    ├── __init__.py
    └── issue_tools.py   # MCP tool implementations
```

### Design Principles

1. **Separation of Concerns**:
   - `jira_client.py` - HTTP communication only
   - `validators.py` - Validation logic only
   - `tools/` - MCP tool interfaces only

2. **Error Handling**:
   - Use descriptive error messages
   - Include actionable guidance in errors
   - Map HTTP errors to user-friendly messages

3. **Caching**:
   - Cache expensive operations (schema fetching)
   - Use TTL to prevent stale data
   - Make caching transparent to users

4. **Testing**:
   - Mock all external dependencies (HTTP calls)
   - Test error paths as thoroughly as success paths
   - Use fixtures for common test data

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass (`pytest`)
- [ ] 100% code coverage maintained
- [ ] Type checking passes (`mypy src/`)
- [ ] Code is formatted (`ruff format src/ tests/`)
- [ ] Linting passes (`ruff check src/ tests/`)
- [ ] Commit messages follow conventional commits
- [ ] Documentation updated if needed

### PR Description

Include:
1. **What** changed
2. **Why** the change was needed
3. **How** it was implemented
4. **Testing** performed

Example:
```markdown
## Description
Adds support for updating issue attachments.

## Motivation
Users need to attach files to issues programmatically.

## Implementation
- Added `add_attachment` method to JiraClient
- Added `jira_issue_add_attachment` MCP tool
- Implemented multipart form data handling

## Testing
- Added 5 unit tests for attachment validation
- Added 3 integration tests with mocked HTTP
- Manual testing with real Jira instance
```

## Feature Development Workflow

### Adding a New MCP Tool

1. **Define the contract** (in comments or separate spec):
   ```python
   # Tool: jira_issue_add_attachment
   # Parameters: issue_key (required), file_path (required), comment (optional)
   # Returns: attachment metadata
   ```

2. **Write contract tests** (`tests/contract/`):
   ```python
   def test_tool_has_required_parameters() -> None:
       """Verify tool signature matches contract."""
       pass
   ```

3. **Write unit tests** (`tests/unit/`):
   ```python
   def test_add_attachment_validates_file_exists() -> None:
       """Test that invalid file paths are rejected."""
       pass
   ```

4. **Implement the tool**:
   ```python
   def jira_issue_add_attachment(
       issue_key: str,
       file_path: str,
       comment: str = ""
   ) -> Dict[str, Any]:
       """Add an attachment to an issue."""
       pass
   ```

5. **Register with FastMCP** (`server.py`):
   ```python
   @mcp.tool()
   def jira_issue_add_attachment_tool(...) -> Dict[str, Any]:
       return jira_issue_add_attachment(...)
   ```

6. **Update documentation** (`README.md`).

## Versioning

We use Semantic Versioning (SemVer):

- **MAJOR**: Breaking API changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` (if exists)
3. Create git tag: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`
5. GitHub Actions will build and publish to PyPI

## Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/yourusername/jira-mcp-server/discussions)
- **Bugs**: Open a [GitHub Issue](https://github.com/yourusername/jira-mcp-server/issues)
- **Security**: Email security@yourcompany.com (do not open public issues)

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to make this project better.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
