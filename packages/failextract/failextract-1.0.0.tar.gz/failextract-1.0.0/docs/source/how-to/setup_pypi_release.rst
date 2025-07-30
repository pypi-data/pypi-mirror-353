How to Set Up Automated PyPI Releases
=====================================

**Task**: Configure automated package publishing to PyPI

This guide helps you set up automated PyPI package releases for FailExtract using GitHub Actions. The setup follows progressive enhancement principles with minimal configuration and security best practices.

Prerequisites
-------------

- GitHub repository with FailExtract source code
- Repository admin access for secrets configuration
- PyPI account with API token
- Basic familiarity with GitHub Actions and Python packaging

Overview
--------

The PyPI release workflow follows the same progressive enhancement approach as documentation:

1. **Start Simple**: Package build and upload only
2. **Release-Triggered**: Automatic on GitHub release publication
3. **Single Purpose**: Each workflow does one thing well
4. **Foundation**: Provides base for future CI/CD enhancements

PyPI Release Workflow
--------------------

The PyPI workflow builds and publishes packages automatically when GitHub releases are published.

**Trigger**: GitHub release publication
**Output**: Package available on PyPI via ``pip install failextract``

PyPI Token Setup
---------------

**Create PyPI API Token**:

1. Go to https://pypi.org/manage/account/
2. Navigate to "API tokens" section
3. Click "Add API token"
4. Name: "FailExtract GitHub Actions"
5. Scope: "Entire account" (or project-specific if preferred)
6. Copy the generated token (starts with ``pypi-``)

**Add to GitHub Secrets**:

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: ``PYPI_API_TOKEN``
4. Value: Paste the PyPI token
5. Click "Add secret"

⚠️ **Security Note**: The token is sensitive and should never be exposed in logs or code.

GitHub Actions Configuration
----------------------------

Create the workflow file:

