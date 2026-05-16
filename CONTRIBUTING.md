# Contributing to flask-request-validate

Thank you for your interest in contributing to flask-request-validate! We welcome contributions from the community, whether it's bug reports, feature requests, documentation improvements, or code contributions.

## Getting Started

### Setting Up Your Development Environment

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd flask-request-validate
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the project in development mode with dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

   If `dev` extras are not defined, install with:
   ```bash
   pip install -e .
   pip install pytest pytest-cov
   ```

## Development Workflow

### Running Tests

Execute the test suite to ensure your changes don't break existing functionality:

```bash
pytest
```

For test coverage reports:
```bash
pytest --cov=src/flask_request_validate
```

### Running Individual Tests

To run a specific test file:
```bash
pytest tests/test_validate.py
```

To run a specific test function:
```bash
pytest tests/test_validate.py::test_function_name
```

## Code Style and Quality

- **Code Style:** Follow [PEP 8](https://pep8.org/) guidelines
- **Type Hints:** Consider adding type hints for better code clarity
- **Documentation:** Add docstrings to functions and classes using standard Python conventions
- **Imports:** Keep imports organized and remove unused ones

## Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   # or for bug fixes:
   git checkout -b fix/your-bug-fix-name
   ```

2. **Make your changes** and commit with clear, descriptive messages:
   ```bash
   git commit -m "Add descriptive commit message"
   ```

3. **Ensure tests pass:**
   ```bash
   pytest
   ```

4. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Submitting Contributions

### Pull Request Process

1. **Create a Pull Request** against the main branch with a clear title and description
2. **Include the following in your PR description:**
   - What problem does this solve or what feature does it add?
   - How have you tested the changes?
   - Any breaking changes or migration notes?
3. **Ensure all tests pass** in the CI/CD pipeline
4. **Address any review feedback** promptly

### Before Submitting

- [ ] All tests pass locally
- [ ] Code follows PEP 8 style guidelines
- [ ] Docstrings are added/updated for new functions
- [ ] Changes are documented in relevant markdown files
- [ ] No debugging code or print statements are left in the code

## Reporting Issues

When reporting bugs, please include:

- **Description:** Clear description of the issue
- **Steps to Reproduce:** Detailed steps to reproduce the problem
- **Expected Behavior:** What should happen
- **Actual Behavior:** What actually happens
- **Environment:** Python version, flask-request-validate version, Flask version
- **Code Sample:** Minimal code example that demonstrates the issue

## Documentation

Documentation improvements are always welcome! Documentation is located in the `docs/` folder and uses Markdown format.

When adding new features or changing behavior:
- Update relevant documentation files
- Add examples in the `examples/` folder if appropriate
- Update the API reference if your changes affect the public API

## Project Structure

Understanding the project structure can help when making contributions:

```
flask-request-validate/
├── src/flask_request_validate/      # Main package code
│   ├── __init__.py
│   ├── validator.py         # Core validation logic
│   ├── decorators.py        # Flask decorators
│   ├── rules.py             # Validation rules
│   ├── patterns.py          # Validation patterns
│   ├── errors.py            # Error definitions
│   └── audit_security.py    # Security auditing
├── tests/                   # Test suite
├── docs/                    # Documentation
├── examples/                # Usage examples
└── pyproject.toml          # Project configuration
```

## Questions?

If you have questions about contributing, feel free to:
- Open a GitHub issue with your question
- Check existing documentation in the `docs/` folder
- Review existing examples in the `examples/` folder

## License

By contributing to flask-request-validate, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

Thank you for contributing to flask-request-validate!
