"""Check that the local tools the audit needs are installed (macOS)."""
import os
import shutil
import sys

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def check(which=shutil.which, exists=os.path.exists) -> list[str]:
    hints = []
    if not which("python3"):
        hints.append("python3 not found: install Python 3 (e.g. `brew install python`).")
    if not which("lighthouse"):
        hints.append("lighthouse not found: run `npm i -g lighthouse`.")
    if not which("sips"):
        hints.append("sips not found: this skill requires macOS.")
    if not exists(CHROME):
        hints.append(f"Google Chrome not found at {CHROME}: install Chrome.")
    return hints


if __name__ == "__main__":
    problems = check()
    for hint in problems:
        print(hint)
    if not problems:
        print("preflight ok")
    sys.exit(1 if problems else 0)
