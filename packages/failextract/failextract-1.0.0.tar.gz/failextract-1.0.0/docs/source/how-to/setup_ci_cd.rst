How to Set Up CI/CD for Documentation
=====================================

**Task**: Configure automated documentation builds and deployment

This guide helps you set up automated documentation builds for FailExtract using GitHub Actions and GitHub Pages. The setup is designed to be minimal, focused, and follows progressive enhancement principles.

Prerequisites
-------------

- GitHub repository with FailExtract documentation
- Repository admin access for GitHub Pages configuration
- Basic familiarity with GitHub Actions

Overview
--------

FailExtract's CI/CD approach follows progressive enhancement:

1. **Start Simple**: Documentation builds only
2. **Release-Triggered**: Avoids noise from development commits
3. **Single Purpose**: Each workflow does one thing well
4. **Foundation**: Provides base for future enhancements

Documentation Workflow
----------------------

The documentation workflow builds and deploys documentation automatically when releases are published.

**Trigger**: GitHub release publication
**Output**: Live documentation site on GitHub Pages

GitHub Actions Configuration
----------------------------

Create the workflow file:

.. code-block:: yaml

   # .github/workflows/docs.yml
   name: Documentation

   on:
     release:
       types: [published]

   jobs:
     build-and-deploy:
       runs-on: ubuntu-latest
       
       steps:
       - name: Checkout repository
         uses: actions/checkout@v4
         
       - name: Set up Python
         uses: actions/setup-python@v4
         with:
           python-version: '3.11'
           
       - name: Install dependencies
         run: |
           python -m pip install --upgrade pip
           pip install sphinx sphinx-rtd-theme myst-parser
           
       - name: Build documentation
         run: |
           cd docs
           make html
           
       - name: Deploy to GitHub Pages
         uses: peaceiris/actions-gh-pages@v3
         with:
           github_token: ${{ secrets.GITHUB_TOKEN }}
           publish_dir: ./docs/build/html

**Key Design Decisions**:

- **Python 3.11**: Stable, modern version for build consistency
- **Minimal Dependencies**: Only essential packages for documentation
- **Existing Makefile**: Leverages proven build system
- **No Custom Domain**: Uses default GitHub Pages domain for simplicity

Repository Configuration
------------------------

**Enable GitHub Pages**:

1. Go to repository Settings → Pages
2. Source: "Deploy from a branch"
3. Branch: "gh-pages" (created automatically by workflow)
4. Folder: "/ (root)"

**Verify Permissions**:

The workflow uses ``GITHUB_TOKEN`` (automatically provided) for deployment. No additional secrets needed.

Testing the Workflow
--------------------

**Local Testing**:

Before creating a release, test documentation builds locally:

.. code-block:: bash

   cd docs
   make html
   
   # Check for build errors
   # Verify HTML output in build/html/

**Workflow Testing**:

1. Create a git tag: ``git tag v0.1.0``
2. Push tag: ``git push origin v0.1.0``
3. Create GitHub release from the tag
4. Monitor workflow execution in Actions tab
5. Verify deployment to GitHub Pages

Expected Workflow Output
------------------------

**Successful Build**:

.. code-block:: text

   Running Sphinx v8.2.3
   building [html]: targets for 25 source files
   build succeeded, X warnings.
   The HTML pages are in build/html.

**Deployment Confirmation**:

.. code-block:: text

   [INFO] Deploy to gh-pages branch
   [INFO] workDir: /github/workspace
   [INFO] Deployment successful

**Live Site**: Documentation available at ``https://username.github.io/failextract/``

Troubleshooting
---------------

**Build Failures**:

- Check Python version compatibility
- Verify all dependencies are installed
- Review Sphinx configuration for errors
- Test local build before release

**Deployment Issues**:

- Ensure GitHub Pages is enabled
- Verify ``gh-pages`` branch exists
- Check repository permissions
- Review workflow logs in Actions tab

**Common Warnings**:

Documentation builds may show warnings for:

- Duplicate autodoc entries (expected, non-critical)
- Missing optional dependencies (handled by mock imports)
- Forward references in type annotations (non-critical)

These warnings don't prevent successful builds or deployment.

Monitoring and Maintenance
--------------------------

**Regular Checks**:

- Monitor workflow execution on each release
- Verify live documentation site updates
- Review build logs for new warnings or errors

**Dependency Updates**:

Periodically update workflow dependencies:

.. code-block:: yaml

   # Update action versions
   uses: actions/checkout@v4        # → v5 when available
   uses: actions/setup-python@v4    # → v5 when available
   uses: peaceiris/actions-gh-pages@v3  # → v4 when available

Future Enhancements
-------------------

Following progressive enhancement, consider adding:

**Testing Workflow** (next priority):

.. code-block:: yaml

   on:
     push:
       branches: [main]
     pull_request:
       branches: [main]

**Link Checking**:

.. code-block:: yaml

   - name: Check links
     run: sphinx-build -b linkcheck docs docs/build/linkcheck

**Multi-format Documentation**:

.. code-block:: yaml

   - name: Build PDF
     run: sphinx-build -b latex docs docs/build/latex

Best Practices
--------------

**Workflow Design**:

- Keep workflows simple and single-purpose
- Use release triggers for production deployments
- Avoid complex conditional logic
- Provide clear error messages

**Documentation Quality**:

- Test builds locally before releases
- Monitor build warnings and address systematically
- Maintain Sphinx configuration hygiene
- Use version control for documentation changes

**Security**:

- Use official GitHub actions when possible
- Pin action versions for reproducibility
- Avoid exposing sensitive information in logs
- Review third-party action permissions

Success Checklist
------------------

| ✅ Workflow file created in ``.github/workflows/docs.yml``
| ✅ GitHub Pages enabled in repository settings
| ✅ Local documentation build tested successfully
| ✅ First release triggers workflow execution
| ✅ Documentation deploys to GitHub Pages
| ✅ Live documentation site accessible

**Next Steps**: Monitor workflow execution and consider progressive enhancements like automated testing or release automation.