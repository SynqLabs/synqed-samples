"""
towers of hanoi demo using the maker/mdap framework.

this script demonstrates solving the towers of hanoi problem with 20 disks
(≈1,048,575 steps) using the maker framework from "solving a million-step llm
task with zero errors" (meyerson et al., arxiv:2511.09030).

the demo showcases:
- maximal agentic decomposition (mad): m=1 step per micro-agent.
- first-to-ahead-by-k voting: error correction at each step.
- red-flagging: discard long/malformed outputs.
- calibration: estimate p and k on a small sample before full run.

usage:
    # set api key
    export ANTHROPIC_API_KEY="sk-ant-..."
    
    # calibration only (estimate p, k, cost)
    python maker_hanoi_20_disks.py --calibrate --num-disks 10
    
    # run small task (10 disks = 1,023 steps)
    python maker_hanoi_20_disks.py --num-disks 10 --k 3
    
    # run full 20-disk task (1,048,575 steps)
    python maker_hanoi_20_disks.py --num-disks 20 --k 3
"""

import os
import sys
import json
import logging
import argparse
import random
from typing import Any

# add synqed to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../synqed-python/src"))

from synqed.mdap import (
    MdapExecutor,
    MdapConfig,
    ModelConfig,
    RedFlagger,
    SynqedStepRunner,
    Voter,
    StepInput,
    StepOutput,
)
from synqed.mdap.execution import print_execution_summary
from synqed.mdap.calibration import estimate_p_and_cost

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ============================================================================
# towers of hanoi domain
# ============================================================================

class HanoiState:
    """
    towers of hanoi state representation.
    
    state is a list of three lists, one per peg:
    - pegs[0]: disks on peg 0.
    - pegs[1]: disks on peg 1.
    - pegs[2]: disks on peg 2.
    
    disks are numbered 1..d, with 1 being the smallest.
    larger disk numbers never sit atop smaller disk numbers.
    """
    
    def __init__(self, num_disks: int):
        self.num_disks = num_disks
        # initial state: all disks on peg 0
        self.pegs = [list(range(num_disks, 0, -1)), [], []]
    
    def copy(self):
        """copy state."""
        new_state = HanoiState(self.num_disks)
        new_state.pegs = [peg[:] for peg in self.pegs]
        return new_state
    
    def move(self, disk: int, from_peg: int, to_peg: int):
        """apply a move to the state."""
        if disk not in self.pegs[from_peg]:
            raise ValueError(f"disk {disk} not on peg {from_peg}")
        if self.pegs[from_peg][-1] != disk:
            raise ValueError(f"disk {disk} is not on top of peg {from_peg}")
        if self.pegs[to_peg] and self.pegs[to_peg][-1] < disk:
            raise ValueError(f"cannot place disk {disk} on smaller disk {self.pegs[to_peg][-1]}")
        
        self.pegs[from_peg].pop()
        self.pegs[to_peg].append(disk)
    
    def is_solved(self) -> bool:
        """check if all disks are on peg 2."""
        return len(self.pegs[2]) == self.num_disks
    
    def to_list(self) -> list[list[int]]:
        """convert to list representation."""
        return [peg[:] for peg in self.pegs]
    
    @classmethod
    def from_list(cls, pegs: list[list[int]]) -> "HanoiState":
        """create from list representation."""
        num_disks = sum(len(peg) for peg in pegs)
        state = cls(num_disks)
        state.pegs = [peg[:] for peg in pegs]
        return state
    
    def __repr__(self) -> str:
        return f"HanoiState({self.pegs})"


