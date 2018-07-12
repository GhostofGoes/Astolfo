import atexit
import logging
import os.path
import sys
from pprint import pformat

import psutil
from pypresence import Presence

# This enables us to alias in the future if need be
PROCS = {
    'crunchyroll': 'CR.WinApp.exe',
    'funimation': 'Funimation.exe',
    # TODO: this is incorrect, as wwahost is a host for apps, not an app
    'netflix': 'WWAHost.exe',
}
CLIENT_ID = "463903446764879892"
DEBUG = False


def get_process(name: str) -> psutil.Process:
    for proc in psutil.process_iter():
        if name.lower() in proc.name().lower():
            logging.debug(f"Found process {proc.name()} "
                          f"(PID: {proc.pid}, "
                          f"Status: {proc.status()})")
            return proc
    logging.warning(f"Couldn't find proc {name}")


class PresenceClient:

    def __init__(self, name: str):
        self.process_name = PROCS[name]
        self.proc = get_process(self.process_name)
        if self.proc is None:
            logging.error(f"Could not find the process {self.process_name} "
                          f"for {name.capitalize()}. Ensure it's running, "
                          f"then try again.")
            sys.exit(1)
        self.name = name
        self.discord = Presence(CLIENT_ID)  # Initialize the client class
        self.discord.connect()  # Start the handshake loop
        atexit.register(self.discord.close)  # Ensure it get's closed on exit
        self.unique_ips = set()  # For debugging purposes

    def get_episode_id(self) -> tuple:
        """Returns Episode ID and Language."""
        open_files = self.proc.open_files()
        for file in open_files:
            # See notes.md for an example of the file path (it's really long)
            if 'INetHistory' in file.path:
                base = os.path.basename(file.path)
                parts = base.split('_')
                return parts[0], parts[1]  # Episode ID, Language
        # TODO: raise an error instead of returning a empty tuple?
        return ()

    @staticmethod
    def lookup_episode(episode_id: str) -> dict:
        # maybe do some lookup dictionary
        details = {}
        eid = int(episode_id)
        if (eid >= 1755434 and eid <= 1755450) or \
           (eid >= 1345110 and eid <= 1345140):
            details[f'large_image'] = f"full_metal_panic_large"
            details[f'large_text'] = "Full Metal Panic!"
            details[f'small_image'] = f"funimation_logo_small"
            details[f'small_text'] = "FunimationNow"
        else:
            details[f'large_image'] = f"funimation_logo_large"
            details[f'large_text'] = "FunimationNow"
        return details

    def update(self):
        try:
            episode_id, language = self.get_episode_id()
        except ValueError:
            logging.info("No episode playing")
        else:
            logging.info(f"Episode ID: {episode_id}\tLanguage: {language}")
            kwargs = {
                'pid': self.proc.pid,
                'details': f"Watching episode {episode_id}",
                'state': f"Language: {language}"
            }
            kwargs.update(self.lookup_episode(episode_id))
            logging.debug(f"Updating presence...\n{pformat(kwargs)}")
            self.discord.update(**kwargs)  # Update the user's status on Discord
            if DEBUG:
                for conn in self.proc.connections():
                    self.unique_ips.add((conn.raddr.ip, conn.raddr.port))
                logging.debug(f"Unique IPs: {pformat(self.unique_ips)}")
