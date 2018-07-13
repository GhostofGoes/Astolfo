#!/usr/bin/env python3

"""Astolfo: Discord Rich Presence for Windows 10 Apps.

Share what show you're watching with all your friends on Discord!
 Basically, Astolfo provides Discord status (aka Rich Presence) for
 Windows 10 Microsoft Store apps. Currently, I am working on support for
 Crunchyroll and Funimation, with goals of expanding it to Netflix,
 Rooster Teeth, and others in the future.

Usage:
  astolfo.py [options] [APP]

Arguments:
    APP         Name of application to monitor [default: funimation]

Options:
  -h, --help     Show this help
  --version      Show the version
  -v, --verbose  Enable verbose output (DEBUG-level messages)
  -d, --debug    Enable debugging mode, for development purposes
  
Author:
    Christopher Goes <ghostofgoes(at)gmail.com>
    https://github.com/GhostofGoes/Astolfo

"""

import atexit
import logging
import os.path
import sys
from pprint import pformat
import time

from docopt import docopt
import psutil
from pypresence import Presence
import win32gui
import win32process


__version__ = '0.1.0'
__author__ = 'Christopher Goes'
__email__ = 'ghostofgoes@gmail.com'

CLIENT_ID = "463903446764879892"
DEBUG = False

# "Discord_UpdatePresence() has a rate limit of one update per 15 seconds"
UPDATE_RATE = 15

# This enables us to alias in the future if need be
PROCS = {
    'crunchyroll': 'CR.WinApp.exe',
    'funimation': 'Funimation.exe',
    # TODO: this is incorrect, as wwahost is a host for apps, not an app
    'netflix': 'WWAHost.exe',
}


def get_windows(pid: int) -> dict:
    def callback(hwnd, cb_hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                cb_hwnds.append(hwnd)
        return True
    hwnds = []
    windows = {}
    win32gui.EnumWindows(callback, hwnds)
    for win in hwnds:
        title = str(win32gui.GetWindowText(win)).lower()
        if title != '':
            windows[title] = win
    return windows


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
        self.name = name.lower()
        self.process_name = PROCS[name]
        self.proc = get_process(self.process_name)
        if self.proc is None:
            logging.error(f"Could not find the process {self.process_name} "
                          f"for {name.capitalize()}. Ensure it's running, "
                          f"then try again.")
            sys.exit(1)

        # if name == 'crunchyroll':
        #     # TODO: minor problem...can only get HWND when it's stopped. WTF?
        #     self.proc.suspend()
        #     print(self.proc.status())
        #     windows = get_windows(self.proc.pid)
        #     self.proc.resume()
        #     logging.debug(windows)
        #
        #     if name not in windows:
        #         logging.error(f"Couldn't find the {name.capitalize()} "
        #                       f"window! (PID: {self.proc.pid})")
        #         sys.exit(1)
        #     childs = []
        #     def cb(hwnd, hwnds):
        #         hwnds.append(hwnd)
        #         return True
        #     win32gui.EnumChildWindows(window, cb, childs)
        #     print(childs)
        #     sys.exit(0)

        # Initialize Discord RPC client
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
            logging.info("Updating Discord status...")
            logging.debug(f"Values:\n{pformat(kwargs)}")
            self.discord.update(**kwargs)  # Update the user's status on Discord
            if DEBUG:
                for conn in self.proc.connections():
                    self.unique_ips.add((conn.raddr.ip, conn.raddr.port))
                logging.debug(f"Unique IPs: {pformat(self.unique_ips)}")


def main(args: dict):
    global DEBUG
    DEBUG = arguments['--debug']
    log_level = logging.DEBUG if args['--verbose'] else logging.INFO
    logging.basicConfig(datefmt="%H:%M:%S", level=log_level,
                        format="%(asctime)s %(levelname)-7s %(message)s")
    logging.getLogger('asyncio').setLevel(logging.ERROR)

    client_name = (args['APP'] or 'funimation')
    client = PresenceClient(client_name)

    # TODO: when I make it a service, just wait around for proc to respawn when it dies
    while client.proc.is_running():
        client.update()
        logging.debug(f"Sleeping for {UPDATE_RATE} seconds...")
        time.sleep(UPDATE_RATE)


if __name__ == '__main__':
    arguments = docopt(__doc__, version=f'Astolfo {__version__}')
    main(args=arguments)
