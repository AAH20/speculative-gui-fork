"""
Speculative Runner: Orchestrates competing agent branches and resolves atomic merges.
"""

import time
from typing import List, Dict, Any, Callable
from .models import (
    BranchState,
    SpeculativeBranch,
    ForkMergeResult,
    SpeculativeAction,
)
from .cow_display_engine import CoWDisplayEngine


class SpeculativeRunner:
    """Manages parallel branch evaluation, fitness scoring, and winner merge resolution."""

    def __init__(self, engine: CoWDisplayEngine):
        self.engine = engine

    def evaluate_and_merge(
        self,
        candidate_branch_ids: List[str],
        fitness_fn: Callable[[SpeculativeBranch, Dict[str, Any]], float],
        master_branch_id: str = "branch_master"
    ) -> ForkMergeResult:
        """Evaluates competing speculative branches, picks the highest scoring branch, and merges it."""
        start_time = time.time()
        scored_branches: List[Tuple[float, str, SpeculativeBranch]] = []
        prevented_side_effects: List[str] = []

        for b_id in candidate_branch_ids:
            branch = self.engine.branches.get(b_id)
            if not branch or branch.status != BranchState.ACTIVE:
                continue

            buffers = self.engine.display_buffers.get(b_id, {})
            score = fitness_fn(branch, buffers)
            branch.score = score
            scored_branches.append((score, b_id, branch))

        if not scored_branches:
            raise RuntimeError("No valid active candidate branches found to evaluate")

        # Sort descending by score
        scored_branches.sort(key=lambda x: x[0], reverse=True)
        winning_score, winning_id, winning_branch = scored_branches[0]

        # Discard losing branches and log side-effects prevented
        discarded_ids: List[str] = []
        for score, b_id, branch in scored_branches[1:]:
            discarded_ids.append(b_id)
            for act in branch.action_log:
                prevented_side_effects.append(
                    f"Discarded action '{act.action_type}' from losing branch {b_id} ({branch.model_name})"
                )
            self.engine.prune_branch(b_id)

        # Atomic Merge of winning branch into master
        self.engine.atomic_merge(winning_id, master_branch_id=master_branch_id)
        exec_time_ms = (time.time() - start_time) * 1000.0

        return ForkMergeResult(
            master_branch_id=master_branch_id,
            winning_branch_id=winning_id,
            winning_model=winning_branch.model_name,
            winning_score=winning_score,
            discarded_branches=discarded_ids,
            actions_replayed=len(winning_branch.action_log),
            execution_time_ms=exec_time_ms,
            side_effects_prevented=prevented_side_effects
        )