def generate_hanoi_strategy(num_disks: int) -> str:
    """
    generate the strategy prompt for hanoi.
    
    from the paper: the strategy is provided to each agent to isolate
    execution from insight. the strategy is optimal for even number of disks.
    """
    return f"""You are solving the Towers of Hanoi puzzle with {num_disks} disks.

GOAL: Move all disks from peg 0 to peg 2.

RULES:
1. Only move one disk at a time.
2. A larger disk can never sit on top of a smaller disk.
3. You can only move the top disk from a peg.

STRATEGY (for even number of disks):
1. Never move the smallest disk (disk 1) to the middle peg (peg 1).
2. Move the smallest disk clockwise: 0 → 2 → 1 → 0 → ...
3. Between moves of the smallest disk, there is exactly one legal move (not involving disk 1).
4. Always make that legal move.

You will be told the current state and the previous move. Your job is to:
1. Determine the next move.
2. Compute the resulting state after that move.

Output format (REQUIRED):
move = [disk, from_peg, to_peg]
next_state = [[peg0_disks], [peg1_disks], [peg2_disks]]

Example:
move = [1, 0, 2]
next_state = [[5, 4, 3, 2], [], [1]]
"""


def build_hanoi_prompt(step_input: StepInput) -> str:
    """
    build prompt for a single hanoi step.
    
    the prompt includes:
    - current state.
    - previous move (if any).
    - request for next move and next state.
    """
    state = step_input.state
    prev_move = step_input.metadata.get("prev_move")
    
    prompt = f"""Current state:
{json.dumps(state, indent=2)}

"""
    
    if prev_move:
        prompt += f"Previous move: {prev_move}\n\n"
    
    prompt += """What is the next move, and what will the resulting state be?

Output format (REQUIRED):
move = [disk, from_peg, to_peg]
next_state = [[peg0_disks], [peg1_disks], [peg2_disks]]
"""
    
    return prompt


def parse_hanoi_response(raw_text: str) -> tuple[Any, Any]:
    """
    parse hanoi response into (action, next_state).
    
    expected format:
        move = [disk, from_peg, to_peg]
        next_state = [[...], [...], [...]]
    """
    import re
    
    # try to extract move
    move_match = re.search(r"move\s*=\s*\[(\d+),\s*(\d+),\s*(\d+)\]", raw_text, re.IGNORECASE)
    if not move_match:
        raise ValueError("move not found")
    
    disk = int(move_match.group(1))
    from_peg = int(move_match.group(2))
    to_peg = int(move_match.group(3))
    action = [disk, from_peg, to_peg]
    
    # try to extract next_state
    state_match = re.search(r"next_state\s*=\s*(\[.*\])", raw_text, re.IGNORECASE | re.DOTALL)
    if not state_match:
        raise ValueError("next_state not found")
    
    state_str = state_match.group(1)
    # safely parse the list
    next_state = json.loads(state_str)
    
    return action, next_state


def compute_hanoi_ground_truth(state: list[list[int]], num_disks: int) -> list[int]:
    """
    compute the correct next move for hanoi given the strategy.
    
    this is used for calibration to determine p.
    """
    # implement simple heuristic based on strategy
    # (for calibration purposes; not optimal solver)
    
    # find which peg has disk 1
    disk1_peg = None
    for peg_idx, peg in enumerate(state):
        if peg and peg[-1] == 1:
            disk1_peg = peg_idx
            break
    
    # move disk 1 clockwise: 0 -> 2 -> 1 -> 0
    if disk1_peg is not None:
        next_peg = (disk1_peg + 2) % 3
        return [1, disk1_peg, next_peg]
    
    # otherwise, find the legal move not involving disk 1
    # (simplified: just pick first legal move)
    for from_peg_idx, from_peg in enumerate(state):
        if not from_peg or from_peg[-1] == 1:
            continue
        
        for to_peg_idx in range(3):
            if to_peg_idx == from_peg_idx:
                continue
            
            to_peg = state[to_peg_idx]
            disk = from_peg[-1]
            
            if not to_peg or to_peg[-1] > disk:
                return [disk, from_peg_idx, to_peg_idx]
    
    # no legal move found
    return None


def hanoi_state_builder(state: list[list[int]]) -> dict:
    """build metadata dict from hanoi state."""
    return {"state": state}


