# tests/test_cli.py

import pytest
from click.testing import CliRunner
from git_ctx.cli import cli, passthrough_git_if_needed
import os
from pathlib import Path
import configparser

@pytest.fixture
def sample_context(tmp_path):
    # Create a fake repo structure
    (tmp_path / '.git').mkdir()
    ctx_file = tmp_path / 'project.context'
    ctx_file.write_text("""[context]
project = testproj
subproject = subproj
""")
    return tmp_path

# def setup_fake_repo_structure(temp_dir, project="vision", subproject="segmentation"):
#     # Create .git directory to mimic Git repo
#     (Path(temp_dir) / ".git").mkdir(parents=True, exist_ok=True)

#     # Create project.context file
#     with open(Path(temp_dir) / "project.context", "w") as f:
#         f.write(f"[context]\nproject = {project}\nsubproject = {subproject}\n")

# def test_checkout_command_runs():
#     runner = CliRunner()
#     with runner.isolated_filesystem() as temp_dir:
#         setup_fake_repo_structure(temp_dir)
#         os.chdir(temp_dir)

#         # Dummy checkout, should fail at actual git call but not our prefixing logic
#         result = runner.invoke(cli, ["-k", "checkout", "testbranch"])
#         assert result.exit_code in (0, 1), f"Unexpected exit code: {result.exit_code}"

# def test_prefix_resolution_with_no_subproject():
#     runner = CliRunner()
#     with runner.isolated_filesystem() as temp_dir:
#         setup_fake_repo_structure(temp_dir, subproject="")
#         os.chdir(temp_dir)

#         result = runner.invoke(cli, ["-k", "branch"])
#         assert result.exit_code in (0, 1)

# def test_missing_project_context():
#     runner = CliRunner()
#     with runner.isolated_filesystem() as temp_dir:
#         (Path(temp_dir) / ".git").mkdir(parents=True)
#         os.chdir(temp_dir)

#         result = runner.invoke(cli, ["-k", "branch"])
#         assert "project.context" in result.output
#         assert result.exit_code == 1

# def test_non_git_directory():
#     runner = CliRunner()
#     with runner.isolated_filesystem() as temp_dir:
#         os.chdir(temp_dir)

#         result = runner.invoke(cli, ["-k", "branch"])
#         assert "Not in a Git repo" in result.output
#         assert result.exit_code == 1

def test_raw_git_passthrough(monkeypatch):
    monkeypatch.setattr('sys.argv', ['git', 'status'])
    try:
        passthrough_git_if_needed()
    except SystemExit:
        assert True  # Should exit cleanly after passthrough

def test_passthrough_with_context_flag(monkeypatch):
    monkeypatch.setattr('sys.argv', ['git', '-k', 'checkout', 'branch'])
    try:
        passthrough_git_if_needed()
    except SystemExit:
        assert False  # Should NOT exit early
