# Distributed Systems Architecture Framework v5.0 - Documentation Site

This is the complete documentation site for the Distributed Systems Architecture Framework, built with MkDocs Material.

## Overview

The framework provides a systematic, mathematically grounded approach to designing distributed systems, based on analysis of thousands of real production systems.

## Features

- **15 Universal Laws** with mathematical proofs
- **30 Fundamental Capabilities** taxonomy
- **20 Building Block Primitives** for system composition
- **15 Proven Micro-Patterns** for common problems
- **Complete System Patterns** used by major tech companies
- **Algorithmic Decision Engine** for automated design
- **Production Reality** - what actually breaks and why
- **Formal Verification** methods and testing strategies

## Development

### Prerequisites

- Python 3.8+
- pip

### Setup

```bash
# Install MkDocs and dependencies
pip install mkdocs mkdocs-material pymdownx-superfences mkdocs-mermaid2-plugin

# Clone the repository
git clone <repository-url>
cd site

# Serve locally
mkdocs serve
```

### Building

```bash
# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

## Structure

```
site/
├── mkdocs.yml          # Configuration
├── docs/               # Documentation source
│   ├── index.md        # Homepage
│   ├── getting-started/
│   │   ├── overview.md
│   │   ├── quick-start.md
│   │   └── concepts.md
│   ├── foundation/
│   │   ├── universal-laws.md
│   │   ├── capabilities.md
│   │   └── primitives.md
│   ├── patterns/
│   │   ├── micro-patterns.md
│   │   ├── system-patterns.md
│   │   └── decision-engine.md
│   ├── production/
│   │   ├── reality.md
│   │   ├── proof-obligations.md
│   │   └── best-practices.md
│   ├── examples/
│   │   ├── case-studies.md
│   │   ├── implementation.md
│   │   └── pitfalls.md
│   └── reference/
│       ├── api.md
│       ├── glossary.md
│       └── reading.md
└── site/               # Generated static site
```

## Contributing

1. Follow the [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) style guide
2. Use clear, concise language
3. Include code examples where applicable
4. Test locally before submitting
5. Update navigation in `mkdocs.yml` for new pages

## Features Used

- **Material Theme**: Modern, responsive design
- **Code Highlighting**: Syntax highlighting for multiple languages
- **Mermaid Diagrams**: Interactive diagrams and flowcharts
- **MathJax**: Mathematical formulas and equations
- **Search**: Full-text search functionality
- **Navigation**: Tabbed navigation with sections
- **Dark/Light Mode**: Toggle between themes

## License

This documentation is part of the Distributed Systems Architecture Framework project.

## Links

- 🏠 [Documentation Home](/)
- 📖 [Getting Started](/getting-started/overview/)
- 🔧 [API Reference](/reference/api/)
- 📚 [Further Reading](/reference/reading/)

---

*The Complete Distributed Systems Architecture Framework v5.0: The Definitive Reference*