#!/usr/bin/env python3

import subprocess
from pathlib import Path
import configparser
import sys
import logging

# Logging setup
logging.basicConfig(format="🔍 %(message)s", level=logging.INFO)


def passthrough_git_if_needed():
    argv = sys.argv[1:]
    if "-k" not in argv and "--ctx" not in argv:
        # passthrough to normal git
        subprocess.run(["git"] + argv, check=False)
        sys.exit(0)

    # Remove context mode flags from sys.argv
    try:
        idx = argv.index("--ctx") if "--ctx" in argv else argv.index("-k")
        argv.pop(idx)
    except ValueError:
        pass

    # Replace sys.argv for the click app
    sys.argv = [sys.argv[0]] + argv


import click

def get_context_prefix(override):
    if override:
        return override
    curr = Path.cwd()
    while curr != curr.parent:
        ctx_file = curr / 'project.context'
        if (curr / '.git').exists() and ctx_file.exists():
            config = configparser.ConfigParser()
            config.read(ctx_file)
            project = config["context"].get("project", "").strip()
            subproject = config["context"].get("subproject", "").strip()
            if not project:
                logging.error("❌ 'project' key missing in project.context")
                sys.exit(1)
            return f"{project}/{subproject}" if subproject else project
        curr = curr.parent
    logging.error("❌ Not in a Git repo with project.context")
    sys.exit(1)


def git(*args):
    logging.info(f"🌀 Running: git {' '.join(args)}")
    subprocess.run(["git"] + list(args), check=False)


def fuzzy_pick_branch(prefix, remote=False):
    cmd = ["git", "branch", "-a" if remote else "--list", f"{prefix}/*"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    branches = [line.strip().lstrip("* ").strip() for line in result.stdout.splitlines()]
    if not branches:
        logging.warning(f"⚠️ No branches found under prefix: {prefix}")
        sys.exit(1)
    fzf = subprocess.run(["fzf"], input="\n".join(branches), text=True, stdout=subprocess.PIPE)
    if not fzf.stdout:
        logging.error("❌ No branch selected.")
        sys.exit(1)
    selected = fzf.stdout.strip()
    return selected[len(prefix)+1:] if selected.startswith(prefix + "/") else selected


@click.group()
@click.option("-x", "--prefix", default=None, help="Override the context prefix.")
@click.pass_context
def cli(ctx, prefix):
    ctx.ensure_object(dict)
    ctx.obj["CTX_OVERRIDE"] = prefix


@cli.command()
@click.argument("branch", required=False)
@click.option("--pick", is_flag=True, help="Interactively pick a branch using fzf.")
@click.pass_context
def checkout(click_ctx, branch, pick):
    prefix = get_context_prefix(click_ctx.obj.get("CTX_OVERRIDE"))
    if pick:
        branch = fuzzy_pick_branch(prefix)
    if not branch:
        logging.error("❌ Branch name required.")
        return
    git("checkout", f"{prefix}/{branch}")


@cli.command()
@click.argument("branch")
@click.option("--from-base", default=None, help="Create from another branch (default: current HEAD)")
@click.pass_context
def create(click_ctx, branch, from_base):
    prefix = get_context_prefix(click_ctx.obj.get("CTX_OVERRIDE"))
    full_branch = f"{prefix}/{branch}"
    if from_base:
        base = f"{prefix}/{from_base}"
        git("checkout", "-b", full_branch, base)
    else:
        git("checkout", "-b", full_branch)


@cli.command()
@click.argument("branch", required=False)
@click.option("--pick", is_flag=True, help="Interactively pick branch with fzf.")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def push(click_ctx, branch, pick, extra_args):
    prefix = get_context_prefix(click_ctx.obj.get("CTX_OVERRIDE"))
    if pick:
        branch = fuzzy_pick_branch(prefix)
    if not branch:
        logging.error("❌ Branch name required.")
        return
    full_branch = f"{prefix}/{branch}"
    git("push", "-u", "origin", full_branch, *extra_args)


@cli.command()
@click.pass_context
def branch(click_ctx):
    prefix = get_context_prefix(click_ctx.obj.get("CTX_OVERRIDE"))
    git("branch", "--list", f"{prefix}/*")


@cli.command()
@click.pass_context
def fetch(click_ctx):
    prefix = get_context_prefix(click_ctx.obj.get("CTX_OVERRIDE"))
    git("fetch", "origin", f"{prefix}/*")


def main():
    passthrough_git_if_needed()
    cli()

if __name__ == "__main__":
    main()
