# Contributing to SmartCitySense

Thank you for your interest in contributing to SmartCitySense! This document provides guidelines and instructions for contributing.

## 🌟 Ways to Contribute

- **Bug Reports**: Found a bug? Open an issue with detailed reproduction steps
- **Feature Requests**: Have an idea? Open an issue describing the feature
- **Code Contributions**: Submit pull requests with bug fixes or new features
- **Documentation**: Improve existing docs or add new ones
- **Testing**: Write tests to improve code coverage
- **Reviews**: Review pull requests and provide feedback

## 🚀 Getting Started

1. **Fork the Repository**
   ```bash
   # Click "Fork" button on GitHub
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/SmartCitySense.git
   cd SmartCitySense
   ```

3. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

4. **Set Up Development Environment**
   ```bash
   ./setup_complete.sh
   ```

## 💻 Development Workflow

### Making Changes

1. **Write Clean Code**
   - Follow PEP 8 for Python
   - Use ESLint/Prettier for JavaScript/TypeScript
   - Add comments for complex logic
   - Keep functions small and focused

2. **Test Your Changes**
   ```bash
   # Test specific module
   cd module-name
   ./test_all.sh
   
   # Or run specific tests
   pytest tests/test_your_feature.py
   ```

3. **Update Documentation**
   - Update README if needed
   - Add docstrings to new functions
   - Update API documentation

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

   **Commit Message Format**:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `test:` - Adding or updating tests
   - `refactor:` - Code refactoring
   - `style:` - Code style changes (formatting, etc.)
   - `chore:` - Maintenance tasks

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template with details

## 📋 Pull Request Guidelines

### Before Submitting

- ✅ Code follows project style guidelines
- ✅ All tests pass
- ✅ New tests added for new features
- ✅ Documentation updated
- ✅ No unnecessary dependencies added
- ✅ Commit messages are clear and descriptive

### PR Description Should Include

- **What**: Brief description of changes
- **Why**: Reason for the changes
- **How**: How the changes work
- **Testing**: How you tested the changes
- **Screenshots**: If UI changes are involved

### Example PR Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested locally
- [ ] Added/updated tests
- [ ] All tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No console warnings/errors
```

## 🧪 Testing Guidelines

### Writing Tests

```python
# tests/test_feature.py
import pytest

def test_feature():
    """Test description"""
    # Arrange
    input_data = {...}
    
    # Act
    result = your_function(input_data)
    
    # Assert
    assert result == expected_output
```

### Running Tests

```bash
# All tests
pytest

# Specific module
pytest tests/test_module.py

# With coverage
pytest --cov=module_name tests/

# Verbose output
pytest -v
```

## 📝 Code Style

### Python

```python
# Good
def process_event(event_data: dict) -> dict:
    """
    Process an event and return enriched data.
    
    Args:
        event_data: Raw event dictionary
        
    Returns:
        Enriched event dictionary
    """
    result = validate_event(event_data)
    return enrich_data(result)

# Avoid
def process(d):
    return enrich(validate(d))
```

### TypeScript/JavaScript

```typescript
// Good
interface Event {
  id: string;
  type: string;
  timestamp: Date;
}

async function fetchEvents(): Promise<Event[]> {
  const response = await api.get('/events');
  return response.data;
}

// Avoid
function getEvents() {
  return api.get('/events').then(r => r.data);
}
```

## 🐛 Reporting Bugs

### Before Reporting

1. Check existing issues
2. Try to reproduce on latest version
3. Gather relevant information

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 12.0]
- Python version: [e.g., 3.8]
- Module: [e.g., data-ingestion]

## Additional Context
Any other relevant information
```

## 💡 Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why this feature is needed

## Proposed Solution
How you think it should work

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Any other relevant information
```

## 📚 Documentation

### Writing Good Documentation

- Use clear, concise language
- Include code examples
- Add diagrams where helpful
- Keep it up-to-date
- Test all examples

### Documentation Structure

```markdown
# Feature Name

## Overview
Brief description

## Installation
Setup steps

## Usage
Basic usage examples

## API Reference
Detailed API documentation

## Examples
Comprehensive examples

## Troubleshooting
Common issues and solutions
```

## 🔍 Code Review Process

### What We Look For

- **Correctness**: Does it work as intended?
- **Style**: Follows project conventions?
- **Tests**: Adequate test coverage?
- **Documentation**: Well documented?
- **Performance**: Efficient implementation?
- **Security**: No security vulnerabilities?

### Review Timeline

- Initial review within 2-3 days
- Follow-up on requested changes
- Approval and merge

## 🎯 Priority Areas

We especially welcome contributions in:

- 🐛 Bug fixes
- 📝 Documentation improvements
- 🧪 Test coverage
- 🚀 Performance optimizations
- ♿ Accessibility improvements
- 🌐 Internationalization

## 📞 Getting Help

- 💬 Open a discussion on GitHub
- 📧 Check existing documentation
- 🔍 Search closed issues

## 🙏 Thank You!

Your contributions make SmartCitySense better for everyone. We appreciate your time and effort!

---

**Questions?** Feel free to ask in discussions or issues.
