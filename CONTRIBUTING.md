# Contributing to Fluxerpy3

Thank you for your interest in contributing to Fluxerpy3! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/fluxerpy.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/macOS: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Install development dependencies: `pip install -r tests/requirements.txt`

## Development Setup

Install the package in development mode:

```bash
pip install -e .
```

## Running Tests

Run the test suite with pytest:

```bash
pytest tests/ -v
```

Run tests with coverage:

```bash
pytest tests/ --cov=fluxerpy3 --cov-report=html
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and concise

## Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and write tests

3. Run the test suite to ensure everything passes

4. Commit your changes with a clear commit message:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Include tests for new features
- Ensure all tests pass
- Update documentation as needed
- Keep commits focused and atomic

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect different viewpoints and experiences

## Questions?

If you have questions, feel free to:
- Open an issue for discussion
- Reach out to the maintainers

Thank you for contributing to Fluxerpy3! 🚀
