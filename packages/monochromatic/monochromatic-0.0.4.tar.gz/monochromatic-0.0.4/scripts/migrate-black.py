#!/usr/bin/env python3
# check out every commit added by the current branch, monochromaticify them,
# and generate diffs to reconstruct the original commits, but then
# monochromaticified
import logging
import os
import sys
from subprocess import PIPE, Popen, check_output, run


def git(*args: str) -> str:
    return check_output(["git", *args]).decode("utf8").strip()


def monochromaticify(base_branch: str, monochromatic_command: str, logger: logging.Logger) -> int:
    current_branch = git("branch", "--show-current")

    if not current_branch or base_branch == current_branch:
        logger.error("You need to check out a feature branch to work on")
        return 1

    if not os.path.exists(".git"):
        logger.error("Run me in the root of your repo")
        return 1

    merge_base = git("merge-base", "HEAD", base_branch)
    if not merge_base:
        logger.error(
            f"Could not find a common commit for current head and {base_branch}"
        )
        return 1

    commits = git(
        "log", "--reverse", "--pretty=format:%H", f"{merge_base}~1..HEAD"
    ).split()
    for commit in commits:
        git("checkout", commit, f"-b{commit}-monochromatic")
        check_output(monochromatic_command, shell=True)
        git("commit", "-aqm", "monochromaticify")

    git("checkout", base_branch, f"-b{current_branch}-monochromatic")

    for last_commit, commit in zip(commits, commits[1:]):
        allow_empty = (
            b"--allow-empty" in run(["git", "apply", "-h"], stdout=PIPE).stdout
        )
        quiet = b"--quiet" in run(["git", "apply", "-h"], stdout=PIPE).stdout
        git_diff = Popen(
            [
                "git",
                "diff",
                "--binary",
                "--find-copies",
                f"{last_commit}-monochromatic..{commit}-monochromatic",
            ],
            stdout=PIPE,
        )
        git_apply = Popen(
            [
                "git",
                "apply",
            ]
            + (["--quiet"] if quiet else [])
            + [
                "-3",
                "--intent-to-add",
            ]
            + (["--allow-empty"] if allow_empty else [])
            + [
                "-",
            ],
            stdin=git_diff.stdout,
        )
        if git_diff.stdout is not None:
            git_diff.stdout.close()
        git_apply.communicate()
        git("commit", "--allow-empty", "-aqC", commit)

    for commit in commits:
        git("branch", "-qD", "%s-monochromatic" % commit)

    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("base_branch")
    parser.add_argument("--monochromatic_command", default="monochromatic -q .")
    parser.add_argument("--logfile", type=argparse.FileType("w"), default=sys.stdout)
    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler(args.logfile))
    logger.setLevel(logging.INFO)
    sys.exit(monochromaticify(args.base_branch, args.monochromatic_command, logger))
