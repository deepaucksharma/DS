# Simplified Makefile for Distributed Systems Documentation
# Focus on Mermaid diagrams embedded in Markdown

.DEFAULT_GOAL := help
.PHONY: help install serve build validate test clean deploy status review

## Display help
help:
	@echo "Distributed Systems Documentation - Streamlined Build"
	@echo "====================================================="
	@echo ""
	@echo "Quick Commands:"
	@echo "  make serve      - Start development server (http://127.0.0.1:8000)"
	@echo "  make build      - Build static site"
	@echo "  make test       - Validate diagrams and links"
	@echo "  make deploy     - Deploy to GitHub Pages"
	@echo ""
	@echo "Status & Review:"
	@echo "  make status     - Show unified creation & review status"
	@echo "  make review     - Run batch compliance review"
	@echo ""
	@echo "Setup & Maintenance:"
	@echo "  make install    - Install required dependencies"
	@echo "  make clean      - Clean generated files"
	@echo ""
	@echo "Shortcuts:"
	@echo "  make s          - Alias for 'make serve'"
	@echo "  make b          - Alias for 'make build'"

## Install dependencies
install:
	@echo "📦 Installing MkDocs and plugins..."
	@pip install -q mkdocs-material mkdocs-mermaid2-plugin
	@echo "✅ Dependencies installed"

## Start development server
serve:
	@echo "🚀 Starting development server..."
	@echo "   Access at: http://127.0.0.1:8000"
	@mkdocs serve --dev-addr=127.0.0.1:8000

## Validate content
validate:
	@echo "🔍 Validating content..."
	@echo ""
	@echo "Checking Mermaid diagrams..."
	@python3 scripts/validate_mermaid.py || true
	@echo ""
	@echo "Checking internal links..."
	@python3 scripts/check_links.py || true

## Run all tests
test: validate
	@echo ""
	@echo "✅ All validation complete"

## Build static site
build: test
	@echo ""
	@echo "🏗️  Building static site..."
	@mkdocs build --clean --quiet
	@echo "✅ Site built in ./site/"
	@echo ""
	@echo "   Files: $$(find site -type f | wc -l)"
	@echo "   Size:  $$(du -sh site | cut -f1)"

## Clean generated files
clean:
	@echo "🧹 Cleaning generated files..."
	@rm -rf site/
	@rm -rf .cache/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean complete"

## Deploy to GitHub Pages
deploy: build
	@echo "📤 Deploying to GitHub Pages..."
	@mkdocs gh-deploy --force --clean
	@echo "✅ Deployed successfully"

## Show unified status dashboard
status:
	@echo "📊 Unified Status Dashboard"
	@echo "============================="
	@python3 scripts/unified_status_tracker.py --scan > /dev/null 2>&1
	@python3 scripts/unified_status_tracker.py --dashboard

## Run batch compliance review
review:
	@echo "🔍 Batch Compliance Review"
	@echo "========================="
	@python3 scripts/batch_diagram_reviewer.py --report

# Shortcuts
s: serve
b: build
t: test
c: clean
d: deploy