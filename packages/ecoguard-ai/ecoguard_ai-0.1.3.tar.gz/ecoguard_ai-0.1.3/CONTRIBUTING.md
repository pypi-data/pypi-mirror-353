# Contributing to EcoGuard AI

We welcome contributions from the community! EcoGuard AI aims to become the sentient core for future-proof software pipelines, and we need your help to make this vision a reality.

## 🎯 Project Vision

EcoGuard AI is a transformative, AI-augmented software development pipeline solution designed to proactively champion excellence across the entire software lifecycle. We serve as a unified intelligence layer, analyzing both human-written and AI-generated code for quality, security, and environmental sustainability.

## 🚀 How to Contribute

### 1. Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/ecoguard-ai.git
   cd ecoguard-ai
   ```
3. **Set up the development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```
4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

### 2. Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes** following our coding standards
3. **Run tests**:
   ```bash
   pytest
   ```
4. **Run linting and formatting**:
   ```bash
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   ```
5. **Commit your changes**:
   ```bash
   git commit -m "feat: add your feature description"
   ```
6. **Push and create a Pull Request**

### 3. Coding Standards

- **Python Code Style**: We use Black for formatting (line length: 88)
- **Type Hints**: All new code should include proper type hints
- **Documentation**: All public functions and classes should have docstrings
- **Testing**: New features should include comprehensive tests
- **Security**: Follow secure coding practices, especially for AI-generated code analysis

### 4. Commit Message Convention

We follow the Conventional Commits specification:

- `feat:` A new feature
- `fix:` A bug fix
- `docs:` Documentation only changes
- `style:` Changes that do not affect the meaning of the code
- `refactor:` A code change that neither fixes a bug nor adds a feature
- `perf:` A code change that improves performance
- `test:` Adding missing tests or correcting existing tests
- `chore:` Changes to the build process or auxiliary tools

## 🏗️ Architecture Overview

EcoGuard AI is built with a modular architecture:

```
src/ecoguard_ai/
├── core/           # Core analysis engine
├── analyzers/      # Pluggable analysis modules
│   ├── quality/    # Code quality rules
│   ├── security/   # Security analysis (SAST)
│   ├── green/      # Green software patterns
│   └── ai_code/    # AI-specific analysis
├── reporting/      # Output and reporting
├── cli/           # Command-line interface
├── server/        # Centralized server components
└── utils/         # Utility functions
```

## 🔍 What We're Looking For

### High Priority Areas

1. **AST Analysis Rules**: New rules for detecting inefficient patterns
2. **Green Software Patterns**: Rules that identify carbon-intensive code patterns
3. **AI Code Analysis**: Patterns specific to AI-generated code inefficiencies
4. **Security Rules**: SAST rules targeting modern security vulnerabilities
5. **Documentation**: User guides, API documentation, and examples

### Current Development Focus (Phase 1)

We're currently working on:
- Foundation & Research (Stages 1-10)
- Core AST analysis engine
- Basic rule implementations
- CLI interface development

## 🧪 Testing

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test module interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Ensure analysis doesn't significantly slow down development

Run tests with:
```bash
pytest                    # All tests
pytest tests/unit/       # Unit tests only
pytest tests/integration/ # Integration tests only
pytest --cov=src/        # With coverage
```

## 📝 Documentation

We use Sphinx for documentation. To build docs locally:

```bash
cd docs/
make html
```

Documentation should include:
- Clear examples of usage
- API reference
- Rule explanations with examples
- Integration guides

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear description** of the issue
2. **Steps to reproduce** the problem
3. **Expected vs actual behavior**
4. **Environment details** (OS, Python version, EcoGuard AI version)
5. **Sample code** that demonstrates the issue (if applicable)

## 💡 Feature Requests

For feature requests:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** and why it's valuable
3. **Provide examples** of how the feature would work
4. **Consider implementation** complexity and maintainability

## 🌱 Green Software Principles

As a project focused on sustainable software development, we practice what we preach:

- **Efficient Code**: Write performant, resource-conscious code
- **Minimal Dependencies**: Avoid unnecessary dependencies
- **Caching**: Implement intelligent caching to reduce computational overhead
- **Profiling**: Regular performance profiling of our own codebase

## 🤝 Community Guidelines

- **Be respectful** and inclusive
- **Provide constructive feedback**
- **Help others** learn and contribute
- **Follow the code of conduct**
- **Stay focused** on the project's mission

## 🎖️ Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Project documentation
- Community showcases

## 📞 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community discussions
- **Documentation**: Check our comprehensive docs first
- **Code Examples**: See the `examples/` directory

## 🗺️ Roadmap Participation

We follow a detailed 50-stage development roadmap. Contributors can:

- **Review the roadmap** in our README
- **Pick up specific stages** or tasks
- **Propose modifications** to the roadmap based on insights
- **Lead entire phases** for major contributions

Thank you for contributing to EcoGuard AI! Together, we're building a sustainable future, one line of code at a time. 🌱