def hanoi_validator(final_state: list[list[int]], actions: list[Any]) -> tuple[bool, str]:
    """
    validate the final hanoi result.
    
    checks:
    - all disks are on peg 2.
    - correct number of moves (2^d - 1).
    """
    num_disks = sum(len(peg) for peg in [[]] * 3)
    for peg in final_state:
        num_disks = max(num_disks, len(peg))
    
    # check all disks on peg 2
    if len(final_state[2]) != num_disks:
        return False, f"expected {num_disks} disks on peg 2, got {len(final_state[2])}"
    
    # check correct number of moves
    expected_moves = 2 ** num_disks - 1
    if len(actions) != expected_moves:
        return False, f"expected {expected_moves} moves, got {len(actions)}"
    
    return True, ""


# ============================================================================
# calibration
# ============================================================================

def run_calibration(args):
    """run calibration to estimate p, k, and cost."""
    logger.info(f"calibrating on {args.num_disks} disks...")
    
    # setup model
    provider = args.provider
    if provider == "anthropic":
        default_model = "claude-sonnet-4-20250514"
        api_key = os.getenv("ANTHROPIC_API_KEY")
        cost_per_input = 0.000003   # $3 per 1M tokens
        cost_per_output = 0.000015  # $15 per 1M tokens
    else:  # openai
        default_model = "gpt-4o-mini"
        api_key = os.getenv("OPENAI_API_KEY")
        cost_per_input = 0.00000015   # $0.15 per 1M tokens
        cost_per_output = 0.0000006   # $0.60 per 1M tokens
    
    model_config = ModelConfig(
        provider=provider,
        model=args.model or default_model,
        api_key=api_key,
        temperature=0.1,
        max_output_tokens=args.max_output_tokens,
        cost_per_input_token=cost_per_input,
        cost_per_output_token=cost_per_output,
    )
    
    # setup red-flagger
    red_flagger = RedFlagger(
        max_output_tokens=args.max_output_tokens,
        required_fields=["action", "next_state"],
        strict_format=True,
    )
    
    # setup step runner
    system_prompt = generate_hanoi_strategy(args.num_disks)
    step_runner = SynqedStepRunner(
        model_config=model_config,
        red_flagger=red_flagger,
        prompt_builder=build_hanoi_prompt,
        response_parser=parse_hanoi_response,
        system_prompt=system_prompt,
    )
    
    # task sampler: generate random steps
    def task_sampler(idx: int) -> StepInput:
        # generate a random valid hanoi state
        num_disks = args.num_disks
        # simplified: just use a random step index
        step_idx = random.randint(0, 2 ** num_disks - 2)
        
        # generate state (simplified: start from initial)
        state = HanoiState(num_disks)
        return StepInput(
            step_index=step_idx,
            total_steps=2 ** num_disks - 1,
            state=state.to_list(),
            metadata={},
        )
    
    # ground truth function
    def ground_truth_fn(step_input: StepInput) -> Any:
        return compute_hanoi_ground_truth(step_input.state, args.num_disks)
    
    # run calibration
    report = estimate_p_and_cost(
        model_config=model_config,
        task_sampler=task_sampler,
        ground_truth_fn=ground_truth_fn,
        step_runner=step_runner,
        num_samples=args.calibration_samples,
        target_success_prob=args.target_success_prob,
        total_steps=2 ** args.num_disks - 1,
    )
    
    # print report
    print(f"\n{'='*60}")
    print(f"Calibration Report")
    print(f"{'='*60}")
    print(f"Model: {report.model_name}")
    print(f"Samples: {report.num_samples}")
    print(f"Per-step success rate p: {report.p_estimate:.4f} ± {report.p_std:.4f}")
    print(f"Avg input tokens: {report.avg_input_tokens:.1f}")
    print(f"Avg output tokens: {report.avg_output_tokens:.1f}")
    print(f"Cost per sample: ${report.cost_per_sample:.6f}")
    print(f"Recommended k: {report.k_min}")
    print(f"Projected total cost: ${report.projected_cost:.2f}")
    print(f"Projected total samples: {report.projected_samples:,}")
    print(f"{'='*60}\n")


# ============================================================================
# full execution
# ============================================================================

