import subprocess
import pytest
from pathlib import Path
from click.testing import CliRunner

# --- Test: context prefix with subproject present ---
def test_context_prefix_with_subproject(monkeypatch, tmp_path):
    # Setup fake .git and project.context
    root = tmp_path
    (root / ".git").mkdir()
    (root / "project.context").write_text("[context]\nproject = proj\nsubproject = sub\n")

    # Patch current directory to the test repo
    monkeypatch.chdir(root)

    # Import after chdir to simulate real context usage
    from git_ctx.cli import get_context_prefix
    assert get_context_prefix() == "proj/sub"

# --- Test: context prefix with no subproject ---
def test_context_prefix_without_subproject(monkeypatch, tmp_path):
    root = tmp_path
    (root / ".git").mkdir()
    (root / "project.context").write_text("[context]\nproject = proj\n")

    monkeypatch.chdir(root)
    from git_ctx.cli import get_context_prefix
    assert get_context_prefix() == "proj"

# --- Test: context file missing 'project' key ---
def test_context_file_missing_key(monkeypatch, tmp_path):
    root = tmp_path
    (root / ".git").mkdir()
    (root / "project.context").write_text("[context]\nsubproject = foo\n")
    monkeypatch.chdir(root)

    from git_ctx.cli import get_context_prefix
    with pytest.raises(SystemExit):
        get_context_prefix()

# --- Test: checkout command with no branch argument ---
def test_checkout_without_branch(monkeypatch, tmp_path):
    from git_ctx.cli import cli
    runner = CliRunner()

    # Setup .git and context so the command doesn't exit early
    (tmp_path / ".git").mkdir()
    (tmp_path / "project.context").write_text("[context]\nproject = demo\n")

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli, ['checkout'])
    assert result.exit_code == 0
    assert "Branch name required" in result.output

# --- Test: push command with extra arguments like --force ---
def test_push_with_extra_args(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".git").mkdir()
    (tmp_path / "project.context").write_text("[context]\nproject = foo\nsubproject = bar\n")

    from git_ctx.cli import get_context_prefix
    assert get_context_prefix() == "foo/bar"

    # Simulate command call to git function
    from git_ctx.cli import git
    # Not asserting anything because we aren't mocking subprocess yet
    git("push", "-u", "origin", "foo/bar/feature/thing", "--force")

# --- Test: fuzzy branch picker when context has no branches ---
def test_fuzzy_pick_empty_context(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".git").mkdir()
    (tmp_path / "project.context").write_text("[context]\nproject = vision\nsubproject = empty\n")

    from git_ctx.cli import fuzzy_pick_branch
    with pytest.raises(SystemExit):
        fuzzy_pick_branch("vision/empty")
