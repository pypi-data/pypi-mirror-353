# tbh_secure_agents - Secure Multi-Agent Framework by TBH.AI
# Author: Saish

import logging

__version__ = "0.5.2"

# EMERGENCY HOTFIX: Skip terminal UI to prevent hanging
# Configure basic logging instead
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Expose core classes
from .expert import Expert
from .operation import Operation
from .squad import Squad
from .agent import SecureAgent

# Expose security validation components (lean and mean)
from .security_validation import SecurityValidator

# Expose memory system components (NEW v5.0)
from .memory.memory_manager import MemoryManager
from .memory.models import MemoryEntry, MemoryType, MemoryPriority, MemoryAccess
from .memory.config import MemorySystemConfig, StorageConfig, SecurityConfig

# Expose terminal UI for direct use in applications
# from .logging_config import get_terminal  # DISABLED - causing import hang

__all__ = [
    'Expert',
    'Operation',
    'Squad',
    'SecureAgent',
    'SecurityValidator',
    'MemoryManager',
    'MemorySystemConfig',
    'MemoryEntry',
    'MemoryType',
    'MemoryPriority',
    'MemoryAccess',
    '__version__',
    # 'get_terminal'  # DISABLED - causing import hang
]
