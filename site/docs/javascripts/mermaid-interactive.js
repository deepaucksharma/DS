/**
 * Mermaid Interactive v2.0
 * Beautiful, zoomable, pannable Mermaid diagrams for MkDocs
 * Part of the Distributed Systems Architecture Framework
 */

class MermaidInteractive {
  constructor() {
    this.diagrams = new Map();
    this.initializeTheme();
    this.setupObserver();
  }

  initializeTheme() {
    // Detect theme preference
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    this.theme = prefersDark ? 'dark' : 'default';

    // Listen for theme changes
    const observer = new MutationObserver(() => {
      const isDark = document.body.getAttribute('data-md-color-scheme') === 'slate';
      this.theme = isDark ? 'dark' : 'default';
      this.reinitializeDiagrams();
    });

    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['data-md-color-scheme']
    });
  }

  setupObserver() {
    // Watch for new Mermaid diagrams being added to the page
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) { // Element node
            if (node.classList && node.classList.contains('mermaid')) {
              setTimeout(() => this.initializeDiagram(node), 100);
            } else if (node.querySelector) {
              const mermaidNodes = node.querySelectorAll('.mermaid');
              mermaidNodes.forEach(mNode => {
                setTimeout(() => this.initializeDiagram(mNode), 100);
              });
            }
          }
        });
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  initializeDiagram(element) {
    // Skip if already processed
    if (element.getAttribute('data-interactive-initialized')) return;

    // Find the SVG within the element
    const svg = element.querySelector('svg') || element;
    if (!svg || svg.tagName !== 'svg') return;

    // Create unique ID
    const diagramId = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Create wrapper
    const wrapper = document.createElement('div');
    wrapper.className = 'mermaid-interactive-wrapper';
    wrapper.setAttribute('data-diagram-id', diagramId);

    // Insert wrapper before the element and move element into wrapper
    element.parentNode.insertBefore(wrapper, element);
    wrapper.appendChild(element);

    // Create diagram state
    const diagramState = {
      id: diagramId,
      element: element,
      svg: svg,
      wrapper: wrapper,
      scale: 1,
      translateX: 0,
      translateY: 0,
      isDragging: false,
      startX: 0,
      startY: 0,
      lastTouchDistance: 0
    };

    this.diagrams.set(diagramId, diagramState);

    // Add controls
    this.addControls(diagramState);

    // Enable interactions
    this.enableZoom(diagramState);
    this.enablePan(diagramState);
    this.enableTouch(diagramState);
    this.makeNodesClickable(diagramState);

    // Mark as initialized
    element.setAttribute('data-interactive-initialized', 'true');

    // Apply initial styles
    this.applyTransform(diagramState);
  }

  addControls(diagramState) {
    const controls = document.createElement('div');
    controls.className = 'mermaid-controls';
    controls.innerHTML = `
      <button class="mermaid-btn zoom-in" title="Zoom In (Scroll up)" aria-label="Zoom In">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="11" y1="8" x2="11" y2="14"></line>
          <line x1="8" y1="11" x2="14" y2="11"></line>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
      </button>
      <button class="mermaid-btn zoom-out" title="Zoom Out (Scroll down)" aria-label="Zoom Out">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="8" y1="11" x2="14" y2="11"></line>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
      </button>
      <button class="mermaid-btn zoom-reset" title="Reset View (Double-click)" aria-label="Reset View">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path>
          <path d="M3 3v5h5"></path>
        </svg>
      </button>
      <button class="mermaid-btn fullscreen" title="Fullscreen (F key)" aria-label="Toggle Fullscreen">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M8 3H5a2 2 0 0 0-2 2v3"></path>
          <path d="M21 8V5a2 2 0 0 0-2-2h-3"></path>
          <path d="M3 16v3a2 2 0 0 0 2 2h3"></path>
          <path d="M16 21h3a2 2 0 0 0 2-2v-3"></path>
        </svg>
      </button>
    `;

    diagramState.wrapper.appendChild(controls);

    // Bind control events
    controls.querySelector('.zoom-in').addEventListener('click', () => {
      diagramState.scale = Math.min(4, diagramState.scale * 1.2);
      this.applyTransform(diagramState);
    });

    controls.querySelector('.zoom-out').addEventListener('click', () => {
      diagramState.scale = Math.max(0.5, diagramState.scale * 0.8);
      this.applyTransform(diagramState);
    });

    controls.querySelector('.zoom-reset').addEventListener('click', () => {
      this.resetView(diagramState);
    });

    controls.querySelector('.fullscreen').addEventListener('click', () => {
      this.toggleFullscreen(diagramState);
    });
  }

  enableZoom(diagramState) {
    const handleWheel = (e) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        e.stopPropagation();

        const rect = diagramState.wrapper.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const prevScale = diagramState.scale;
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        diagramState.scale = Math.min(Math.max(0.5, diagramState.scale * delta), 4);

        // Adjust translation to zoom towards cursor
        const scaleDiff = diagramState.scale - prevScale;
        diagramState.translateX -= x * scaleDiff;
        diagramState.translateY -= y * scaleDiff;

        this.applyTransform(diagramState);
      }
    };

    diagramState.wrapper.addEventListener('wheel', handleWheel, { passive: false });
  }

  enablePan(diagramState) {
    const svg = diagramState.svg;

    svg.style.cursor = 'grab';

    svg.addEventListener('mousedown', (e) => {
      if (e.button !== 0) return; // Only left click
      if (e.target.classList.contains('clickable-node')) return;

      e.preventDefault();
      diagramState.isDragging = true;
      diagramState.startX = e.clientX - diagramState.translateX;
      diagramState.startY = e.clientY - diagramState.translateY;
      svg.style.cursor = 'grabbing';
    });

    document.addEventListener('mousemove', (e) => {
      if (!diagramState.isDragging) return;

      diagramState.translateX = e.clientX - diagramState.startX;
      diagramState.translateY = e.clientY - diagramState.startY;
      this.applyTransform(diagramState);
    });

    document.addEventListener('mouseup', () => {
      if (diagramState.isDragging) {
        diagramState.isDragging = false;
        svg.style.cursor = 'grab';
      }
    });

    // Double-click to reset
    svg.addEventListener('dblclick', (e) => {
      e.preventDefault();
      this.resetView(diagramState);
    });
  }

  enableTouch(diagramState) {
    const svg = diagramState.svg;
    let touches = [];

    svg.addEventListener('touchstart', (e) => {
      touches = Array.from(e.touches);

      if (touches.length === 2) {
        e.preventDefault();
        const dx = touches[0].clientX - touches[1].clientX;
        const dy = touches[0].clientY - touches[1].clientY;
        diagramState.lastTouchDistance = Math.sqrt(dx * dx + dy * dy);
      } else if (touches.length === 1) {
        diagramState.isDragging = true;
        diagramState.startX = touches[0].clientX - diagramState.translateX;
        diagramState.startY = touches[0].clientY - diagramState.translateY;
      }
    });

    svg.addEventListener('touchmove', (e) => {
      touches = Array.from(e.touches);

      if (touches.length === 2) {
        e.preventDefault();

        // Calculate pinch zoom
        const dx = touches[0].clientX - touches[1].clientX;
        const dy = touches[0].clientY - touches[1].clientY;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (diagramState.lastTouchDistance > 0) {
          const scale = distance / diagramState.lastTouchDistance;
          diagramState.scale = Math.min(Math.max(0.5, diagramState.scale * scale), 4);
          this.applyTransform(diagramState);
        }

        diagramState.lastTouchDistance = distance;
      } else if (touches.length === 1 && diagramState.isDragging) {
        diagramState.translateX = touches[0].clientX - diagramState.startX;
        diagramState.translateY = touches[0].clientY - diagramState.startY;
        this.applyTransform(diagramState);
      }
    });

    svg.addEventListener('touchend', () => {
      diagramState.isDragging = false;
      diagramState.lastTouchDistance = 0;
    });
  }

  makeNodesClickable(diagramState) {
    const nodes = diagramState.svg.querySelectorAll('g.node, .node, [class*="node"]');

    nodes.forEach(node => {
      const text = node.textContent || '';

      // Check for various clickable indicators
      if (text.includes('Click') ||
          text.includes('→') ||
          node.getAttribute('href') ||
          node.querySelector('a')) {

        node.classList.add('clickable-node');
        node.style.cursor = 'pointer';

        node.addEventListener('click', (e) => {
          e.stopPropagation();

          // Try to find a link
          const link = node.getAttribute('href') ||
                      node.querySelector('a')?.getAttribute('href') ||
                      node.getAttribute('data-link');

          if (link) {
            window.open(link, '_blank');
          }
        });

        // Add hover effect
        node.addEventListener('mouseenter', () => {
          node.style.filter = 'brightness(1.1)';
        });

        node.addEventListener('mouseleave', () => {
          node.style.filter = '';
        });
      }
    });
  }

  applyTransform(diagramState) {
    const transform = `translate(${diagramState.translateX}px, ${diagramState.translateY}px) scale(${diagramState.scale})`;
    diagramState.svg.style.transform = transform;
    diagramState.svg.style.webkitTransform = transform;

    // Update zoom indicator
    this.updateZoomIndicator(diagramState);
  }

  updateZoomIndicator(diagramState) {
    const percent = Math.round(diagramState.scale * 100);
    const resetBtn = diagramState.wrapper.querySelector('.zoom-reset');
    if (resetBtn) {
      resetBtn.setAttribute('data-zoom', `${percent}%`);
    }
  }

  resetView(diagramState) {
    diagramState.scale = 1;
    diagramState.translateX = 0;
    diagramState.translateY = 0;
    this.applyTransform(diagramState);
  }

  toggleFullscreen(diagramState) {
    if (!document.fullscreenElement) {
      diagramState.wrapper.requestFullscreen().catch(err => {
        console.error(`Error attempting to enable fullscreen: ${err.message}`);
      });
    } else {
      document.exitFullscreen();
    }
  }

  reinitializeDiagrams() {
    // Reinitialize all diagrams when theme changes
    this.diagrams.forEach(diagramState => {
      // Update theme-dependent styles
      this.applyTransform(diagramState);
    });
  }

  // Keyboard shortcuts
  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Find focused diagram
      const focusedWrapper = document.querySelector('.mermaid-interactive-wrapper:hover');
      if (!focusedWrapper) return;

      const diagramId = focusedWrapper.getAttribute('data-diagram-id');
      const diagramState = this.diagrams.get(diagramId);
      if (!diagramState) return;

      switch(e.key) {
        case '+':
        case '=':
          e.preventDefault();
          diagramState.scale = Math.min(4, diagramState.scale * 1.2);
          this.applyTransform(diagramState);
          break;
        case '-':
        case '_':
          e.preventDefault();
          diagramState.scale = Math.max(0.5, diagramState.scale * 0.8);
          this.applyTransform(diagramState);
          break;
        case '0':
          e.preventDefault();
          this.resetView(diagramState);
          break;
        case 'f':
        case 'F':
          e.preventDefault();
          this.toggleFullscreen(diagramState);
          break;
      }
    });
  }

  init() {
    // Initialize existing diagrams
    document.querySelectorAll('.mermaid').forEach(element => {
      this.initializeDiagram(element);
    });

    // Setup keyboard shortcuts
    this.setupKeyboardShortcuts();

    // Add performance optimization
    this.setupLazyLoading();
  }

  setupLazyLoading() {
    const observerOptions = {
      root: null,
      rootMargin: '100px',
      threshold: 0.01
    };

    const lazyObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const mermaidDiv = entry.target;
          if (!mermaidDiv.getAttribute('data-processed')) {
            // Trigger Mermaid rendering if needed
            if (typeof mermaid !== 'undefined' && mermaid.init) {
              mermaid.init(undefined, mermaidDiv);
            }
            mermaidDiv.setAttribute('data-processed', 'true');
            lazyObserver.unobserve(mermaidDiv);
          }
        }
      });
    }, observerOptions);

    // Observe unprocessed mermaid elements
    document.querySelectorAll('.mermaid:not([data-processed])').forEach(diagram => {
      lazyObserver.observe(diagram);
    });
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    const mermaidInteractive = new MermaidInteractive();
    mermaidInteractive.init();
  });
} else {
  const mermaidInteractive = new MermaidInteractive();
  mermaidInteractive.init();
}

// Export for use in other scripts
window.MermaidInteractive = MermaidInteractive;