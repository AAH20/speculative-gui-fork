"""
Unit tests for Speculative-GUI-Fork using standard unittest.
"""

import unittest
from speculative_gui_fork.models import (
    BranchState,
    SpeculativeAction,
)
from speculative_gui_fork.cow_display_engine import CoWDisplayEngine
from speculative_gui_fork.speculative_runner import SpeculativeRunner


class TestSpeculativeGUIFork(unittest.TestCase):
    def setUp(self):
        self.engine = CoWDisplayEngine(master_display=99)
        self.runner = SpeculativeRunner(self.engine)

    def test_master_init(self):
        self.assertIn("branch_master", self.engine.branches)
        self.assertEqual(self.engine.branches["branch_master"].display_number, 99)
        self.assertEqual(self.engine.branches["branch_master"].status, BranchState.ACTIVE)

    def test_fork_branch_cow_isolation(self):
        # Fork branch
        child = self.engine.fork_branch(
            parent_branch_id="branch_master",
            child_branch_id="branch_child",
            display_number=100,
            agent_id="agent_astra",
            model_name="GPT-6 Astra"
        )
        self.assertEqual(child.display_number, 100)
        self.assertEqual(child.status, BranchState.ACTIVE)

        # Mutate child
        act = SpeculativeAction(
            branch_id="branch_child",
            action_type="type",
            target_window_id="window_main",
            payload={"text": "SPECULATIVE_CHANGE"}
        )
        self.engine.mutate_window("branch_child", "window_main", act)

        # Verify mutation exists in child but NOT in master (CoW isolation)
        child_input = self.engine.display_buffers["branch_child"]["window_main"]["input"]
        master_input = self.engine.display_buffers["branch_master"]["window_main"]["input"]
        self.assertEqual(child_input, "SPECULATIVE_CHANGE")
        self.assertEqual(master_input, "")

    def test_evaluate_and_merge_winner(self):
        # Branch 1 (Poor outcome)
        b1 = self.engine.fork_branch("branch_master", "b1", 101, "agent_1", "GPT-6 Astra")
        self.engine.mutate_window("b1", "window_main", SpeculativeAction("b1", "type", "window_main", {"text": "FAIL"}))

        # Branch 2 (Winning outcome)
        b2 = self.engine.fork_branch("branch_master", "b2", 102, "agent_2", "DeepSeek V4.1")
        self.engine.mutate_window("b2", "window_main", SpeculativeAction("b2", "type", "window_main", {"text": "WIN_SUCCESS"}))

        def fitness(branch, buffers):
            return 1.0 if "WIN_SUCCESS" in str(buffers) else 0.1

        result = self.runner.evaluate_and_merge(["b1", "b2"], fitness)

        self.assertEqual(result.winning_branch_id, "b2")
        self.assertIn("b1", result.discarded_branches)

        # Verify master state updated to winning branch state
        master_input = self.engine.display_buffers["branch_master"]["window_main"]["input"]
        self.assertEqual(master_input, "WIN_SUCCESS")

        # Verify losing branch pruned
        self.assertEqual(self.engine.branches["b1"].status, BranchState.PRUNED)
        self.assertNotIn("b1", self.engine.display_buffers)


if __name__ == "__main__":
    unittest.main()
