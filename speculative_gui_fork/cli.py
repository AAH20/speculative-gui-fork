"""
CLI simulation for Speculative-GUI-Fork.
"""

import sys
import json
from .models import SpeculativeAction, BranchState
from .cow_display_engine import CoWDisplayEngine
from .speculative_runner import SpeculativeRunner


def run_simulation() -> None:
    print("\n" + "=" * 70)
    print("❖ SPECULATIVE-GUI-FORK: PARALLEL DISPLAY BRANCHING SIMULATION")
    print("=" * 70)
    print("Master Display: :99 [Claude Opus 5.5]")
    print("-" * 70)

    engine = CoWDisplayEngine(master_display=99)
    runner = SpeculativeRunner(engine)

    print("[STEP 1] FORKING VIRTUAL DISPLAY :99 INTO COMPETING BRANCHES...")

    # Branch A: GPT-6 Astra tests GUI Wizard Path on Display :100
    b_astra = engine.fork_branch(
        parent_branch_id="branch_master",
        child_branch_id="branch_gui_wizard",
        display_number=100,
        agent_id="agent_astra",
        model_name="GPT-6 Astra"
    )
    print(f" • Forked Branch A -> Display :100 (Assigned: GPT-6 Astra, Role: GUI Wizard)")

    # Branch B: DeepSeek V4.1-Flash tests CLI Automation Script on Display :101
    b_deepseek = engine.fork_branch(
        parent_branch_id="branch_master",
        child_branch_id="branch_cli_script",
        display_number=101,
        agent_id="agent_deepseek",
        model_name="DeepSeek V4.1-Flash"
    )
    print(f" • Forked Branch B -> Display :101 (Assigned: DeepSeek V4.1-Flash, Role: CLI Automation)")

    print("-" * 70)
    print("[STEP 2] PARALLEL SPECULATIVE MUTATION...")

    # Branch A attempts GUI button click, encounters crash modal
    engine.mutate_window("branch_gui_wizard", "window_main", SpeculativeAction(
        branch_id="branch_gui_wizard",
        action_type="click",
        target_window_id="window_main",
        payload={"target": "btn_legacy_wizard"}
    ))
    engine.mutate_window("branch_gui_wizard", "window_main", SpeculativeAction(
        branch_id="branch_gui_wizard",
        action_type="type",
        target_window_id="window_main",
        payload={"text": "ERR_MODAL_TIMEOUT: UI wizard hung on step 3"}
    ))
    print(" • [Branch A (:100)] Executed GUI Wizard -> Status: CRASH / TIMEOUT")

    # Branch B executes automated CLI command, completes cleanly
    engine.mutate_window("branch_cli_script", "window_main", SpeculativeAction(
        branch_id="branch_cli_script",
        action_type="script",
        target_window_id="window_main",
        payload={"cmd": "python3 deploy_cluster.py --fast-sync"}
    ))
    engine.mutate_window("branch_cli_script", "window_main", SpeculativeAction(
        branch_id="branch_cli_script",
        action_type="type",
        target_window_id="window_main",
        payload={"text": "DEPLOY_SUCCESS: Cluster online, healthcheck 200 OK"}
    ))
    print(" • [Branch B (:101)] Executed CLI Script  -> Status: SUCCESS (200 OK)")

    print("-" * 70)
    print("[STEP 3] FITNESS EVALUATION & ATOMIC WINNER MERGE...")

    def fitness_evaluator(branch, buffers):
        win_text = str(buffers.get("window_main", {}))
        if "DEPLOY_SUCCESS" in win_text:
            return 0.98
        elif "ERR_MODAL" in win_text:
            return 0.12
        return 0.50

    result = runner.evaluate_and_merge(
        candidate_branch_ids=["branch_gui_wizard", "branch_cli_script"],
        fitness_fn=fitness_evaluator
    )

    print(f" • Winning Branch:           {result.winning_branch_id} ({result.winning_model})")
    print(f" • Winning Score:            {result.winning_score:.2f}")
    print(f" • Discarded Losing Branch:  {result.discarded_branches}")
    print(f" • Actions Merged to :99:    {result.actions_replayed}")
    print(f" • Resolution Latency:       {result.execution_time_ms:.2f} ms")
    print(f" • Side-Effects Prevented:   {len(result.side_effects_prevented)}")
    for se in result.side_effects_prevented:
        print(f"    - {se}")

    print("-" * 70)
    print("[STEP 4] MASTER DISPLAY :99 POST-MERGE STATE:")
    master_state = engine.display_buffers["branch_master"]
    print(json.dumps(master_state, indent=2))
    print("=" * 70 + "\n")


def main() -> None:
    run_simulation()


if __name__ == "__main__":
    main()