def run_full_task(args):
    """run the full hanoi task with mdap/maker."""
    num_disks = args.num_disks
    total_steps = 2 ** num_disks - 1
    
    logger.info(f"running hanoi with {num_disks} disks ({total_steps:,} steps)...")
    
    # setup model
    provider = args.provider
    if provider == "anthropic":
        default_model = "claude-sonnet-4-20250514"
        api_key = os.getenv("ANTHROPIC_API_KEY")
    else:  # openai
        default_model = "gpt-4o-mini"
        api_key = os.getenv("OPENAI_API_KEY")
    
    model_config = ModelConfig(
        provider=provider,
        model=args.model or default_model,
        api_key=api_key,
        temperature=0.1,
        max_output_tokens=args.max_output_tokens,
    )
    
    # setup red-flagger
    red_flagger = RedFlagger(
        max_output_tokens=args.max_output_tokens,
        required_fields=["action", "next_state"],
        strict_format=True,
    )
    
    # setup step runner
    system_prompt = generate_hanoi_strategy(num_disks)
    step_runner = SynqedStepRunner(
        model_config=model_config,
        red_flagger=red_flagger,
        prompt_builder=build_hanoi_prompt,
        response_parser=parse_hanoi_response,
        system_prompt=system_prompt,
    )
    
    # setup voter
    voter = Voter(
        step_runner=step_runner,
        red_flagger=red_flagger,
        k=args.k,
        max_votes=args.max_votes,
        max_samples=args.max_samples,
        first_to_k=args.first_to_k,
    )
    
    # setup executor
    mdap_config = MdapConfig(
        k=args.k,
        max_votes_per_step=args.max_votes,
        red_flag_max_output_tokens=args.max_output_tokens,
    )
    
    executor = MdapExecutor(
        mdap_config=mdap_config,
        voter=voter,
        state_builder=hanoi_state_builder,
        validator=hanoi_validator,
    )
    
    # initial state
    initial_state = HanoiState(num_disks).to_list()
    
    # run task
    result = executor.run_task(
        initial_state=initial_state,
        num_steps=total_steps,
        verbose=True,
    )
    
    # print summary
    print_execution_summary(result)
    
    # save results
    if args.output:
        output_data = {
            "num_disks": num_disks,
            "total_steps": total_steps,
            "k": args.k,
            "success": result.success,
            "actions": result.actions,
            "total_samples": result.total_samples,
            "total_valid_samples": result.total_valid_samples,
            "total_red_flagged": result.total_red_flagged,
        }
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        logger.info(f"results saved to {args.output}")


# ============================================================================
# main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="towers of hanoi with maker/mdap (uses anthropic claude by default)"
    )
    
    parser.add_argument("--num-disks", type=int, default=10, help="number of disks")
    parser.add_argument("--k", type=int, default=3, help="vote margin for first-to-ahead-by-k")
    parser.add_argument("--max-votes", type=int, default=20, help="max votes per step")
    parser.add_argument("--max-samples", type=int, default=100, help="max samples per step")
    parser.add_argument("--max-output-tokens", type=int, default=750, help="max output tokens")
    parser.add_argument("--first-to-k", action="store_true", help="use first-to-k instead of first-to-ahead-by-k")
    
    parser.add_argument("--calibrate", action="store_true", help="run calibration only")
    parser.add_argument("--calibration-samples", type=int, default=1000, help="calibration samples")
    parser.add_argument("--target-success-prob", type=float, default=0.95, help="target success probability")
    
    parser.add_argument("--output", type=str, help="output file for results")
    
    # provider selection
    parser.add_argument("--provider", type=str, default="anthropic", choices=["anthropic", "openai"], 
                        help="llm provider (default: anthropic)")
    parser.add_argument("--model", type=str, help="model name (overrides default for provider)")
    
    args = parser.parse_args()
    
    # check api key
    if args.provider == "anthropic":
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("❌ ANTHROPIC_API_KEY not set!")
            print("   export ANTHROPIC_API_KEY='sk-ant-...'")
            sys.exit(1)
    elif args.provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ OPENAI_API_KEY not set!")
            print("   export OPENAI_API_KEY='sk-...'")
            sys.exit(1)
    
    if args.calibrate:
        run_calibration(args)
    else:
        run_full_task(args)


if __name__ == "__main__":
    main()

