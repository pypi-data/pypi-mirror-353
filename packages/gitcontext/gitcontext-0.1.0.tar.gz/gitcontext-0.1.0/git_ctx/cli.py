#!/usr/bin/env python3

import subprocess
import click
from pathlib import Path
import configparser
import sys

def get_context_prefix():
    curr = Path.cwd()
    while curr != curr.parent:
        ctx_file = curr / 'project.context'
        if (curr / '.git').exists() and ctx_file.exists():
            config = configparser.ConfigParser()
            config.read(ctx_file)
            project = config["context"].get("project", "").strip()
            subproject = config["context"].get("subproject", "").strip()
            if not project:
                click.echo("❌ 'project' key missing in project.context", err=True)
                sys.exit(1)
            return f"{project}/{subproject}" if subproject else project
        curr = curr.parent
    click.echo("❌ Not in a Git repo with project.context", err=True)
    sys.exit(1)

def git(*args):
    click.echo(f"🌀 git {' '.join(args)}")
    subprocess.run(["git"] + list(args))

def fuzzy_pick_branch(prefix, remote=False):
    cmd = ["git", "branch", "-a" if remote else "--list", f"{prefix}/*"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    branches = [line.strip().lstrip("* ").strip() for line in result.stdout.splitlines()]
    if not branches:
        click.echo(f"⚠️ No branches found under prefix: {prefix}")
        sys.exit(1)
    fzf = subprocess.run(["fzf"], input="\n".join(branches), text=True, stdout=subprocess.PIPE)
    if not fzf.stdout:
        click.echo("❌ No branch selected.")
        sys.exit(1)
    selected = fzf.stdout.strip()
    return selected[len(prefix)+1:] if selected.startswith(prefix + "/") else selected

@click.group()
def cli():
    pass

@cli.command()
@click.argument("branch", required=False)
@click.option("--pick", is_flag=True, help="Interactively pick a branch using fzf.")
def checkout(branch, pick):
    prefix = get_context_prefix()
    if pick:
        branch = fuzzy_pick_branch(prefix)
    if not branch:
        click.echo("❌ Branch name required.")
        return
    git("checkout", f"{prefix}/{branch}")

@cli.command()
@click.argument("branch")
@click.option("--from-base", default=None, help="Create from another branch (default: current HEAD)")
def create(branch, from_base):
    prefix = get_context_prefix()
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
def push(branch, pick, extra_args):
    prefix = get_context_prefix()
    if pick:
        branch = fuzzy_pick_branch(prefix)
    if not branch:
        click.echo("❌ Branch name required.")
        return
    full_branch = f"{prefix}/{branch}"
    git("push", "-u", "origin", full_branch, *extra_args)

@cli.command()
def branch():
    prefix = get_context_prefix()
    git("branch", "--list", f"{prefix}/*")

@cli.command()
def fetch():
    prefix = get_context_prefix()
    git("fetch", "origin", f"{prefix}/*")
