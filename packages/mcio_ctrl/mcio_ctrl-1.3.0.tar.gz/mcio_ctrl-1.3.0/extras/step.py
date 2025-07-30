"""Test that communication is working properly.
Just sends noop actions and displays observations"""

import argparse
import sys
import textwrap

import mcio_ctrl as mcio

# XXX Doesn't work if agent is started first


def step(n_steps: int, wait: bool = False) -> None:
    env = mcio.gym_lite.GymLite("Hello", render_mode="human", mcio_mode="sync")
    observation = env.reset(commands=["time set day", "teleport @s 0 -60 0 180 0"])
    print(f"RESET: {observation}")
    if n_steps == 0 or wait:
        n_steps = sys.maxsize  # Go forever
    for i in range(1, n_steps):
        if wait:
            input("Step> ")
        action = mcio.network.ActionPacket()
        print(f"ACTION {i+1} {action}")
        observation = env.step(action)
        print(f"OBS {i+1}: {observation}")

    env.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(""" """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mcio.util.logging_add_arg(parser)
    parser.add_argument(
        "--steps", "-s", type=int, default=1, help="Number of steps, 0 for forever"
    )
    parser.add_argument(
        "--wait",
        "-w",
        action="store_true",
        help="Wait for enter between steps. Overrides -s",
    )
    args = parser.parse_args()
    mcio.util.logging_init(args=args)
    return args


def main() -> None:
    args = parse_args()
    step(args.steps, args.wait)


if __name__ == "__main__":
    main()
