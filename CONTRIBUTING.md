# Contributing to RelayZero

Thank you for contributing to RelayZero. RelayZero is an open-source project created for Hack Apertus 2026.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/abhijeetnardele24-hash/relayzero.git
   cd relayzero
   ```
2. Set up Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows
   pip install -r track_2b/src/backend/requirements.txt
   ```
3. Run test suite:
   ```bash
   pytest track_2b/src/backend/tests -v
   ```
4. Build frontend:
   ```bash
   cd track_2b/src/frontend
   npm install
   npm run build
   ```

## Commit Guidelines
- Use descriptive commit messages.
- Never commit secrets, tokens, or large model weights.
- Ensure all tests pass before opening pull requests.
