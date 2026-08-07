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


def sync_from_remote(repo: git.Repo, auth_url: str, branch: str = "main") -> None:
    """Fetch from the remote and merge origin/<branch> into the current branch.

    The authenticated URL is passed per call rather than stored in the remote, so the
    token never lands in /config/.git/config. The explicit refspec keeps
    refs/remotes/origin/<branch> up to date, so the merge below is unchanged.

    Failures are not swallowed: callers should surface auth/network/merge conflicts to the user.
    """
    repo.git.fetch(auth_url, f"+{branch}:refs/remotes/origin/{branch}")
    repo.git.merge(f"origin/{branch}", "--no-edit")


def scrub_token(text, token: str) -> str:
    """Strip the token from a message before logging it.

    Git echoes the full remote URL in its error output, so anything derived from a
    GitCommandError would otherwise leak the credential into the Home Assistant log.
    """
    text = str(text)
    return text.replace(token, "***") if token else text
