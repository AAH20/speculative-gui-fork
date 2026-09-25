"""
Data models and typed schemas for Speculative-GUI-Fork.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import time


class BranchState(str, Enum):
    ACTIVE = "active"
    MERGED = "merged"
    PRUNED = "pruned"
    ROLLED_BACK = "rolled_back"


@dataclass
class DisplayFrameSnapshot:
    snapshot_id: str
    branch_id: str
    display_number: int
    window_buffers: Dict[str, Dict[str, Any]]
    cursor_pos: Tuple[int, int]
    timestamp: float = field(default_factory=time.time)
    digest: str = ""


@dataclass
class SpeculativeAction:
    branch_id: str
    action_type: str  # "click", "type", "script"
    target_window_id: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)


@dataclass
class SpeculativeBranch:
    branch_id: str
    parent_id: Optional[str]
    display_number: int
    assigned_agent: str
    model_name: str
    status: BranchState = BranchState.ACTIVE
    score: float = 0.0
    action_log: List[SpeculativeAction] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


@dataclass
class ForkMergeResult:
    master_branch_id: str
    winning_branch_id: str
    winning_model: str
    winning_score: float
    discarded_branches: List[str]
    actions_replayed: int
    execution_time_ms: float
    side_effects_prevented: List[str]
