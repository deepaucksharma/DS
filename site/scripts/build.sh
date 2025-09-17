#!/bin/bash
# Simple build script for the documentation site

set -e  # Exit on any error

echo "🚀 Building Documentation Site"
echo "=============================="

# Check if we're in the right directory
if [ ! -f "mkdocs.yml" ]; then
    echo "❌ Error: mkdocs.yml not found. Run this script from the site directory."
    exit 1
fi

# Validate Mermaid diagrams
echo ""
echo "📊 Validating Mermaid diagrams..."
if python3 scripts/validate_mermaid.py; then
    echo "✅ Mermaid validation passed"
else
    echo "⚠️  Warning: Some Mermaid diagrams have issues"
fi

# Check internal links
echo ""
echo "🔗 Checking internal links..."
if python3 scripts/check_links.py; then
    echo "✅ Link validation passed"
else
    echo "⚠️  Warning: Some links are broken"
fi

# Build the site
echo ""
echo "🏗️  Building site with MkDocs..."
mkdocs build --clean

# Check if build was successful
if [ -d "site" ]; then
    echo ""
    echo "✅ Build successful!"
    echo "📁 Output directory: ./site"

    # Count files
    FILE_COUNT=$(find site -type f | wc -l)
    DIR_SIZE=$(du -sh site | cut -f1)

    echo "📊 Statistics:"
    echo "   - Total files: $FILE_COUNT"
    echo "   - Total size: $DIR_SIZE"
else
    echo "❌ Build failed"
    exit 1
fi

echo ""
echo "🎉 Done! To preview locally, run: mkdocs serve"
echo "📤 To deploy to GitHub Pages, run: mkdocs gh-deploy"