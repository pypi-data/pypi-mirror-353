# py-jira

A Python client library for JIRA API that provides easy-to-use interfaces for interacting with Atlassian JIRA instances.

## Installation

### Install from GitHub

**⚠️ Important**: Replace `codegen-sh/py-jira` with your actual GitHub username and repository name in the commands below.

You can install this package directly from GitHub using pip or uv:

```bash
# Using pip
pip install git+https://github.com/codegen-sh/py-jira.git

# Using uv
uv add git+https://github.com/codegen-sh/py-jira.git
```

### Install specific version or branch

```bash
# Install specific tag/version
pip install git+https://github.com/codegen-sh/py-jira.git@v0.1.0

# Install from specific branch
pip install git+https://github.com/codegen-sh/py-jira.git@main
```

### Install with optional dependencies

```bash
# Install with development dependencies
pip install "git+https://github.com/codegen-sh/py-jira.git[dev]"
```

## Usage

```python
from jira_client import ApiClient, Configuration
from jira_client.api.issues_api import IssuesApi

# Configure the client
config = Configuration()
config.host = "https://code-gen.atlassian.net"
# Add authentication configuration as needed

# Initialize the client
api_client = ApiClient(configuration=config)
issues_api = IssuesApi(api_client)

# Use the API
# issues = issues_api.search_for_issues_using_jql(jql="project = TEST")
```

## Package Structure

This package includes:
- Complete JIRA REST API client generated from OpenAPI specifications
- Type hints support (`py.typed` file included)
- All JIRA API endpoints and models
- Configurable authentication and connection settings

## Dependencies

The package has minimal runtime dependencies:
- `urllib3>=1.25.3` - HTTP client
- `pydantic>=2.0.0` - Data validation
- `python-dateutil>=2.8.0` - Date parsing utilities

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/codegen-sh/py-jira.git
cd py-jira

# Install with development dependencies
uv sync --dev

# Run tests
pytest

# Run linting
ruff check .

# Run type checking
mypy .

# Build the package
uv build
```

## Configuration for Publishing

If you want to use this package in your projects, make sure to:

1. **Update the GitHub URLs** in `pyproject.toml`:
   - Replace `codegen-sh` with your actual GitHub username
   - Update the repository name if different

2. **Update author information** in `pyproject.toml`:
   - Replace the placeholder name and email with your details

3. **Create a proper README** with usage examples specific to your implementation

4. **Tag releases** for version management:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
