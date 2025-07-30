# FailExtract Documentation

This directory contains the documentation source files for FailExtract. The documentation is built using [Sphinx](https://www.sphinx-doc.org/) and hosted on GitHub Pages.

## 🚀 Quick Start

### First-time Setup
```bash
cd docs
make setup
make serve
```

Then open http://localhost:8000 to view the documentation.

### Daily Development
```bash
# For development with auto-reload
make watch

# Quick build
make html

# Quality check before committing
make quality
```

## 📁 Structure

```
docs/
├── requirements.txt     # Documentation dependencies
├── Makefile            # Build automation
├── README.md           # This file
└── source/             # Documentation source files
    ├── conf.py         # Sphinx configuration
    ├── index.rst       # Main documentation index
    ├── tutorials/      # Step-by-step guides
    ├── how-to/         # Problem-solving guides
    ├── discussions/    # Background and explanations
    ├── reference/      # API documentation
    └── _static/        # Static files (CSS, images)
```

## 🛠️ Building Documentation

### Prerequisites
- Python 3.11+
- pip

### Install Dependencies
```bash
# Option 1: From requirements.txt
pip install -r docs/requirements.txt

# Option 2: From pyproject.toml
pip install .[docs]

# Option 3: Using Makefile
make install-deps
```

### Build Commands

| Command | Description |
|---------|-------------|
| `make setup` | First-time setup (install + build) |
| `make html` | Build HTML documentation |
| `make clean` | Remove build artifacts |
| `make serve` | Serve docs at http://localhost:8000 |
| `make watch` | Auto-rebuild on changes |
| `make quality` | Run quality checks |

### Advanced Commands

| Command | Description |
|---------|-------------|
| `make linkcheck` | Check external links |
| `make doctest` | Test code examples |
| `make coverage` | Documentation coverage |
| `make apidoc` | Generate API docs from source |
| `make production` | Full production build |

## 📝 Writing Documentation

### Documentation Types (Diátaxis)

We follow the [Diátaxis](https://diataxis.fr/) documentation framework:

- **Tutorials** (`tutorials/`): Learning-oriented, step-by-step lessons
- **How-to Guides** (`how-to/`): Problem-oriented, practical instructions  
- **Discussions** (`discussions/`): Understanding-oriented, explanations
- **Reference** (`reference/`): Information-oriented, technical descriptions

### Writing Guidelines

1. **Use clear, concise language**
2. **Include working code examples**
3. **Test all code examples**
4. **Link between related sections**
5. **Keep content up-to-date with code**

### reStructuredText vs Markdown

- **RST files** (`.rst`): Full Sphinx features, cross-references, autodoc
- **Markdown files** (`.md`): Simple formatting, use for discussions

### Code Examples

Always test code examples:

```python
# Good: Working example
from failextract import extract_on_failure

@extract_on_failure
def test_example():
    assert 1 == 2, "This will be captured"

# Bad: Hypothetical example that doesn't work
@magical_decorator
def test_fantasy():
    assert impossible_thing()
```

## 🔧 Development Workflow

### 1. Local Development
```bash
cd docs
make watch  # Auto-rebuild on changes
# Edit files in source/
# View changes at http://localhost:8000
```

### 2. Quality Check
```bash
make quality  # Run linkcheck + doctest
```

### 3. Commit and Push
The GitHub Actions workflow will:
- Build documentation on PR/push
- Deploy to GitHub Pages on main branch
- Cache dependencies for faster builds

## 🌐 Deployment

Documentation is automatically deployed via GitHub Actions:

### Triggers
- **Push to main**: Deploy to GitHub Pages
- **Pull requests**: Build and check (no deploy)
- **Releases**: Deploy to GitHub Pages

### Manual Deployment
```bash
make production  # Full production build
# Upload docs/build/html/ to your hosting
```

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
# Install the package in development mode
pip install -e .
```

**"sphinx-build not found"**
```bash
pip install -r docs/requirements.txt
```

**"Permission denied" when serving**
```bash
# Try a different port
cd docs/build/html && python -m http.server 8080
```

**Broken links**
```bash
make linkcheck
# Check docs/build/linkcheck/output.txt
```

### Build Cache Issues
```bash
make clean  # Remove build artifacts
make html   # Fresh build
```

## 📚 Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [MyST Markdown Guide](https://myst-parser.readthedocs.io/)
- [Diátaxis Framework](https://diataxis.fr/)

## 🤝 Contributing

1. **Follow the Diátaxis structure**
2. **Test all code examples**
3. **Run quality checks**: `make quality`
4. **Keep dependencies minimal**
5. **Update this README when adding new workflows**

Happy documenting! 📖