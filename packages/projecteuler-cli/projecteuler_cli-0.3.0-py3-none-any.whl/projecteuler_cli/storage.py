"""
Local-storage helpers: solved-problem tracker and file generation.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import textwrap
from datetime import date
from pathlib import Path
from typing import Final

TRACK_FILE: Final = Path.home() / ".projecteuler_tracker.json"


def _load_track() -> dict[str, bool]:
    if TRACK_FILE.exists():
        try:
            return json.loads(TRACK_FILE.read_text())
        except Exception:
            # Corrupt file – start fresh but keep backup.
            TRACK_FILE.rename(TRACK_FILE.with_suffix(".bak"))
    return {}


def mark_done(n: int) -> None:
    data = _load_track()
    data[str(n)] = True
    TRACK_FILE.write_text(json.dumps(data, indent=2))


def stats() -> tuple[int, int]:
    data = _load_track()
    solved = sum(data.values())
    # 9999 is an upper bound; adjust if PE releases >10000.
    return solved, 9999


def make_problem_dir(
    n: int,
    snippet: str,
    lang: str = "py",
) -> Path:
    """
    Create `problem NNN/NNN.[md|py|jl|ipynb]` and return the problem directory.
    """
    prob_dir = Path.cwd() / f"problem {n}"
    prob_dir.mkdir(exist_ok=True)

    # ---------- Markdown ----------
    md_file = prob_dir / f"{n}.md"
    md_file.write_text(snippet + "\n")

    # ---------- Code template ----------
    if lang.lower() in {"py", "python"}:
        code_path = prob_dir / f"{n}.py"
        template = textwrap.dedent(
            f"""
            \"\"\"Project Euler problem {n}.\"\"\"

            # Write your solution function here.
            def solve() -> int:
                raise NotImplementedError

            if __name__ == "__main__":
                print(solve())
            """
        )
    elif lang.lower() in {"jl", "julia"}:
        code_path = prob_dir / f"{n}.jl"
        template = textwrap.dedent(
            f"""
            # Project Euler problem {n}

            function solve()
                # TODO: write solution
            end

            println(solve())
            """
        )
    else:
        raise ValueError("Unsupported --lang (choose py|python|jl|julia)")
    code_path.write_text(template.lstrip())

    # ---------- Notebook ----------
    ipynb_path = prob_dir / f"{n}.ipynb"
    minimal_nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [snippet],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": ["# Start coding here\n"],
                "outputs": [],
                "execution_count": None,
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    import json

    ipynb_path.write_text(json.dumps(minimal_nb, indent=2))
    return prob_dir
