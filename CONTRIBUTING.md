# Contributing to SmartCitySense

Thank you for your interest in contributing to SmartCitySense! This document provides guidelines and instructions for contributing.

## 🎯 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:
- Python 3.8+ installed
- Node.js 16+ installed
- Git configured with your GitHub account
- Firebase account (for testing)

### Setting Up Development Environment

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/SmartCitySense.git
   cd SmartCitySense
   ```

2. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/Kushagrakumar12/SmartCitySense.git
   ```

3. **Set up the project**
   ```bash
   ./setup_complete.sh
   ```

4. **Create a branch for your feature**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Development Workflow

### 1. Before You Start

- Check existing issues and pull requests to avoid duplicates
- Create an issue describing what you plan to work on
- Wait for approval/discussion before starting major changes
- Ensure you're working on the latest code:
  ```bash
  git fetch upstream
  git rebase upstream/main
  ```

### 2. Making Changes

#### Code Style

**Python**:
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Keep functions small and focused

**JavaScript/React**:
- Use ES6+ syntax
- Follow Airbnb JavaScript Style Guide
- Use functional components with hooks
- Add PropTypes for all components

**General**:
- Write self-documenting code
- Add comments for complex logic
- Keep line length under 100 characters
- Use meaningful variable and function names

#### Testing

**Always add tests for new features**:

```bash
# Python modules
cd ai-ml && pytest tests/test_your_feature.py -v

# Run all tests
pytest tests/ -v --cov=.

# JavaScript
cd frontend && npm test
```

**Test requirements**:
- Unit tests for all new functions
- Integration tests for API endpoints
- Test both success and error cases
- Aim for >80% code coverage

#### Commit Messages

Follow conventional commits:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```bash
feat(ai-ml): add multilingual support for sentiment analysis

fix(data-ingestion): handle Reddit API rate limiting correctly

docs(readme): update installation instructions for macOS

test(backend): add integration tests for authentication
```

### 3. Submitting Changes

1. **Ensure all tests pass**
   ```bash
   # Test your module
   pytest tests/ -v
   
   # Run linting
   flake8 . --max-line-length=100
   ```

2. **Update documentation**
   - Update README.md if you changed functionality
   - Add docstrings to new functions
   - Update API documentation if endpoints changed

3. **Push your changes**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request**
   - Go to GitHub and create a PR from your fork
   - Fill in the PR template completely
   - Link related issues
   - Request review from maintainers

## 🔍 Pull Request Guidelines

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts with main branch
- [ ] PR description clearly explains changes
- [ ] Related issues are linked

### PR Description Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #(issue number)

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
Describe how you tested your changes

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code reviewed
```

## 🐛 Reporting Bugs

### Before Reporting

- Check if the bug has already been reported
- Verify it's actually a bug and not a configuration issue
- Try to reproduce with the latest code

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 13.0]
- Python version: [e.g., 3.9.6]
- Module: [e.g., ai-ml]

## Additional Context
Any other relevant information

## Screenshots/Logs
If applicable
```

## 💡 Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this work?

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Any other relevant information
```

## 📦 Module-Specific Guidelines

### Data Ingestion Module

- Always handle API rate limits
- Add retry logic with exponential backoff
- Log all data source errors
- Validate data before publishing

### Data Processing Module

- Ensure idempotent processing
- Add monitoring metrics
- Handle malformed data gracefully
- Test with large data volumes

### AI/ML Module

- Document model parameters
- Include model performance metrics
- Test with edge cases
- Optimize for inference speed

### Backend API

- Follow REST conventions
- Add input validation
- Include proper error responses
- Update OpenAPI documentation

### Frontend

- Ensure responsive design
- Test on multiple browsers
- Optimize bundle size
- Follow accessibility guidelines

## 🧪 Testing Guidelines

### Unit Tests

```python
# Example test structure
def test_feature_name():
    """Test description"""
    # Arrange
    input_data = {"key": "value"}
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result.status == "success"
    assert result.data["key"] == "expected_value"
```

### Integration Tests

- Test complete workflows
- Use test Firebase project
- Mock external APIs
- Test error handling

### Performance Tests

- Benchmark critical paths
- Test with realistic data volumes
- Monitor memory usage
- Profile slow functions

## 📚 Documentation

### Code Documentation

```python
def process_event(event_data: Dict[str, Any], options: Optional[Dict] = None) -> ProcessedEvent:
    """
    Process an incoming event with optional configuration.
    
    Args:
        event_data: Raw event data containing type, location, and description
        options: Optional processing configuration
            - validate: Whether to validate input (default: True)
            - enrich: Whether to enrich with additional data (default: True)
    
    Returns:
        ProcessedEvent: Processed event with enriched metadata
        
    Raises:
        ValidationError: If event_data is invalid
        ProcessingError: If processing fails
        
    Example:
        >>> event = {"type": "traffic", "location": "MG Road"}
        >>> result = process_event(event)
        >>> result.status
        'processed'
    """
    # Implementation
```

### README Updates

- Keep README.md up to date
- Include code examples
- Document configuration changes
- Update architecture diagrams

## 🔒 Security

### Reporting Security Issues

**Do not open public issues for security vulnerabilities**

Email security concerns to: [your-email@example.com]

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Best Practices

- Never commit credentials
- Use environment variables for secrets
- Validate all inputs
- Sanitize user data
- Follow OWASP guidelines

## 📋 Code Review Process

### For Contributors

- Respond to review comments promptly
- Make requested changes in new commits
- Update PR description if scope changes
- Be open to feedback

### For Reviewers

- Review code within 48 hours
- Provide constructive feedback
- Check for security issues
- Verify tests pass
- Approve when ready

## 🎓 Learning Resources

### Python

- [PEP 8 Style Guide](https://pep8.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PyTest Tutorial](https://docs.pytest.org/)

### React

- [React Documentation](https://react.dev/)
- [React Hooks](https://react.dev/reference/react)
- [Testing Library](https://testing-library.com/react)

### AI/ML

- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [Scikit-learn Guide](https://scikit-learn.org/stable/)

## 🤝 Community

### Getting Help

- Check existing documentation
- Search closed issues
- Ask in discussions
- Join our Discord (if available)

### Helping Others

- Answer questions in issues
- Review pull requests
- Improve documentation
- Share your experience

## 📄 License

By contributing to SmartCitySense, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to SmartCitySense! 🏙️🤖
