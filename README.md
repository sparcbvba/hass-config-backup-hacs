# ![GitHub Config Backup Banner](images/backup-logo.png)

## GitHub Config Backup (HACS Integration)

A Home Assistant Custom Component that automatically backs up your configuration files to a GitHub repository using native Git operations.

## Features
* **Native Home Assistant Integration:** No need for add-ons or bash scripts.
* **Config Flow UI:** Set up everything directly from the Home Assistant UI (Settings > Devices & Services).
* **Automatic Syncs:** Runs smoothly in the background on your configured interval.
* **Dashboard Entities:** Provides a native Button entity (`button.github_backup_nu`) to force a manual sync, and a Sensor entity (`sensor.github_backup_status`) for real-time status updates.
* **Repairs Dashboard Integration:** Active warnings via the Home Assistant Repairs dashboard if a backup fails due to a token issue or merge conflict.
* **Home Assistant Service:** Provides a native service (`github_config_backup.push`) that can be used in automations.
* **Multi-language:** UI supports English, Dutch, and French.

## Prerequisites
1. A **Private** GitHub Repository to store your backup.
2. A GitHub **Personal Access Token (PAT)** with the `repo` scope.

## Installation via HACS

1. Go to **HACS** in Home Assistant.
2. Click on **Integrations**.
3. Click the three dots in the top right corner and select **Custom repositories**.
4. Add the URL of this repository and select **Integration** as the category.
5. Click **Add** and then install the integration.
6. Restart Home Assistant.

## Configuration
After restarting, go to **Settings > Devices & Services**. Click **Add Integration** and search for "GitHub Config Backup". Fill in your repository URL, Token, and the files/folders you want to sync.