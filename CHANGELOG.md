# Changelog

## 1.0.2
- **Options Flow**: Added the ability to change settings (repository, token, interval, and paths) via the "Configure" button without reinstalling the integration.
- **Home Assistant Service**: Registered a native service (`github_config_backup.push`) that can be used in automations and scripts.
- **Repairs Dashboard**: Integrated with the Home Assistant Repairs dashboard to provide active notifications if a backup fails (e.g., due to an expired token or merge conflict).
- **Internationalization**: Added full translations for English, Dutch, French, German, and Spanish, including service descriptions.
- **Branding**: Added a new official banner image for the HACS store.

## 1.0.0
- **Initial HACS Release**: Migrated from a Home Assistant Add-on to a native Custom Component.
- **Native Git Integration**: Switched to the Python `GitPython` library for more robust Git operations.
- **Config Flow**: Added a user-friendly setup interface (Settings > Devices & Services).
- **Native Entities**: 
  - Added a Button entity (`button.github_backup_nu`) for manual triggers.
  - Added a Sensor entity (`sensor.github_backup_status`) for real-time status updates.
- **Background Sync**: Implemented automatic synchronization based on a configurable time interval.