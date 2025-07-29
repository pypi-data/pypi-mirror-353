"""
AMP Agent package.

Core functionality for building and running AMP agents.
Optional modules:
- subscription: Event subscription and listening (import from amp_agent.subscription)
- swarm_cell: Swarm-based agent components (import from amp_agent.swarm_cell)
"""

__version__ = "0.1.1"

from amp_agent.core import *
from amp_agent.semantic import *
