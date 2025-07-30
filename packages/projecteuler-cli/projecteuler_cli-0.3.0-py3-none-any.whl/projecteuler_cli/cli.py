"""
CLI entry-point (exposed as the `projecteuler` console-script).
"""
from __future__ import annotations

import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from datetime import date
from pathlib import Path

from .fetch import fetch_rss, get_problem_html
from .storage import make_problem_dir, mark_done, stats

HELP = """
Commands
--------
projecteuler (problem #) --lang py OR python
projecteuler (problem #) --lang jl OR julia
projecteuler rss
projecteuler rss --txt
projecteuler done (problem #)
projecteuler stats
projecteuler stats --txt

More Info:
--------
Sample Usage: projecteuler 42 --lang julia
The default language is Python if --lang not specified.
IMPORTANT: running a command like the sample usage command will create a fresh directory.
This directory will have the name "problem 42"
THIS WILL OVERWRITE ANY PREVIOUS DIRECTORY OF THE SAME NAME.

""".strip()


def main() -> None:  # noqa: C901
    parser = ArgumentParser(
        prog="projecteuler",
        description="Handy Project Euler helper",
        formatter_class=RawTextHelpFormatter,
        epilog=HELP,
    )

    # The first positional argument can be:
    #   * integer (problem number)
    #   * keyword 'rss'   | 'done' | 'stats'
    parser.add_argument("action", help="problem #, rss, done, or stats")
    parser.add_argument(
        "--lang",
        default="py",
        help="py|python|jl|julia (default: py)",
    )
    parser.add_argument(
        "--txt",
        action="store_true",
        help="on rss|stats: also write plain-text file",
    )
    args, extras = parser.parse_known_args()

    today = date.today().isoformat()

    # ---------- rss ----------
    if args.action.lower() == "rss":
        rss = fetch_rss()
        print(rss)
        if args.txt:
            fn = f"{today}_rss.txt"
            Path(fn).write_text(rss)
            print(f"Wrote {fn}")
        return

    # ---------- stats ----------
    if args.action.lower() == "stats":
        solved, total = stats()
        out = f"Solved {solved} / {total} problems ({solved/total:.2%})"
        print(out)
        if args.txt:
            fn = f"{today}_stats.txt"
            Path(fn).write_text(out + "\n")
            print(f"Wrote {fn}")
        return

    # ---------- done ----------
    if args.action.lower() == "done":
        if not extras:
            print("Specify which problem number to mark as done.", file=sys.stderr)
            sys.exit(1)
        try:
            n = int(extras[0])
        except ValueError:
            print("Problem number must be an integer.", file=sys.stderr)
            sys.exit(1)
        mark_done(n)
        print(f"Marked problem {n} as solved.")
        return

    # ---------- problem fetch ----------
    try:
        n = int(args.action)
    except ValueError:
        print("Invalid command. Run with -h for help.", file=sys.stderr)
        sys.exit(1)

    snippet = get_problem_html(n)
    make_problem_dir(n, snippet, args.lang)
    print(f"Created scaffold for problem {n}.")


if __name__ == "__main__":  # pragma: no cover
    main()
