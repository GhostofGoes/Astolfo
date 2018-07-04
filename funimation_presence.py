#!/usr/bin/env python3

import atexit
import logging
import json
import time
import os.path
import sys

import pypresence
from pypresence import Presence
import psutil

# TODO list
# * Figure out how to use the episode ID to get more useful information about what's playing.
# * Setup this app as a Windows service. It could either just check perodically for the Funimation process,
#       or I could investigate if there's a way for the OS to wake us up somehow.
# * Get the current time of whatever's playing (need to dive into memory for this most likely)
# * Get the playing state (paused/playing)
# * Link to open app
# * Link to open the specific episode in the app

# Want to follow Discord's recommendations as much as possible here
# https://discordapp.com/developers/docs/rich-presence/best-practices
# Ideal status information
#   Show name
#   Season number
#   Episode number
#   Episode name
#   Start time, current time, or end time (so we can show elapsed/remaining using startTimestamp/endTimestamp) 

# Example:
#   Funimation
#   Full Metal Panic!
#   S2 E9 | Her Problem
#   Elapsed: 6:03

# Other useful information that might be excessive, but let's see if we can get it
#   Season name

# Some examples:
#   Star Blazers 2202 Episode 6: 1757485 (English)
#   Full Metal Panic Season 2 Episode 4: 1345116 (English)
#   Full Metal Panic Season 2 Episode 7: 1345122 (English)
#   Full Metal Panic Season 2 Episode 8: 1345124 (English)
#   Full Metal Panic Season 2 Episode 9: 1345126 (English)
#   Full Metal Panic Season 2 Episode 10: 1345128 (English)

# I suspect the episode "id" is incremented by two per episode since there may be two audo languages, English and Japanese.
# The app doesn't make it easy to switch languages, however, so don't have a easy way to validate this hypothesis.
# Either way, we can get the language from the filename.

def get_episode_id(proc):
    # Returns Episode ID and Language
    open_files = proc.open_files()
    for file in open_files:
        if 'INetHistory' in file.path:
            # Example of path:
            # \\AppData\\Local\\Packages\\FunimationProductionsLTD.FunimationNow_nat5s4eq2a0cr\\AC\\INetHistory
            # \\mms\\HUOPOA32\\1345116_English_431a16b9-c95a-e711-8175-020165574d09[1].dat
            base = os.path.basename(file.path)
            parts = base.split('_')
            return parts[0], parts[1] # Episode ID, Language
    # TODO: raise an error instead of returning a empty tuple?
    return ()


def get_process(name='funimation'):
    for proc in psutil.process_iter():
        if name.lower() in proc.name().lower():
            logging.debug("Found process %s (PID: %d, Status: %s)", 
                          proc.name(), proc.pid, proc.status())
            return proc
    logging.warning("Couldn't find process %s", name)


def main():
    logging.basicConfig(datefmt="%H:%M:%S", level=logging.DEBUG,
                        format="%(asctime)s %(levelname)-7s %(name)-7s %(message)s")
    logging.getLogger('asyncio').setLevel(logging.ERROR)
    with open('app_config.json') as f:
        app_config = json.load(f)
    client_id = app_config["client_id"]
    # we probably don't need the secret for this
    # secret = app_config["secret"]

    RPC = Presence(client_id, pipe=0)  # Initialize the client class
    RPC.connect() # Start the handshake loop
    atexit.register(RPC.close)

    # Get the Funimation process
    process = get_process('funimation')  # TODO: check for none

    # TODO: when I make it a service, just wait around for process to respawn when it dies
    while process.is_running():
        episode_id, language = get_episode_id(process)
        logging.debug("Episode ID: %s\tLanguage: %s", episode_id, language)
        time.sleep(10)

    # from pprint import pprint as pp
    # print(process)
    # pp(process.open_files())
    # pp(process.connections('all'))
    # print(process.exe())
    # print(process.cwd())
    # print(process.cmdline())


if __name__ == '__main__':
    main()