.. code-block:: yaml

   # .github/workflows/pypi-release.yml
   name: PyPI Release

   on:
     release:
       types: [published]

   jobs:
     build-and-publish:
       runs-on: ubuntu-latest
       
       steps:
       - name: Checkout repository
         uses: actions/checkout@v4
         
       - name: Set up Python
         uses: actions/setup-python@v4
         with:
           python-version: '3.11'
           
       - name: Install build tools
         run: |
           python -m pip install --upgrade pip
           pip install build twine
           
       - name: Validate version consistency
         run: |
           # Extract version from git tag (remove 'v' prefix if present)
           GIT_TAG=${GITHUB_REF#refs/tags/}
           GIT_VERSION=${GIT_TAG#v}
           
           # Extract version from pyproject.toml
           PYPROJECT_VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
           
           echo "Git tag version: $GIT_VERSION"
           echo "pyproject.toml version: $PYPROJECT_VERSION"
           
           if [ "$GIT_VERSION" != "$PYPROJECT_VERSION" ]; then
             echo "Version mismatch: git tag ($GIT_VERSION) != pyproject.toml ($PYPROJECT_VERSION)"
             exit 1
           fi
           
           echo "Version validation passed: $GIT_VERSION"
           
       - name: Build package
         run: |
           python -m build
           
       - name: Validate package
         run: |
           # Check that the package can be built and contains expected files
           python -m twine check dist/*
           
           # List built artifacts
           echo "Built artifacts:"
           ls -la dist/
           
           # Verify wheel can be installed and imported
           pip install dist/*.whl
           python -c "import failextract; print(f'FailExtract version: {failextract.__version__}')"
           
       - name: Publish to PyPI
         env:
           TWINE_USERNAME: __token__
           TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
         run: |
           python -m twine upload dist/*

**Key Design Decisions**:

- **Python 3.11**: Stable version for build consistency
- **Industry Standard Tools**: ``build`` + ``twine`` for reliability
- **Version Validation**: Ensures git tag matches ``pyproject.toml``
- **Package Validation**: Multiple checks before upload
- **Secure Token Handling**: Uses GitHub secrets

Package Configuration
--------------------

Ensure ``pyproject.toml`` is properly configured:

.. code-block:: toml

   [project]
   name = "failextract"
   version = "1.0.0"  # Must match git tag
   description = "Test failure extraction and reporting library"
   # ... other project metadata
   
   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"

**Critical Requirements**:

- Version in ``pyproject.toml`` must exactly match git tag
- All required metadata fields must be present
- Package structure must be valid

Testing the Workflow
--------------------

**Local Testing**:

Before creating a release, test package building locally:

.. code-block:: bash

   # Install build tools
   pip install build twine
   
   # Build package
   python -m build
   
   # Validate package
   python -m twine check dist/*
   
   # Test installation
   pip install dist/*.whl
   python -c "import failextract; print('Success!')"

**Test Workflow** (optional):

For safer testing, use the test workflow:

.. code-block:: yaml

   # .github/workflows/test-pypi-release.yml
   name: Test PyPI Release
   
   on:
     workflow_dispatch:  # Manual trigger
     
   jobs:
     test-build-and-publish:
       # Same steps as main workflow but without PyPI upload

**Live Release Testing**:

1. Create version tag: ``git tag v1.0.0``
2. Push tag: ``git push origin v1.0.0``
3. Create GitHub release from the tag
4. Monitor workflow execution in Actions tab
5. Verify package appears on PyPI

Release Process
--------------

**Standard Release Workflow**:

1. **Update Version**: Modify ``version`` in ``pyproject.toml``
2. **Commit Changes**: ``git commit -am "Release v1.0.0"``
3. **Create Tag**: ``git tag v1.0.0``
4. **Push Changes**: ``git push && git push --tags``
5. **Create Release**: Use GitHub web interface to create release from tag
6. **Monitor Workflow**: Check Actions tab for successful execution
7. **Verify Publication**: Confirm package is available on PyPI

**Version Validation**:

The workflow automatically validates that:

- Git tag version matches ``pyproject.toml`` version
- Package builds successfully
- Package passes Twine validation
- Package can be imported after installation

Expected Workflow Output
------------------------

**Successful Build**:

.. code-block:: text

   * Creating isolated environment: venv+pip...
   * Installing packages in isolated environment:
     - hatchling
   * Building sdist...
   * Building wheel from sdist
   Successfully built failextract-1.0.0.tar.gz and failextract-1.0.0-py3-none-any.whl

**Package Validation**:

.. code-block:: text

   Checking dist/failextract-1.0.0-py3-none-any.whl: PASSED
   Checking dist/failextract-1.0.0.tar.gz: PASSED

**PyPI Upload**:

.. code-block:: text

   Uploading distributions to https://upload.pypi.org/legacy/
   Uploading failextract-1.0.0-py3-none-any.whl
   Uploading failextract-1.0.0.tar.gz

Troubleshooting
---------------

**Version Mismatch Errors**:

.. code-block:: text

   Version mismatch: git tag (1.0.1) != pyproject.toml (1.0.0)

**Solution**: Update ``pyproject.toml`` version to match git tag or create new tag.

**Build Failures**:

- Check ``pyproject.toml`` syntax and configuration
- Verify all required files are included
- Test build locally before release

**Upload Failures**:

- Verify PyPI token is correctly set in GitHub secrets
- Check for version conflicts (version already exists on PyPI)
- Ensure package metadata is complete

**Import Failures**:

- Check package structure and ``__init__.py`` files
- Verify dependencies are correctly specified
- Test installation in clean environment

Common Issues
-------------

**Token Authentication**:

.. code-block:: text

   403 Client Error: Invalid or non-existent authentication information

**Solution**: 
- Verify ``PYPI_API_TOKEN`` secret is set correctly
- Ensure token has sufficient permissions
- Check token hasn't expired

**Version Already Exists**:

.. code-block:: text

   400 Client Error: File already exists

**Solution**: 
- PyPI doesn't allow overwriting existing versions
- Create new version tag and update ``pyproject.toml``
- Use pre-release versions for testing (e.g., ``1.0.0rc1``)

Monitoring and Maintenance
--------------------------

**Regular Checks**:

- Monitor workflow execution on each release
- Verify packages install correctly: ``pip install failextract``
- Check PyPI project page for correct metadata
- Review download statistics and user feedback

**Token Management**:

- Rotate PyPI tokens periodically
- Use project-scoped tokens when possible
- Monitor token usage in PyPI account settings

**Dependency Updates**:

Update workflow dependencies periodically:

.. code-block:: yaml

   # Update action versions
   uses: actions/checkout@v4        # → v5 when available
   uses: actions/setup-python@v4    # → v5 when available

Future Enhancements
-------------------

Following progressive enhancement, consider adding:

**Pre-release Testing**:

.. code-block:: yaml

   - name: Run tests before release
     run: pytest tests/

**Multi-Python Testing**:

.. code-block:: yaml

   strategy:
     matrix:
       python-version: ['3.11', '3.12', '3.13']

**TestPyPI Integration**:

.. code-block:: yaml

   - name: Upload to TestPyPI first
     run: python -m twine upload --repository testpypi dist/*

Security Best Practices
-----------------------

**Token Management**:

- Use project-scoped tokens when possible
- Rotate tokens regularly (every 6-12 months)
- Monitor token usage in PyPI account settings
- Never commit tokens to version control

**Workflow Security**:

- Pin action versions for reproducibility
- Use official GitHub actions when possible
- Review third-party action permissions
- Monitor workflow logs for sensitive information exposure

**Release Security**:

- Validate all packages before upload
- Use signed commits for release tags
- Require pull request reviews for version changes
- Monitor PyPI package for unauthorized changes

Success Checklist
------------------

| ✅ PyPI API token created and added to GitHub secrets
| ✅ Workflow file created in ``.github/workflows/pypi-release.yml``
| ✅ ``pyproject.toml`` properly configured with version
| ✅ Local package build tested successfully
| ✅ First release triggers workflow execution
| ✅ Package successfully uploaded to PyPI
| ✅ Package can be installed via ``pip install failextract``
| ✅ Installed package imports and functions correctly

**Next Steps**: Monitor release process and consider progressive enhancements like automated testing or multi-environment validation.