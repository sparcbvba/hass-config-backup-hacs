"""Hub for GitHub Config Backup."""
import logging
import os
from datetime import datetime
import git

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
        """Register the callback to update the sensor state."""
        self.sensor_update_callback = callback

    def _update_state(self, state):
        """Send a state update to the sensor."""
        if self.sensor_update_callback:
            # We moeten dit 'threadsafe' doen, omdat git acties op de achtergrond draaien
            self.hass.loop.call_soon_threadsafe(self.sensor_update_callback, state)

    def do_backup(self):
        """Perform the backup operation. Runs in a background thread."""
        self._update_state("Bezig met voorbereiden...")
        
        data = self.config_entry.data
        repo_url = data["github_repo"]
        token = data["github_token"]
        name = data.get("git_name", "Home Assistant")
        email = data.get("git_email", "homeassistant@local.host")
        
        # In de config flow is dit een comma-gescheiden string
        target_paths_str = data.get("target_paths", "configuration.yaml, template/")
        
        # Bouw de URL op inclusief token
        auth_repo = repo_url.replace("https://", f"https://{token}@")

        try:
            # Check of de map al een git repo is
            if not os.path.exists(os.path.join(self.repo_dir, ".git")):
                self._update_state("Repository initialiseren...")
                repo = git.Repo.init(self.repo_dir)
                origin = repo.create_remote('origin', auth_repo)
                repo.git.branch('-M', 'main')
            else:
                repo = git.Repo(self.repo_dir)
                origin = repo.remotes.origin
                origin.set_url(auth_repo)

            # Stel Git in voor deze actie
            with repo.config_writer() as git_config:
                git_config.set_value('user', 'name', name)
                git_config.set_value('user', 'email', email)
                git_config.set_value('pull', 'rebase', 'false')

            self._update_state("Bezig met pullen...")
            try:
                origin.pull('main')
            except Exception as e:
                _LOGGER.warning("Git Pull mislukt (misschien een lege of nieuwe repo): %s", e)

            self._update_state("Bestanden voorbereiden...")
            target_paths = [p.strip() for p in target_paths_str.split(",")]
            
            for path in target_paths:
                full_path = os.path.join(self.repo_dir, path)
                if os.path.exists(full_path):
                    repo.git.add(path)
                else:
                    _LOGGER.warning("Bestand of map overgeslagen (bestaat niet): %s", path)

            # Check of er daadwerkelijk wijzigingen zijn
            if repo.is_dirty(untracked_files=True):
                self._update_state("Bezig met committen...")
                commit_msg = f"Automatische backup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                repo.index.commit(commit_msg)
                
                self._update_state("Bezig met pushen naar GitHub...")
                origin.push('main')
                
                self._update_state(f"Succesvol! (Laatste: {datetime.now().strftime('%H:%M')})")
                _LOGGER.info("GitHub Backup succesvol afgerond.")
            else:
                self._update_state(f"Geen wijzigingen (Laatste check: {datetime.now().strftime('%H:%M')})")
                _LOGGER.info("Geen wijzigingen gedetecteerd voor GitHub Backup.")

        except Exception as e:
            _LOGGER.error("Fout tijdens GitHub Backup: %s", e)
            self._update_state(f"Fout opgetreden (zie logboek)")
            raise e