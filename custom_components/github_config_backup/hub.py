"""Hub for GitHub Config Backup."""
import logging
import os
from datetime import datetime
import git

from homeassistant.helpers import issue_registry as ir
from .const import DOMAIN, CONF_REPO, CONF_TOKEN, CONF_NAME, CONF_EMAIL, CONF_PATHS
from .git_logic import has_staged_changes_vs_head, sync_from_remote

_LOGGER = logging.getLogger(__name__)

class GitHubBackupHub:
    """Class to handle Git operations."""

    def __init__(self, hass, config_entry):
        """Initialize the hub."""
        self.hass = hass
        self.config_entry = config_entry
        self.repo_dir = "/config"
        self.sensor_update_callback = None

    def set_sensor_callback(self, callback):
        self.sensor_update_callback = callback

    def _update_state(self, state):
        if self.sensor_update_callback:
            self.hass.loop.call_soon_threadsafe(self.sensor_update_callback, state)

    def _clear_issue(self):
        """Verwijder de melding veilig vanuit de hoofd-thread."""
        ir.async_delete_issue(self.hass, DOMAIN, "backup_failed")

    def _create_issue(self):
        """Maak een melding aan veilig vanuit de hoofd-thread."""
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            "backup_failed",
            is_fixable=False,
            severity=ir.IssueSeverity.ERROR,
            translation_key="backup_failed",
        )

    def do_backup(self):
        self._update_state("Bezig met voorbereiden...")
        
        # Haal de data op (bij voorkeur de opties als ze zijn aangepast)
        config_data = {**self.config_entry.data, **self.config_entry.options}
        
        repo_url = config_data.get(CONF_REPO)
        token = config_data.get(CONF_TOKEN)
        name = config_data.get(CONF_NAME, "Home Assistant")
        email = config_data.get(CONF_EMAIL, "homeassistant@local.host")
        target_paths_str = config_data.get(CONF_PATHS, "configuration.yaml, template/")
        
        auth_repo = repo_url.replace("https://", f"https://{token}@")

        try:
            if not os.path.exists(os.path.join(self.repo_dir, ".git")):
                self._update_state("Repository initialiseren...")
                repo = git.Repo.init(self.repo_dir)
                origin = repo.create_remote('origin', auth_repo)
                repo.git.branch('-M', 'main')
            else:
                repo = git.Repo(self.repo_dir)
                origin = repo.remotes.origin
                origin.set_url(auth_repo)

            with repo.config_writer() as git_config:
                git_config.set_value('user', 'name', name)
                git_config.set_value('user', 'email', email)
                git_config.set_value('pull', 'rebase', 'false')

            # Fetch + merge so remote commits land in /config; failures must surface (repairs / logs).
            self._update_state("Synchroniseren met remote...")
            sync_from_remote(repo, origin)

            self._update_state("Bestanden voorbereiden...")
            target_paths = [p.strip() for p in target_paths_str.split(",")]
            
            for path in target_paths:
                full_path = os.path.join(self.repo_dir, path)
                if os.path.exists(full_path):
                    repo.git.add(path)
                else:
                    _LOGGER.warning("Bestand/map overgeslagen: %s", path)

            if has_staged_changes_vs_head(repo):
                self._update_state("Bezig met committen...")
                commit_msg = f"Automatische backup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                repo.index.commit(commit_msg)

                self._update_state("Bezig met pushen naar GitHub...")
                origin.push("main")

                self._update_state(f"Succesvol! (Laatste: {datetime.now().strftime('%H:%M')})")
                _LOGGER.info("GitHub Backup succesvol afgerond.")
            else:
                self._update_state(
                    f"Geen wijzigingen in backup-paden (Laatste check: {datetime.now().strftime('%H:%M')})"
                )
                _LOGGER.info("Geen staged wijzigingen in geconfigureerde paden; geen commit.")

            # Als we hier komen, was het succesvol. We roepen de event-loop veilig aan:
            self.hass.loop.call_soon_threadsafe(self._clear_issue)

        except Exception as e:
            _LOGGER.error("Fout tijdens GitHub Backup: %s", e)
            self._update_state(f"Fout opgetreden (zie logboek)")
            
            # Reparaties-item aanmaken, maar nu veilig via de threadsafe aanroep:
            self.hass.loop.call_soon_threadsafe(self._create_issue)
            raise