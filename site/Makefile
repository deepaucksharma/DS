# Distributed Systems Documentation Framework v5.0 Build System
# Supports new navigation structure with Operations parent section

.DEFAULT_GOAL := help
.PHONY: help install serve build validate test clean deploy status review validate-structure validate-paths validate-home validate-operations validate-systems validate-incidents validate-comparisons

# Directory structure validation paths
HOME_DIRS := foundation guarantees mechanisms patterns examples reference
OPERATIONS_DIRS := debugging production
SYSTEMS_DIRS := airbnb amazon cloudflare coinbase datadog discord doordash dropbox github google instacart linkedin meta microsoft netflix openai pinterest reddit robinhood shopify slack snap spotify square stripe tiktok twitch twitter uber zoom
INCIDENTS_DIRS := high-profile cloud-providers financial-services communication entertainment e-commerce travel social-media response-patterns
COMPARISONS_DIRS := database messaging api-networking cloud-infrastructure monitoring-observability ci-cd-devops service-discovery-config frontend

## Display help
help:
	@echo "Distributed Systems Documentation Framework v5.0"
	@echo "=================================================="
	@echo ""
	@echo "🚀 Quick Commands:"
	@echo "  make serve      - Start development server (http://127.0.0.1:8000)"
	@echo "  make build      - Build static site with structure validation"
	@echo "  make test       - Validate diagrams, links, and navigation structure"
	@echo "  make deploy     - Deploy to GitHub Pages"
	@echo ""
	@echo "🔍 Validation Commands:"
	@echo "  make validate-structure  - Validate complete navigation structure"
	@echo "  make validate-paths      - Check all directory paths exist"
	@echo "  make validate-home       - Validate Home section structure"
	@echo "  make validate-operations - Validate Operations parent structure"
	@echo "  make validate-systems    - Validate Systems section (30 companies)"
	@echo "  make validate-incidents  - Validate Incidents section"
	@echo "  make validate-comparisons - Validate Comparisons section"
	@echo ""
	@echo "📊 Status & Review:"
	@echo "  make status     - Show unified creation & review status"
	@echo "  make review     - Run batch compliance review"
	@echo ""
	@echo "🔧 Setup & Maintenance:"
	@echo "  make install    - Install required dependencies"
	@echo "  make clean      - Clean generated files"
	@echo ""
	@echo "⚡ Shortcuts:"
	@echo "  make s          - Alias for 'make serve'"
	@echo "  make b          - Alias for 'make build'"
	@echo "  make v          - Alias for 'make validate-structure'"

## Install dependencies
install:
	@echo "📦 Installing MkDocs and plugins..."
	@pip install -q -r requirements.txt
	@echo "✅ Dependencies installed"

## Start development server
serve:
	@echo "🚀 Starting development server..."
	@echo "   Access at: http://127.0.0.1:8000"
	@mkdocs serve --dev-addr=127.0.0.1:8000

## Validate directory structure
validate-structure: validate-paths validate-home validate-operations validate-systems validate-incidents validate-comparisons
	@echo ""
	@echo "✅ Complete navigation structure validation passed"

## Validate all required paths exist
validate-paths:
	@echo "🔍 Validating directory structure..."
	@for dir in $(HOME_DIRS); do \
		if [ ! -d "docs/$$dir" ]; then \
			echo "❌ Missing Home directory: docs/$$dir"; \
			exit 1; \
		else \
			echo "✅ docs/$$dir"; \
		fi; \
	done
	@for dir in $(OPERATIONS_DIRS); do \
		if [ ! -d "docs/$$dir" ]; then \
			echo "❌ Missing Operations directory: docs/$$dir"; \
			exit 1; \
		else \
			echo "✅ docs/$$dir"; \
		fi; \
	done
	@for dir in $(SYSTEMS_DIRS); do \
		if [ ! -d "docs/systems/$$dir" ]; then \
			echo "❌ Missing Systems directory: docs/systems/$$dir"; \
			exit 1; \
		else \
			echo "✅ docs/systems/$$dir"; \
		fi; \
	done

## Validate Home section structure
validate-home:
	@echo "🏠 Validating Home section structure..."
	@for dir in $(HOME_DIRS); do \
		if [ ! -d "docs/$$dir" ]; then \
			echo "❌ Missing Home subsection: $$dir"; \
			exit 1; \
		fi; \
	done
	@echo "✅ Home section structure valid"

## Validate Operations parent structure
validate-operations:
	@echo "⚙️  Validating Operations parent structure..."
	@for dir in $(OPERATIONS_DIRS); do \
		if [ ! -d "docs/$$dir" ]; then \
			echo "❌ Missing Operations subsection: $$dir"; \
			exit 1; \
		fi; \
	done
	@echo "✅ Operations parent structure valid"

## Validate Systems section (30 companies)
validate-systems:
	@echo "🏢 Validating Systems section (30 companies)..."
	@systems_count=$$(find docs/systems -mindepth 1 -maxdepth 1 -type d | wc -l); \
	if [ $$systems_count -ne 30 ]; then \
		echo "❌ Expected 30 systems, found $$systems_count"; \
		exit 1; \
	fi
	@for dir in $(SYSTEMS_DIRS); do \
		if [ ! -d "docs/systems/$$dir" ]; then \
			echo "❌ Missing system: $$dir"; \
			exit 1; \
		fi; \
	done
	@echo "✅ All 30 systems validated"

## Validate Incidents section
validate-incidents:
	@echo "🚨 Validating Incidents section..."
	@if [ ! -d "docs/incidents" ]; then \
		echo "❌ Missing incidents directory"; \
		exit 1; \
	fi
	@echo "✅ Incidents section structure valid"

## Validate Comparisons section
validate-comparisons:
	@echo "⚖️  Validating Comparisons section..."
	@if [ ! -d "docs/comparisons" ]; then \
		echo "❌ Missing comparisons directory"; \
		exit 1; \
	fi
	@echo "✅ Comparisons section structure valid"

## Validate content
validate:
	@echo "🔍 Validating content..."
	@echo ""
	@echo "Checking Mermaid diagrams..."
	@python3 scripts/validate_mermaid.py || true
	@echo ""
	@echo "Checking internal links..."
	@python3 scripts/check_links.py || true
	@echo ""
	@echo "Checking navigation structure..."
	@$(MAKE) validate-structure

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
v: validate-structure
c: clean
d: deploy