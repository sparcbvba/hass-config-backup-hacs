"""Tests for pure git backup helpers (no Home Assistant runtime)."""
import importlib.util
from pathlib import Path
import tempfile

import git

_REPO_ROOT = Path(__file__).resolve().parents[1]
# Git writes under `.git/` must live inside the workspace (Cursor sandbox blocks system temp).
_TMP_PARENT = _REPO_ROOT / ".pytest_git_workdirs"
_GIT_LOGIC_PATH = _REPO_ROOT / "custom_components" / "github_config_backup" / "git_logic.py"
_spec = importlib.util.spec_from_file_location(
    "github_config_backup_git_logic_standalone",
    _GIT_LOGIC_PATH,
)
_git_logic = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_git_logic)
has_staged_changes_vs_head = _git_logic.has_staged_changes_vs_head
scrub_token = _git_logic.scrub_token


def _workspace_tmp_dirs():
    _TMP_PARENT.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(dir=_TMP_PARENT), tempfile.TemporaryDirectory(
        dir=_TMP_PARENT
    )


def test_no_staged_changes_after_commit_clean_tree():
    # Empty `template` avoids copying default hooks.
    tpl_cm, tmp_cm = _workspace_tmp_dirs()
    with tpl_cm as tpl_path, tmp_cm as tmp_path:
        repo = git.Repo.init(tmp_path, template=tpl_path)
        cfg = Path(tmp_path) / "configuration.yaml"
        cfg.write_text("a: 1\n", encoding="utf-8")
        repo.git.add("configuration.yaml")
        repo.index.commit("init")
        assert has_staged_changes_vs_head(repo) is False


def test_staged_modification_triggers_true():
    tpl_cm, tmp_cm = _workspace_tmp_dirs()
    with tpl_cm as tpl_path, tmp_cm as tmp_path:
        repo = git.Repo.init(tmp_path, template=tpl_path)
        cfg = Path(tmp_path) / "configuration.yaml"
        cfg.write_text("a: 1\n", encoding="utf-8")
        repo.git.add("configuration.yaml")
        repo.index.commit("init")
        cfg.write_text("a: 2\n", encoding="utf-8")
        repo.git.add("configuration.yaml")
        assert has_staged_changes_vs_head(repo) is True


def test_untracked_file_outside_staged_paths_does_not_trigger_commit_gate():
    """Regression: repo-wide is_dirty(untracked) would be true; staged-vs-HEAD must stay false."""
    tpl_cm, tmp_cm = _workspace_tmp_dirs()
    with tpl_cm as tpl_path, tmp_cm as tmp_path:
        repo = git.Repo.init(tmp_path, template=tpl_path)
        cfg = Path(tmp_path) / "configuration.yaml"
        cfg.write_text("a: 1\n", encoding="utf-8")
        repo.git.add("configuration.yaml")
        repo.index.commit("init")
        (Path(tmp_path) / "junk.log").write_text("noise\n", encoding="utf-8")
        assert has_staged_changes_vs_head(repo) is False


def test_scrub_removes_token_from_real_git_error():
    """Git echoes the full remote URL in its errors; the token must never reach the log."""
    token = "ghp_EXAMPLEtoken1234567890"
    url = f"https://{token}@github.com/owner/repo.git"
    # Shape mirrors what GitPython raises when a push/fetch is rejected.
    exc = git.exc.GitCommandError(["git", "push", url, "HEAD:main"], 128, b"remote: Invalid username or password")
    scrubbed = scrub_token(exc, token)
    assert token not in scrubbed
    assert "***" in scrubbed


def test_scrub_without_token_is_a_passthrough():
    assert scrub_token("plain message", "") == "plain message"
    assert scrub_token("plain message", None) == "plain message"
