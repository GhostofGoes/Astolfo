#!/usr/bin/env python3

import atexit
import logging
import time
import os.path
import sys
from pprint import pprint, pformat

from pypresence import Presence
import psutil


# "Discord_UpdatePresence() has a rate limit of one update per 15 seconds"
UPDATE_RATE = 15
CLIENT_ID = "463903446764879892"
DEBUG = True
PROCS = {  # This enables us to alias in the future if need be
    'crunchyroll': 'CR.WinApp.exe',
    'funimation': 'Funimation.exe',
    # TODO: this is incorrect, as wwahost is a host for apps, not an app
    'netflix': 'WWAHost.exe',
}


def get_process(name: str) -> psutil.Process:
    for proc in psutil.process_iter():
        if name.lower() in proc.name().lower():
            logging.debug(f"Found process {proc.name()} "
                          f"(PID: {proc.pid}, "
                          f"Status: {proc.status()})")
            return proc
    logging.warning(f"Couldn't find proc {name}")


# TODO: classes for each client type, e.g. Crunchyroll, Netflix, etc.
class PresenceClient:

    def __init__(self, name: str, discord: Presence):
        self.name = name
        self.process_name = PROCS[name]
        self.proc = get_process(self.process_name)
        if self.proc is None:
            logging.error(f"Could not find the process {self.process_name} "
                          f"for {name.capitalize()}. Ensure it's running, "
                          f"then try again.")
            sys.exit(1)
        else:
            self.discord = discord

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
            self.discord.update(**kwargs)


def main():
    logging.basicConfig(datefmt="%H:%M:%S", level=logging.DEBUG,
                        format="%(asctime)s %(levelname)-7s %(message)s")
    logging.getLogger('asyncio').setLevel(logging.ERROR)

    discord_client = Presence(CLIENT_ID)  # Initialize the client class
    discord_client.connect()  # Start the handshake loop
    atexit.register(discord_client.close)  # Ensure it get's closed on exit

    client_name = 'funimation'
    client = PresenceClient(client_name, discord_client)

    unique_ips = set()

    # TODO: when I make it a service, just wait around for proc to respawn when it dies
    while client.proc.is_running():
        client.update()
        if DEBUG:
            # pprint(proc.connections('all'))
            for conn in client.proc.connections():
                unique_ips.add((conn.raddr.ip, conn.raddr.port))
            pprint(unique_ips)
        logging.debug(f"Sleeping for {UPDATE_RATE} seconds...")
        time.sleep(UPDATE_RATE)


if __name__ == '__main__':
    main()
