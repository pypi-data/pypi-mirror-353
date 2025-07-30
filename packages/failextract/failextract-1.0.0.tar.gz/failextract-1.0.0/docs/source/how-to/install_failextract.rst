How to Install FailExtract
==========================

**Task**: Get FailExtract installed and verify it works

This guide shows you exactly how to install FailExtract for different scenarios, with honest information about what's actually available.

Quick Installation (Most Users)
--------------------------------

Install FailExtract with the most commonly needed features:

.. code-block:: bash

   pip install failextract

This gives you:

- Core failure extraction with ``@extract_on_failure`` decorator  
- JSON, Markdown, XML, and CSV output formatters
- Basic CLI commands
- Zero required dependencies beyond Python standard library

**Verify the installation:**

.. code-block:: python

   import failextract
   print(failextract.__version__)

You should see a version number without any errors.

Adding Optional Features
------------------------

FailExtract follows a progressive enhancement model. Add features only when you need them:

**YAML Output Support**

.. code-block:: bash

   pip install failextract[formatters]

This adds YAML output format support (requires ``pyyaml``).

**Enhanced Configuration**

.. code-block:: bash

   pip install failextract[config]

This adds TOML configuration file support (requires ``tomli`` for Python < 3.11).

**Rich CLI Interface**

.. code-block:: bash

   pip install failextract[cli]

This adds enhanced terminal output with colors and formatting (requires ``rich`` and ``typer``).

**All Optional Features**

.. code-block:: bash

   pip install failextract[formatters,config,cli]

Environment-Specific Installation
----------------------------------

**Production/CI Environments**

.. code-block:: bash

   # Minimal installation for production monitoring
   pip install failextract
   
   # Verify no extra dependencies
   pip list | grep -E "(yaml|rich|typer|tomli)"

**Development Environments**

.. code-block:: bash

   # Install with commonly used optional features
   pip install failextract[formatters,cli]

**Documentation/Reporting Environments**

.. code-block:: bash

   # Install with all output formatters
   pip install failextract[formatters]

Installation Verification
--------------------------

**Test Core Functionality**

Create a test file to verify installation:

.. code-block:: python

   # test_installation.py
   from failextract import extract_on_failure, FailureExtractor, OutputConfig

   @extract_on_failure
   def test_basic():
       assert False, "Installation test failure"

   if __name__ == "__main__":
       try:
           test_basic()
       except AssertionError:
           pass
       
       extractor = FailureExtractor()
       print(f"Captured {len(extractor.failures)} failures")
       
       if extractor.failures:
           config = OutputConfig("test.json")
           extractor.save_report(config)
           print("✓ JSON output works")
           
           config = OutputConfig("test.md", format="markdown")
           extractor.save_report(config)
           print("✓ Markdown output works")
           
           print("✅ FailExtract installation verified!")

Run the test:

.. code-block:: bash

   python test_installation.py

**Test Optional Features**

If you installed optional features, test them:

.. code-block:: python

   # test_optional_features.py
   from failextract import FailureExtractor, OutputConfig

   def test_yaml_support():
       """Test YAML formatter if available."""
       try:
           extractor = FailureExtractor()
           config = OutputConfig("test.yaml", format="yaml")
           extractor.save_report(config)
           print("✓ YAML formatter available")
           return True
       except Exception as e:
           print(f"✗ YAML formatter not available: {e}")
           return False

   def test_cli_support():
       """Test rich CLI features if available."""
       try:
           import rich
           print("✓ Rich CLI features available")
           return True
       except ImportError:
           print("✗ Rich CLI features not available")
           return False

   if __name__ == "__main__":
       print("Testing optional features:")
       test_yaml_support()
       test_cli_support()

Python Version Requirements
----------------------------

**Minimum Requirements**

- Python 3.11 or later
- No other required dependencies for core functionality

**Recommended Setup**

- Python 3.11 or later for best performance
- pip 20.0 or later for reliable dependency resolution

**Check Your Python Version**

.. code-block:: bash

   python --version
   pip --version

Upgrading FailExtract
---------------------

**Standard Upgrade**

.. code-block:: bash

   pip install --upgrade failextract

**Upgrade with Features**

.. code-block:: bash

   # Upgrade and ensure optional features are installed
   pip install --upgrade failextract[formatters,cli]

**Clean Reinstall**

If you encounter issues:

.. code-block:: bash

   pip uninstall failextract
   pip install failextract

Development Installation
------------------------

**For Contributing to FailExtract**

.. code-block:: bash

   git clone https://github.com/your-repo/failextract.git
   cd failextract
   pip install -e ".[formatters,config,cli,dev]"

**For Customizing FailExtract**

.. code-block:: bash

   # Install in editable mode
   pip install -e .

This allows you to modify the source code and see changes immediately.

Troubleshooting Installation
----------------------------

**Import Errors**

.. code-block:: python

   # Check if FailExtract is properly installed
   try:
       import failextract
       print("✓ FailExtract is available")
   except ImportError as e:
       print(f"✗ FailExtract not found: {e}")

**Dependency Conflicts**

.. code-block:: bash

   # Check for conflicting packages
   pip check
   
   # Show FailExtract dependencies
   pip show failextract

**Permission Issues**

.. code-block:: bash

   # Install for current user only
   pip install --user failextract
   
   # Or use virtual environment (recommended)
   python -m venv failextract_env
   source failextract_env/bin/activate  # Linux/Mac
   # failextract_env\\Scripts\\activate  # Windows
   pip install failextract

**Version Conflicts**

.. code-block:: bash

   # Check installed version
   python -c "import failextract; print(failextract.__version__)"
   
   # Force reinstall
   pip install --force-reinstall failextract

Installation in Different Environments
---------------------------------------

**Virtual Environments (Recommended)**

.. code-block:: bash

   # Create and activate virtual environment
   python -m venv myproject_env
   source myproject_env/bin/activate  # Linux/Mac
   # myproject_env\\Scripts\\activate  # Windows
   
   # Install FailExtract
   pip install failextract[formatters]

**Docker Containers**

.. code-block:: dockerfile

   FROM python:3.9-slim
   
   # Install FailExtract
   RUN pip install failextract[formatters]
   
   # Verify installation
   RUN python -c "import failextract; print('FailExtract ready')"

**GitHub Actions**

.. code-block:: yaml

   - name: Install FailExtract
     run: |
       pip install failextract[formatters]
       python -c "import failextract; print('Installed:', failextract.__version__)"

What's NOT Available
--------------------

**To set proper expectations, FailExtract does NOT currently include:**

- No HTML output formatter (use Markdown instead)
- Database storage capabilities  
- IDE integration plugins
- Chat platform integrations (Slack, Teams, etc.)
- Automated CI/CD integrations beyond CLI usage

**Note**: The codebase includes an advanced analytics system and dependency graph analysis, but these may require additional configuration or optional dependencies.

Next Steps
----------

After successful installation:

1. **Start Learning**: :doc:`../tutorials/getting_started` - Your first failure extraction
2. **Explore Formats**: :doc:`../tutorials/multiple_formats` - Different output formats  
3. **Configure Behavior**: :doc:`../tutorials/configuration` - Customize FailExtract
4. **Integrate with pytest**: :doc:`../tutorials/pytest_integration` - Automatic test suite integration

Success Checklist
------------------

| ✅ Python 3.8+ installed and verified  
| ✅ FailExtract installed with ``pip install failextract``  
| ✅ Import test successful: ``import failextract``  
| ✅ Basic functionality verified with test script  
| ✅ Optional features installed if needed  
| ✅ Ready to start using FailExtract!  

**Installation complete - you're ready to start extracting failure data!**