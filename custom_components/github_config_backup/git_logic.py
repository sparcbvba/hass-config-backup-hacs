"""Pure Git helpers for the backup hub (no Home Assistant imports; testable in isolation)."""
import git
from git.exc import GitCommandError


def has_staged_changes_vs_head(repo: git.Repo) -> bool:
    """Return True if the index differs from HEAD (i.e. `git diff --cached` is non-empty).

    Unlike repo-wide is_dirty(untracked_files=True), this ignores untracked files outside
    the paths you explicitly staged, so unrelated noise under /config does not trigger commits.
    """
    try:
        repo.git.diff("--cached", "--quiet")
        return False
    except GitCommandError as exc:
        if exc.status == 1:
            return True
        raise


def sync_from_remote(repo: git.Repo, origin, branch: str = "main") -> None:
    """Fetch from origin and merge origin/<branch> into the current branch.

    Failures are not swallowed: callers should surface auth/network/merge conflicts to the user.
    """
    origin.fetch()
    repo.git.merge(f"origin/{branch}", "--no-edit")
