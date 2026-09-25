"""
Copy-on-Write (CoW) Virtual Display Engine for Speculative-GUI-Fork.
Maintains isolated virtual display branches (:99 -> :100, :101) with atomic state merging.
"""

import copy
import hashlib
import time
from typing import Dict, List, Optional, Tuple, Any

from .models import (
    BranchState,
    DisplayFrameSnapshot,
    SpeculativeBranch,
    SpeculativeAction,
)


class CoWDisplayEngine:
    """Manages Copy-on-Write virtual display state and parallel branched framebuffers."""

    def __init__(self, master_display: int = 99):
        self.master_display = master_display
        self.branches: Dict[str, SpeculativeBranch] = {}
        # branch_id -> {window_id: window_data}
        self.display_buffers: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.display_cursors: Dict[str, Tuple[int, int]] = {}
        self.snapshots: Dict[str, DisplayFrameSnapshot] = {}

        self._init_master()

    def _init_master(self) -> None:
        """Initializes baseline master display :99."""
        master_branch = SpeculativeBranch(
            branch_id="branch_master",
            parent_id=None,
            display_number=self.master_display,
            assigned_agent="agent_claude",
            model_name="Claude Opus 5.5",
            status=BranchState.ACTIVE
        )
        self.branches[master_branch.branch_id] = master_branch
        self.display_buffers[master_branch.branch_id] = {
            "window_main": {
                "title": "Cloud Dashboard v1.0",
                "content": ["Service Status: Healthy", "Active Pods: 4"],
                "input": ""
            }
        }
        self.display_cursors[master_branch.branch_id] = (640, 400)
        self.snapshot_branch("branch_master", "baseline_snapshot")

    def fork_branch(
        self,
        parent_branch_id: str,
        child_branch_id: str,
        display_number: int,
        agent_id: str,
        model_name: str
    ) -> SpeculativeBranch:
        """Creates an isolated Copy-on-Write branch inheriting parent display state."""
        if parent_branch_id not in self.branches:
            raise ValueError(f"Parent branch '{parent_branch_id}' does not exist")

        if child_branch_id in self.branches:
            raise ValueError(f"Branch '{child_branch_id}' already exists")

        # Copy-on-Write deepcopy of window buffers
        parent_buffers = self.display_buffers[parent_branch_id]
        child_buffers = copy.deepcopy(parent_buffers)

        branch = SpeculativeBranch(
            branch_id=child_branch_id,
            parent_id=parent_branch_id,
            display_number=display_number,
            assigned_agent=agent_id,
            model_name=model_name,
            status=BranchState.ACTIVE
        )

        self.branches[child_branch_id] = branch
        self.display_buffers[child_branch_id] = child_buffers
        self.display_cursors[child_branch_id] = self.display_cursors.get(parent_branch_id, (640, 400))

        return branch

    def mutate_window(
        self,
        branch_id: str,
        window_id: str,
        action: SpeculativeAction
    ) -> Dict[str, Any]:
        """Applies a speculative modification exclusively inside a child branch display."""
        if branch_id not in self.branches:
            raise ValueError(f"Branch '{branch_id}' not found")

        buffers = self.display_buffers[branch_id]
        if window_id not in buffers:
            buffers[window_id] = {"title": window_id, "content": [], "input": ""}

        win = buffers[window_id]

        if action.action_type == "type":
            text = action.payload.get("text", "")
            win["input"] += text
        elif action.action_type == "click":
            target = action.payload.get("target", "element")
            win["content"].append(f"[CLICK] Clicked {target}")
        elif action.action_type == "script":
            cmd = action.payload.get("cmd", "")
            win["content"].append(f"[RUN] {cmd}")

        self.branches[branch_id].action_log.append(action)
        return win

    def snapshot_branch(self, branch_id: str, snapshot_id: str) -> DisplayFrameSnapshot:
        """Captures a point-in-time cryptographic digest of branch display state."""
        buffers = self.display_buffers[branch_id]
        cursor = self.display_cursors[branch_id]
        hasher = hashlib.sha256()
        hasher.update(str(sorted(buffers.items())).encode("utf-8"))

        snap = DisplayFrameSnapshot(
            snapshot_id=snapshot_id,
            branch_id=branch_id,
            display_number=self.branches[branch_id].display_number,
            window_buffers=copy.deepcopy(buffers),
            cursor_pos=cursor,
            digest=hasher.hexdigest()[:16]
        )
        self.snapshots[snapshot_id] = snap
        return snap

    def prune_branch(self, branch_id: str) -> None:
        """Discards a speculative branch and frees its isolated framebuffers."""
        if branch_id in self.branches:
            self.branches[branch_id].status = BranchState.PRUNED
            self.display_buffers.pop(branch_id, None)
            self.display_cursors.pop(branch_id, None)

    def atomic_merge(self, winning_branch_id: str, master_branch_id: str = "branch_master") -> None:
        """Atomically merges the winning branch display state into the master display."""
        if winning_branch_id not in self.branches:
            raise ValueError(f"Winning branch '{winning_branch_id}' not found")

        winning_buffers = self.display_buffers[winning_branch_id]
        # Atomically overwrite master display state
        self.display_buffers[master_branch_id] = copy.deepcopy(winning_buffers)
        self.display_cursors[master_branch_id] = self.display_cursors[winning_branch_id]
        self.branches[winning_branch_id].status = BranchState.MERGED
