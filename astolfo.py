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
import configparser
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


__version__ = '0.2.0'
__author__ = 'Christopher Goes'
__email__ = 'ghostofgoes@gmail.com'

# Enable debugging mode
DEBUG = False

# "Discord_UpdatePresence() has a rate limit of one update per 15 seconds"
UPDATE_RATE = 15

# This enables us to alias in the future if need be
PROCS = {
    'crunchyroll': 'CR.WinApp.exe',
    'funimation': 'Funimation.exe',
    # TODO: this is incorrect, as wwahost is a host for apps, not an app
    'netflix': 'WWAHost.exe',
    'windows media player': 'wmplayer.exe',
}

# FUTURE APPS:
#   VLC Media Player
#   iTunes
CLIENTS = {
    'funimation': {
        'client_id': '463903446764879892',
        'full_name': 'FunimationNow',
        'process': 'Funimation.exe',
        'default_details': 'Watching some anime',
        'default_state': '  ',
    },
    'crunchyroll': {
        'client_id': '471880598668181555',
        'full_name': 'Crunchyroll',
        'process': 'CR.WinApp.exe',
        'default_details': 'Watching some anime',
        'default_state': '  ',
    },
    'netflix': {
        'client_id': '471883383866392596',
        'full_name': 'Netflix',
        'process': 'WWAHost.exe',
        'default_details': 'Binging a show',
        'default_state': '  ',
    },
    'windows media player': {
        'client_id': '471884051259588609',
        'full_name': 'Windows Media Player',
        'process': 'wmplayer.exe',
        'default_details': 'Watching a video on Windows',
        'default_state': '  ',
    },
}

def get_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    config['DEFAULT']
    return config


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


class Client:

    def __init__(self, config, name: str):
        self.log = logging.getLogger('Client')

        self.name = name.lower()
        self.full_name = CLIENTS[self.name]['full_name']
        self.process_name = CLIENTS[self.name]['process']
        self.client_id = CLIENTS[self.name]['client_id']
        self.default_details = CLIENTS[self.name]['default_details']
        self.default_state = CLIENTS[self.name]['default_state']
        

        self.start_time = int(time.time())
        self.proc = get_process(self.process_name)
        if self.proc is None:
            logging.error(f"Could not find the process {self.process_name} "
                          f"for {name.capitalize()}. Ensure it's running, "
                          f"then try again.")
            sys.exit(1)

        # Initialize Discord RPC client
        self.discord = Presence(self.client_id)  # Initialize the client class
        self.discord.connect()  # Start the handshake loop
        atexit.register(self.discord.close)  # Ensure it get's closed on exit

        self.unique_ips = set()  # For debugging purposes

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

    def get_state(self) -> str:
        """Returns state string"""
        state = self.default_state
        if self.name == 'funimation':
            open_files = self.proc.open_files()
            for file in open_files:
                # See notes.md for an example of the file path (it's really long)
                if 'INetHistory' in file.path or 'INetCache' in file.path:
                    base = os.path.basename(file.path)
                    parts = base.split('_')
                    # Episode ID, Language
                    return f'Watching Episode {parts[0]}\tLanguage: {parts[1]}'
            logging.debug("Couldn't find an episode ID")
            if DEBUG:
                logging.debug(pformat(open_files))
        return state

    # @staticmethod
    # def lookup_episode(episode_id: str) -> dict:
    #     # maybe do some lookup dictionary
    #     details = {}
    #     eid = int(episode_id)
    #     if (eid >= 1755434 and eid <= 1755450) or \
    #        (eid >= 1345110 and eid <= 1345140):
    #         details['large_image'] = "full_metal_panic_large"
    #         details['large_text'] = "Full Metal Panic!"
    #         details['small_image'] = "funimation_logo_small"
    #         details['small_text'] = "FunimationNow"
    #         name = "Full Metal Panic!"
    #     else:
    #         details['large_image'] = "funimation_logo_large"
    #         details['large_text'] = "FunimationNow"
    #         name = f"episode {str(episode_id)}"
    #     details['details'] = f"Watching {name}"
    #     return details

    def update(self):
        try:
            # episode_id, language = self.get_episode_id()
            state = self.get_state()
        except ValueError:
            logging.info("No episode playing")
        else:
            # logging.info(f"Episode ID: {episode_id}\tLanguage: {language}")
            logging.info(f"State: {state}")
            kwargs = {
                'pid': self.proc.pid,
                'large_image': 'logo_large',
                'large_text': self.full_name,
                'small_image': 'logo_small',
                'small_text': self.full_name,
                'start': self.start_time,
                'details': self.default_details,
                'state': state,
            }
            # kwargs.update(self.lookup_episode(episode_id))
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
    logging.basicConfig(datefmt="%H:%M:%S", level=log_level, filename='astolfo.log',
                        format="%(asctime)s %(levelname)-7s %(name)-7s %(message)s")
    logging.getLogger('asyncio').setLevel(logging.ERROR)

    client_name = (args['APP'] or 'funimation')
    client = Client(client_name)

    # TODO: when I make it a service, just wait around for proc to respawn when it dies
    while client.proc.is_running():
        client.update()
        logging.debug(f"Sleeping for {UPDATE_RATE} seconds...")
        time.sleep(UPDATE_RATE)


if __name__ == '__main__':
    # TODO: install service option?
    arguments = docopt(__doc__, version=f'Astolfo {__version__}')
    main(args=arguments)
