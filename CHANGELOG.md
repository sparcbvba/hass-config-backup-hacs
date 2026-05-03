# Changelog

## 1.1.3
- **Behaviour**: Commits and pushes run only when staged content in the configured backup paths actually differs from `HEAD` (`git diff --cached`), instead of using repo-wide `is_dirty(untracked_files=True)`. This avoids empty or noise-driven commits from unrelated untracked files under `/config`.
- **Remote sync**: Replaced silent pull failures with an explicit `fetch` followed by `merge origin/main` (same merge semantics as before). Network, auth, or merge problems now surface through the existing error handling and Repairs flow instead of only a log warning.
- **Tests**: Added `pytest` coverage for the staged-vs-HEAD gate (`requirements-test.txt`, `pytest.ini`, `tests/test_git_logic.py`).

## 1.1.2
- **Bugfix**: Fixed a "500 Internal Server Error" when opening the Options Flow via the "Configure" button. Added strict type-casting and safe fallbacks for missing data to prevent the `voluptuous` schema from crashing.

## 1.1.1
- **Bugfix**: Fixed a thread-safety issue where the Repairs dashboard (`issue_registry`) was being called from a background executor job instead of the main event loop. This resolves the `asyncio_thread_safety` warning/error in the Home Assistant logs.

## 1.1.0
- **HACS Branding**: Added native local HACS branding (`brand/icon.png` and `brand/logo.png`) so the custom integration icon displays correctly in the Home Assistant UI.
- **Repository Maintenance**: Added a `.gitignore` file to keep the repository clean from temporary Python and Home Assistant files.
- Version bump in `manifest.json`.

## 1.0.2
- **Options Flow**: Added the ability to change settings (repository, token, interval, and paths) via the "Configure" button without reinstalling the integration.
- **Home Assistant Service**: Registered a native service (`github_config_backup.push`) that can be used in automations and scripts.
- **Repairs Dashboard**: Integrated with the Home Assistant Repairs dashboard to provide active notifications if a backup fails (e.g., due to an expired token or merge conflict).
- **Internationalization**: Added full translations for English, Dutch, French, German, and Spanish, including service descriptions.

## 1.0.0
- **Initial HACS Release**: Migrated from a Home Assistant Add-on to a native Custom Component.
- **Native Git Integration**: Switched to the Python `GitPython` library for more robust Git operations.
- **Config Flow**: Added a user-friendly setup interface (Settings > Devices & Services).
- **Native Entities**: 
  - Added a Button entity (`button.github_backup_nu`) for manual triggers.
  - Added a Sensor entity (`sensor.github_backup_status`) for real-time status updates.
- **Background Sync**: Implemented automatic synchronization based on a configurable time interval.