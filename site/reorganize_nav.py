#!/usr/bin/env python3
import os

# Systems with complete content (8 files each)
complete_systems = [
    'netflix', 'uber', 'amazon', 'google', 'meta', 'linkedin',
    'stripe', 'spotify', 'airbnb', 'discord', 'cloudflare',
    'shopify', 'twitter', 'microsoft'
]

# Systems with partial content
partial_systems = {
    'zoom': ['architecture', 'request-flow', 'failure-domains']
}

# Generate nav section for systems
nav_systems = []

for system in complete_systems:
    system_title = system.capitalize()
    if system == 'meta':
        system_title = 'Meta'
    elif system == 'linkedin':
        system_title = 'LinkedIn'
    elif system == 'cloudflare':
        system_title = 'Cloudflare'
    elif system == 'doordash':
        system_title = 'DoorDash'
    elif system == 'openai':
        system_title = 'OpenAI'

    nav_systems.append(f"""    - {system_title}:
      - Complete Architecture: systems/{system}/architecture.md
      - Request Flow: systems/{system}/request-flow.md
      - Storage Architecture: systems/{system}/storage-architecture.md
      - Failure Domains: systems/{system}/failure-domains.md
      - Scale Evolution: systems/{system}/scale-evolution.md
      - Cost Breakdown: systems/{system}/cost-breakdown.md
      - Novel Solutions: systems/{system}/novel-solutions.md
      - Production Operations: systems/{system}/production-operations.md""")

# Add Zoom with partial content
nav_systems.append("""    - Zoom:
      - Complete Architecture: systems/zoom/architecture.md
      - Request Flow: systems/zoom/request-flow.md
      - Failure Domains: systems/zoom/failure-domains.md""")

print("Systems Architecture:")
print('\n'.join(nav_systems))