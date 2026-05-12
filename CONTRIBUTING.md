# Contributing to Pricy Price Tracker

First off, thank you for considering contributing to Pricy Price Tracker. It is people like you that make this project a great tool for the community.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to see if the problem has already been reported. When you are creating a bug report, please include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed and what behavior you expected
- Include screenshots if applicable
- Specify your environment (OS, Python version, Node version, browser)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- A clear and descriptive title
- A detailed description of the proposed functionality
- Explain why this enhancement would be useful
- List some examples of how it would be used

### Pull Requests

1. Fork the repository
2. Create a new branch from `main` (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the tests and ensure they pass
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn
- Git

### Backend Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run database migrations
python -c "from backend.app.database import init_db; init_db()"

# Start development server
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Running Tests

```bash
# Backend tests
python -m pytest backend/tests -v

# Frontend lint
cd frontend && npm run lint
```

## Styleguides

### Git Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding or correcting tests
- `chore`: Changes to the build process or auxiliary tools

Example: `feat: add email notification system`

### Python Styleguide

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type annotations on all function signatures
- Use descriptive variable names
- Keep functions focused and under 50 lines when possible
- Use docstrings for all public functions and classes

### React/JavaScript Styleguide

- Use functional components with hooks
- Use descriptive component names
- Keep components focused and under 300 lines when possible
- Use PropTypes or TypeScript for type checking
- Follow the existing code style in the project

## Community

- Join discussions in GitHub Issues
- Help answer questions from other contributors
- Share the project with others who might find it useful

## Recognition

Contributors will be recognized in our release notes and README. Thank you for helping make this project better.
