# Atlas Rendering Pipeline

A comprehensive, high-performance rendering pipeline for converting YAML data to Mermaid diagrams and generating optimized SVG/PNG outputs.

## Overview

The Atlas Rendering Pipeline provides:

- **Single File Rendering**: `render_pipeline.py` for processing individual files
- **Batch Processing**: `batch_render.py` for parallel rendering of multiple files
- **File Watching**: `watch_render.py` for automatic re-rendering on file changes
- **Performance Analysis**: `analyze_performance.py` for optimization insights
- **Makefile Integration**: Comprehensive build targets for all scenarios

## Quick Start

### 1. Install Dependencies

```bash
make install
```

### 2. Render All Diagrams

```bash
make render-all
```

### 3. Show Statistics

```bash
make stats
```

## Core Components

### render_pipeline.py

The main rendering engine that processes single YAML files through the complete pipeline:

- Loads YAML data and validates structure
- Applies Jinja2 templates to generate Mermaid diagrams
- Renders SVG outputs using mermaid-cli
- Generates PNG files with optimization
- Tracks performance metrics and errors

**Usage:**
```bash
python scripts/render_pipeline.py --file data/yaml/example.yaml
python scripts/render_pipeline.py --category guarantees --force
```

### batch_render.py

High-performance batch processor with parallel rendering capabilities:

- Concurrent processing using multiprocessing
- Incremental builds with change detection
- Real-time progress tracking with ETA
- Resource monitoring and throttling
- Comprehensive error handling and recovery

**Usage:**
```bash
python scripts/batch_render.py --categories guarantees mechanisms
python scripts/batch_render.py --workers 4 --force
python scripts/batch_render.py --stats-only
```

### render_config.json

Comprehensive configuration file controlling all aspects of the pipeline:

- **Paths**: Input/output directory configuration
- **Mermaid Settings**: Theme, dimensions, scaling options
- **Optimization**: SVG/PNG optimization parameters
- **Performance**: Worker count, timeouts, memory limits
- **Quality Gates**: File size limits, success rate thresholds

### Makefile

Production-ready build system with targets for every use case:

```bash
# Main rendering targets
make render-all           # Render all diagrams
make render-guarantees    # Render guarantees only
make render-mechanisms    # Render mechanisms only
make render-patterns      # Render patterns only

# Development targets
make render-single FILE=example.yaml  # Render single file
make watch                # Watch for changes
make validate             # Validate schemas

# Utility targets
make clean               # Clean generated files
make stats               # Show statistics
make optimize            # Optimize existing SVGs
```

## Features

### Atlas Color Scheme Integration

The pipeline automatically applies the Atlas color scheme:

- **Planes**: Edge (#0066CC), Service (#00AA00), Stream (#AA00AA), State (#FF8800), Control (#CC0000)
- **Status**: Healthy (#00CC00), Degraded (#FFAA00), Failed (#CC0000), Unknown (#999999)
- **Consistency**: Linearizable (#FF0000) to Eventual (#FFCC00)
- **Regions**: Primary (#00CC00), Secondary (#0099CC), DR (#FF9900)
- **Backpressure**: Control, Queue, Capacity, Timeout, Breaker, Shed

### Performance Optimizations

- **Incremental Builds**: Only render changed files
- **Parallel Processing**: Multi-core rendering with optimal worker count
- **Resource Monitoring**: Automatic throttling on high CPU/memory usage
- **Caching**: File hash-based change detection
- **Optimization**: SVGO for SVG compression, Sharp for PNG generation

### Error Handling & Recovery

- **Graceful Degradation**: Continue processing on individual file errors
- **Retry Logic**: Automatic retry with exponential backoff
- **Comprehensive Logging**: Detailed error reporting and diagnostics
- **Validation**: Schema validation before rendering
- **Recovery**: Cleanup of partial outputs on failure

## Directory Structure

```
site/
├── scripts/
│   ├── render_pipeline.py      # Main rendering engine
│   ├── batch_render.py         # Batch processor
│   ├── watch_render.py         # File watcher
│   ├── analyze_performance.py  # Performance analyzer
│   ├── render_config.json      # Configuration
│   └── README.md               # This file
├── data/yaml/                  # Input YAML files
│   ├── guarantees/
│   ├── mechanisms/
│   └── patterns/
├── templates/                  # Jinja2 templates
├── assets/diagrams/            # Generated outputs
│   ├── mmd/                    # Mermaid files
│   ├── svg/                    # SVG outputs
│   └── png/                    # PNG outputs
└── Makefile                    # Build system
```

## Configuration Options

### Mermaid Settings

```json
{
  "mermaid": {
    "theme": "base",
    "background": "white",
    "width": 1920,
    "height": 1080,
    "scale": 2
  }
}
```

### Performance Settings

```json
{
  "rendering": {
    "incremental": true,
    "timeout": 30,
    "retry_attempts": 3,
    "max_workers": 8
  }
}
```

### Quality Gates

```json
{
  "quality_gates": {
    "max_file_size": {
      "svg": "500KB",
      "png": "2MB"
    },
    "min_success_rate": 95.0
  }
}
```

## Advanced Usage

### Custom Configuration

```bash
make render-all CONFIG=custom_config.json
```

### Force Regeneration

```bash
make render-all FORCE=1
```

### Verbose Output

```bash
make render-guarantees VERBOSE=1
```

### Worker Count Override

```bash
make render-all WORKERS=16
```

### Performance Analysis

```bash
python scripts/analyze_performance.py --benchmark --plot
```

### Watch Mode

```bash
make watch
# or
python scripts/watch_render.py --debounce 1.0
```

## Performance Characteristics

### Throughput

- **Single-threaded**: ~2-5 files/second (depending on complexity)
- **Multi-threaded**: ~8-15 files/second (8-core system)
- **Incremental**: ~50-100 files/second (unchanged files)

### Resource Usage

- **Memory**: ~256MB per worker process
- **CPU**: Scales linearly with worker count
- **Disk I/O**: Optimized with streaming and batching

### Quality Metrics

- **SVG Size**: Target <500KB per file
- **PNG Size**: Target <2MB per file
- **Render Time**: Target <200ms per file
- **Success Rate**: Target >95%

## Troubleshooting

### Common Issues

1. **mermaid-cli not found**: Run `npm install`
2. **Python dependencies missing**: Run `pip install -r requirements.txt`
3. **Permission errors**: Check file permissions and directory access
4. **Memory issues**: Reduce worker count or enable incremental builds
5. **Timeout errors**: Increase timeout in configuration

### Debug Mode

```bash
python scripts/render_pipeline.py --verbose --file problematic.yaml
```

### Performance Issues

```bash
make diagnose                    # System diagnostics
python scripts/analyze_performance.py --benchmark  # Performance analysis
```

## Integration

### CI/CD

```bash
make ci-build                   # Optimized for automation
```

### Git Hooks

```bash
# Pre-commit hook
make validate render-all
```

### Development Workflow

```bash
make dev                        # Start development mode
make watch                      # Auto-render on changes
make test                       # Run validation
```

## Support

- **Issues**: Check logs in `logs/` directory
- **Performance**: Use `make stats` and performance analyzer
- **Configuration**: Refer to `render_config.json` documentation
- **Templates**: See `templates/README.md` for template development