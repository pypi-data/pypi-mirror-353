# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD  ?= sphinx-build
SOURCEDIR    = source
BUILDDIR     = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Custom targets for FailExtract documentation

# Clean all build artifacts
clean:
	@$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "Cleaned all build artifacts"

# Build HTML documentation
html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "HTML documentation generated in $(BUILDDIR)/html/"

# Build HTML with live reload for development
livehtml:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

# Check all external links
linkcheck:
	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "Link check completed. See $(BUILDDIR)/linkcheck/output.txt for results"

# Test code examples in documentation
doctest:
	@$(SPHINXBUILD) -M doctest "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "Doctest completed. See $(BUILDDIR)/doctest/output.txt for results"

# Check documentation coverage
coverage:
	@$(SPHINXBUILD) -M coverage "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "Coverage check completed. See $(BUILDDIR)/coverage/ for results"

# Build PDF documentation (requires LaTeX)
latexpdf:
	@$(SPHINXBUILD) -M latexpdf "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "PDF documentation generated in $(BUILDDIR)/latex/"

# Build EPUB documentation
epub:
	@$(SPHINXBUILD) -M epub "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "EPUB documentation generated in $(BUILDDIR)/epub/"

# Spell check documentation (requires sphinxcontrib.spelling)
spelling:
	@$(SPHINXBUILD) -b spelling "$(SOURCEDIR)" "$(BUILDDIR)/spelling" $(SPHINXOPTS) $(O)
	@echo "Spell check completed. See $(BUILDDIR)/spelling/ for results"

# Quick quality check (build + linkcheck + doctest)
quality:
	@echo "Running documentation quality checks..."
	@$(MAKE) html
	@$(MAKE) linkcheck
	@$(MAKE) doctest
	@echo "Quality check completed"

# Development target (clean + html + open in browser)
dev: clean html
	@echo "Opening documentation in browser..."
	@python -c "import webbrowser; webbrowser.open('file://$(CURDIR)/$(BUILDDIR)/html/index.html')"

# Production build (clean + all formats + quality checks)
production: clean
	@echo "Building production documentation..."
	@$(MAKE) html
	@$(MAKE) epub
	@$(MAKE) linkcheck
	@$(MAKE) doctest
	@$(MAKE) coverage
	@echo "Production build completed"

# Serve documentation locally for testing
serve:
	@echo "Serving documentation at http://localhost:8000"
	@cd $(BUILDDIR)/html && python -m http.server 8000

# Watch for changes and rebuild automatically
watch:
	@echo "Watching for changes... Press Ctrl+C to stop"
	@sphinx-autobuild --host 0.0.0.0 --port 8000 "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

# Install documentation dependencies
install-deps:
	@echo "Installing documentation dependencies..."
	@pip install -r requirements.txt
	@echo "Documentation dependencies installed from requirements.txt"

# First-time setup (install deps + generate API docs + build)
setup: install-deps apidoc html
	@echo "Documentation setup completed!"
	@echo "Run 'make serve' to view docs at http://localhost:8000"

# Generate API documentation from source code
apidoc:
	@echo "Generating API documentation..."
	@sphinx-apidoc -f -o "$(SOURCEDIR)/api" ../src/failextract
	@echo "API documentation generated"

# Validate all documentation
validate: quality coverage spelling
	@echo "Full documentation validation completed"

# Help for custom targets
help-custom:
	@echo "FailExtract Documentation Makefile"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make setup        First-time setup (install deps + build)"
	@echo "  make install-deps Install documentation dependencies"
	@echo "  make html         Build HTML documentation"
	@echo "  make serve        Serve docs locally at http://localhost:8000"
	@echo ""
	@echo "📚 Standard targets:"
	@echo "  html        Build HTML documentation"
	@echo "  clean       Remove build artifacts"
	@echo "  linkcheck   Check external links"
	@echo "  doctest     Test code examples"
	@echo ""
	@echo "🔧 Development targets:"
	@echo "  dev         Clean build + open in browser"
	@echo "  watch       Auto-rebuild on changes (http://localhost:8000)"
	@echo "  serve       Serve docs locally"
	@echo "  livehtml    Live reload development server"
	@echo ""
	@echo "✅ Quality targets:"
	@echo "  quality     Quick quality check"
	@echo "  validate    Full validation suite"
	@echo "  coverage    Documentation coverage"
	@echo "  spelling    Spell check"
	@echo ""
	@echo "📦 Production targets:"
	@echo "  production  Full production build"
	@echo "  latexpdf    Build PDF documentation"
	@echo "  epub        Build EPUB documentation"
	@echo ""
	@echo "🛠️  Utility targets:"
	@echo "  apidoc      Generate API docs from source"
	@echo "  install-deps Install documentation dependencies"
	@echo ""
	@echo "💡 Tips:"
	@echo "  - Use 'make watch' for development with auto-reload"
	@echo "  - Use 'make quality' before committing changes"
	@echo "  - Dependencies are listed in requirements.txt"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)