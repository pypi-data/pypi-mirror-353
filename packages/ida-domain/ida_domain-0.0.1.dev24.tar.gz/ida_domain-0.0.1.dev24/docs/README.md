# Documentation Generation with Sphinx

This document outlines the documentation workflow for the **IDA Domain API** using **Sphinx** for generating comprehensive Python API documentation.

---

## Overview

The IDA Domain API documentation is built using **Sphinx**, a powerful documentation generator that creates beautiful, searchable HTML documentation from reStructuredText files and Python docstrings.

## Features

- **Automatic API Documentation**: Sphinx autodoc automatically extracts documentation from Python docstrings
- **Modern Theme**: Uses the Read the Docs theme for a clean, professional appearance
- **Cross-References**: Automatic linking between different parts of the documentation
- **Code Examples**: Comprehensive examples and usage patterns
- **Search Functionality**: Built-in search across all documentation

---

## Documentation Structure

```
docs/
├── conf.py              # Sphinx configuration
├── index.rst            # Main documentation page
├── installation.rst     # Installation guide
├── examples.rst         # Usage examples
├── api/                 # API reference documentation
│   ├── database.rst     # Database class documentation
│   ├── functions.rst    # Functions class documentation
│   ├── basic_blocks.rst # BasicBlocks class documentation
│   └── ...              # Other API modules
├── _static/             # Static files (CSS, images)
│   └── custom.css       # Custom styling
└── _build/              # Generated documentation (HTML)
```

---

## Building Documentation

### Prerequisites

Install Sphinx and required extensions:

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
```

### Generate Documentation

To build the HTML documentation:

```bash
cd docs
make html
```

The generated documentation will be available in `docs/_build/html/index.html`.

### Development Mode

For continuous documentation development, you can use:

```bash
cd docs
make clean && make html
```

This cleans previous builds and generates fresh documentation.

---

## Configuration

The documentation is configured in `docs/conf.py` with the following key settings:

- **Extensions**: autodoc, viewcode, napoleon, intersphinx, sphinx-autodoc-typehints
- **Theme**: sphinx_rtd_theme (Read the Docs theme)
- **Autodoc**: Automatically generates documentation from Python docstrings
- **Napoleon**: Supports Google and NumPy style docstrings
- **Type Hints**: Automatic type hint documentation

---

## Writing Documentation

### API Documentation

API documentation is automatically generated from Python docstrings in the source code. To add or update API documentation:

1. Update docstrings in the Python source files (`ida_domain/*.py`)
2. Rebuild the documentation with `make html`

### Adding New Sections

To add new documentation sections:

1. Create a new `.rst` file in the appropriate directory
2. Add the file to the `toctree` directive in `index.rst` or the relevant parent file
3. Rebuild the documentation

### Adding New Classes/Modules

**Minimal manual work required!** When you add a new module to the `ida_domain` package:

1. Add your new Python class/module to the `ida_domain` package
2. Write proper docstrings in your Python code
3. Add a new section to `docs/api.rst` following the existing pattern:

   ```rst
   Your New Module
   ~~~~~~~~~~~~~~~

   .. automodule:: ida_domain.your_new_module
      :members:
      :undoc-members:
      :show-inheritance:
   ```

4. Run `make html` - Sphinx will automatically generate documentation from your docstrings

This approach ensures the documentation builds reliably without requiring the IDA SDK to be installed.

### Examples and Tutorials

Examples are maintained in `docs/examples.rst`. To add new examples:

1. Add code examples with proper syntax highlighting
2. Include explanatory text
3. Test the examples to ensure they work correctly

---

## Deployment

### Local Preview

After building, open `docs/_build/html/index.html` in your browser to preview the documentation.

### GitHub Pages (if applicable)

The documentation can be deployed to GitHub Pages by:

1. Building the documentation locally
2. Pushing the `_build/html` contents to the `gh-pages` branch
3. Configuring GitHub Pages to serve from the `gh-pages` branch

---

## Maintenance

### Updating Documentation

- **API Changes**: Documentation automatically updates when docstrings are modified
- **Examples**: Update `examples.rst` when adding new features or changing APIs
- **Installation**: Update `installation.rst` when requirements or installation procedures change

### Quality Checks

Before committing documentation changes:

1. Build the documentation and check for warnings
2. Verify all links work correctly
3. Test code examples
4. Review the generated HTML for formatting issues

---

## Troubleshooting

### Common Issues

**Build Errors**:
- Check that all required packages are installed
- Verify Python path configuration in `conf.py`
- Ensure all referenced files exist

**Missing API Documentation**:
- Check that the Python modules are importable
- Verify autodoc configuration in `conf.py`
- Ensure docstrings are properly formatted

**Styling Issues**:
- Check `_static/custom.css` for custom styling
- Verify theme configuration in `conf.py`
- Clear the build cache with `make clean`

---

## Migration from Doxygen

This project has been migrated from Doxygen to Sphinx. The key benefits of this migration include:

- **Native Python Support**: Better integration with Python codebases
- **Modern Appearance**: Clean, responsive design with search functionality
- **Easier Maintenance**: Documentation stays in sync with code through docstrings
- **Better Developer Experience**: Improved IDE integration and help system support

---
