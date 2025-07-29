# IDA Domain


This project provides a **Domain Model** for IDA, allowing interaction with IDA SDK components via Python.

## 🚀 Features

- Exposes a Domain Model on top of IDA SDK functions to Python
- Pure Python implementation - no C++ compilation required
- Easy installation via pip

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.TXT) file for details.

## ⚙️ Installation

### (Optional) Using UV

Install from https://docs.astral.sh/uv/getting-started/installation/
```bash
git clone git@github.com:HexRaysSA/ida-api-domain.git
cd ida-api-domain
uv sync
uv build
# Documentation building using uv
cd docs && make
# Publish packaged (not yet implemented)
uv publish
```

### Prerequisites

Set the `IDADIR` environment variable to point to your IDA installation directory:

```bash
export IDADIR="[IDA Installation Directory]"
```

**Example:**
```bash
export IDADIR="/Applications/IDA Professional 9.1.app/Contents/MacOS/"
```

> **Note:** If you have already installed and configured the `idapro` Python package, setting `IDADIR` is not required.

### Install from PyPI (Recommended)

```bash
pip install ida-domain
```

### Install from Source

```bash
git clone git@github.com:HexRaysSA/ida-api-domain.git
cd ida-api-domain
pip install .
```

### Development Installation

For development, install in editable mode:

```bash
git clone git@github.com:HexRaysSA/ida-api-domain.git
cd ida-api-domain
pip install -e .
```

## 🧪 Testing

Run the test suite using pytest:

```bash
pytest tests/
```

## 📚 Documentation

The IDA Domain API documentation is built with Sphinx and includes:

- **API Reference**: Complete documentation of all classes and methods
- **Installation Guide**: Step-by-step setup instructions
- **Examples**: Practical usage examples for common tasks
- **Getting Started**: Quick start guide for new users

### Building Documentation Locally

To build the documentation locally:

```bash
cd docs
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
make html
```

The generated documentation will be available at `docs/_build/html/index.html`.

### Online Documentation

The latest documentation is available at: https://hexrayssa.github.io/ida-api-domain/

## 📝 Examples

Check the `examples/` directory for usage examples:

```bash
python examples/traverse.py
```

## 🛠️ Development

### Prerequisites for Development

- Python 3.7+
- pytest for testing

### Running Tests

```bash
pip install pytest
pytest tests/
```

### Project Structure

```
ida-api-domain/
├── ida_domain/          # Main Python package
├── examples/            # Usage examples
├── tests/              # Test suite
├── docs/               # Documentation
└── setup.py           # Package configuration
