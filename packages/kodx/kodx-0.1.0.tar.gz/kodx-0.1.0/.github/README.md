# GitHub Automation for Kodx

This directory contains GitHub Actions workflows and configurations for automated Kodx usage.

## Workflows

### `/code` - Automated Code Implementation

**File**: `.github/workflows/kodx-code.yml`  
**Program**: `.github/config/kodx-code-program.yaml`

Implements code changes requested in GitHub issues or pull requests.

**Usage:**
```
/code Add a new feature to handle CSV exports
```

**Dev Mode (uses source code):**
```
dev /code Add a new feature to handle CSV exports
```

**What it does:**
1. Creates a new feature branch
2. Runs Kodx with the code expert program in a Docker container
3. Exports changes from the container to the repository
4. Commits changes and creates a pull request
5. Labels PR with `kodx` for easy tracking

### `/ask` - Repository Q&A

**File**: `.github/workflows/kodx-ask.yml`  
**Program**: `.github/config/kodx-ask-program.yaml`

Answers questions about the codebase using Kodx analysis.

**Usage:**
```
/ask How does the export functionality work?
```

**Dev Mode (uses source code):**
```
dev /ask How does the export functionality work?
```

**What it does:**
1. Analyzes the repository in a Docker container
2. Uses the ask expert program to understand and explain code
3. Posts a detailed answer as a comment reply

## Security

- Only responds to comments from repository owners, members, and collaborators
- Uses GitHub's default `GITHUB_TOKEN` for `/ask` workflow (no additional setup required)
- Uses custom `KODX_WRITE_TOKEN` for `/code` workflow (requires setup for pull request creation)
- Runs in isolated Docker containers for safety

## Setup Requirements

### For `/ask` workflow:
- `ANTHROPIC_API_KEY` secret (API key for Claude)

### For `/code` workflow:
- `ANTHROPIC_API_KEY` secret (API key for Claude)  
- `KODX_WRITE_TOKEN` secret (GitHub personal access token with `contents` and `pull-requests` permissions)

## Cost Control

Both workflows include automatic cost limits to prevent runaway expenses:

- **Code implementation**: Limited to $2.00 per request
- **Q&A responses**: Limited to $1.00 per request

Cost information is displayed in all status comments for transparency.

## Required Secrets

- `ANTHROPIC_API_KEY`: Your Claude API key from Anthropic

## Expert Programs

### Code Expert (`kodx-code-program.yaml`)

Specialized for:
- Implementing new features
- Fixing bugs and issues
- Writing tests
- Updating documentation
- Following project conventions

### Ask Expert (`kodx-ask-program.yaml`)

Specialized for:
- Code analysis and explanation
- Architecture review
- Documentation help
- Best practices guidance
- Technical Q&A

## Examples

### Code Implementation
```
/code Implement rate limiting for the API endpoints with configurable limits per user
```

### Code Questions
```
/ask What are the main components of the export system and how do they interact?
```

### Cost-Aware Responses
Both workflows automatically include cost tracking and will show cost information in responses:

✅ **Code implemented successfully with Kodx!** — [View PR](https://github.com/repo/pull/123) | [View logs](https://github.com/repo/actions/runs/456) (cost: $0.0234)

⚠️ **Code request stopped due to cost limit** — [View logs](https://github.com/repo/actions/runs/789) (cost: $2.0000)

### Multi-line Requests
```
/code Please implement the following:
- Add input validation for user uploads
- Include proper error handling
- Write unit tests for the new functionality
```

## Tips

- Be specific in your requests for better results
- Include context about requirements or constraints
- Reference specific files or functions when asking questions
- Check the Actions tab to see workflow progress and logs

## Troubleshooting

- If workflows don't trigger, check that you're a collaborator on the repository
- Ensure the `ANTHROPIC_API_KEY` secret is configured in repository settings
- View workflow logs in the Actions tab for detailed error information
- Export functionality requires Docker to be available in the runner
