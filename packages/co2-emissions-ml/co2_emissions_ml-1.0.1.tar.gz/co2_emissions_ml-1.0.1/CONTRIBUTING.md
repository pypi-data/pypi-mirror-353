# Contributing to CO₂ Emissions Prediction

Thank you for your interest in contributing! We welcome improvements, bug fixes, and new features.

## How to contribute

1. **Fork** the repository.
2. **Clone** your fork:

```bash
   git clone https://github.com/Shashvat-Jain/CO2-predictions-using-Automotive-Features.git
```

3. **Create a branch** for your feature or bugfix:

```bash
git checkout -b feature/my-new-feature
```

4. **Install dependencies** in a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Make your changes**, and add tests in src/ if appropriate.

6. **Run tests** (if available) and ensure notebooks still execute:

```bash
pytest
```

7. **Commit** your changes with a clear message:

```bash
git add .
git commit -m "Add feature X to preprocessing pipeline"
```

8. **Push** to your fork:

```bash
git push origin feature/my-new-feature
```

9. **Open a Pull Request** against the main branch.

## Code style

- Follow PEP8 for Python code.

- Keep notebook outputs cleared before committing.

## Reporting issues

Please open an issue in the repository with a descriptive title and steps to reproduce.
