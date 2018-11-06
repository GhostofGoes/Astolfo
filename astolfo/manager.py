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
    Christopher Goes <ghostofgoes(at)gmail(com)>
    https://github.com/GhostofGoes/Astolfo

"""

import atexit
import logging.config
import os.path
import sys
from pprint import pformat
from pathlib import Path
import time
from configparser import ConfigParser

from docopt import docopt
import psutil
from pypresence import Presence

__version__ = '0.2.1'
__author__ = 'Christopher Goes'
DEBUG = False  # Enable debugging mode

# "Discord_UpdatePresence() has a rate limit of one update per 15 seconds.
#  Developers do not need to do anything to handle this rate limit.
#  The SDK will queue up any presence updates sent in that window and send
#  the newest one once the client is free to do so."
# Soooo....we actually don't need to worry about this.
# UPDATE_RATE = 15


LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)-7s %(message)s',
            'datefmt': '%H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'astolfo.log',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'asyncio': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


def get_process(name: str) -> psutil.Process:
    for proc in psutil.process_iter():
        if name.lower() in proc.name().lower():
            logging.debug(f"Found process {proc.name()} "
                          f"(PID: {proc.pid}, "
                          f"Status: {proc.status()})")
            return proc
    logging.warning(f"Couldn't find proc {name}")


def read_config(filepath: Path) -> dict:
    # TODO: error handling
    parser = ConfigParser()
    parser.read(filepath)
    dict_config = {s: dict(parser.items(s)) for s in parser.sections()}
    return dict_config


# FUTURE APPS:
#   VLC Media Player
#   iTunes
#   VMware Workstation (https://github.com/naim94a/vix)
#   VirtualBox?
class Client:

    def __init__(self):
        self.log = logging.getLogger('Client')

        self.start_time = int(time.time())
        self.proc = get_process(self.process_name)
        if self.proc is None:
            self.log.error(f"Could not find the process {self.process_name} "
                           f"for {name.capitalize()}. Ensure it's running, "
                           f"then try again.")
            sys.exit(1)

        # Initialize Discord RPC client
        self.discord = Presence(self.client_id)  # Initialize the client class
        self.discord.connect()  # Start the handshake loop
        atexit.register(self.discord.close)  # Ensure it get's closed on exit

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
                    return f'Episode {parts[0]} - {parts[1]}'
            self.log.debug("Couldn't find an episode ID")
            if DEBUG:
                logging.debug(pformat(open_files))
        return state

    def update(self):
        try:
            state = self.get_state()
        except ValueError:
            self.log.info("No episode playing")
        else:
            self.log.info(f"State: {state}")
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
            self.log.info("Updating Discord status...")
            self.log.debug(f"Values:\n{pformat(kwargs)}")
            self.discord.update(**kwargs)  # Update the user's status on Discord
            if DEBUG:
                for conn in self.proc.connections():
                    self.unique_ips.add((conn.raddr.ip, conn.raddr.port))
                    self.log.debug(f"Unique IPs: {pformat(self.unique_ips)}")


def main(args: dict):
    global DEBUG
    DEBUG = arguments['--debug']
    console_level = 'DEBUG' if args['--verbose'] else 'INFO'
    LOG_CONFIG['handlers']['console']['level'] = console_level
    logging.config.dictConfig(LOG_CONFIG)
    logging.captureWarnings(True)

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
