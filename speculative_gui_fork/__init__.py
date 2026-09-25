"""
Speculative-GUI-Fork: Copy-on-Write Time-Travel Display Forking Engine for Computer-Use AI Agents.
Enables parallel speculative path execution across isolated virtual displays with atomic merge and zero-leak rollback.
"""

from .models import (
    BranchState,
    DisplayFrameSnapshot,
    SpeculativeBranch,
    ForkMergeResult,
    SpeculativeAction,
)
from .cow_display_engine import CoWDisplayEngine
from .speculative_runner import SpeculativeRunner

__version__ = "1.0.0"
__all__ = [
    "BranchState",
    "DisplayFrameSnapshot",
    "SpeculativeBranch",
    "ForkMergeResult",
    "SpeculativeAction",
    "CoWDisplayEngine",
    "SpeculativeRunner",
]
