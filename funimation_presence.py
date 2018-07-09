#!/usr/bin/env python3

import atexit
import logging
import json
import time
import os.path
import sys
from pprint import pprint, pformat

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
# * Put in a badge and shoutout to pypresence

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
# Format:
#   App name
#   Details (this will wrap lines)
#   Status (string)
#   start (int)

# Other useful information that might be excessive, but let's see if we can get it
#   Season name

# Some examples:
#   Star Blazers 2202 Episode 6: 1757485 (English)
#   Full Metal Panic Season 2 Episode 4: 1345116 (English)
#   Full Metal Panic Season 2 Episode 7: 1345122 (English)
#   Full Metal Panic Season 2 Episode 8: 1345124 (English)
#   Full Metal Panic Season 2 Episode 9: 1345126 (English)
#   Full Metal Panic Season 2 Episode 10: 1345128 (English)
#   Full Metal Panic Season 3 Episode 1: 1755434 (English)

# I suspect the episode "id" is incremented by two per episode since there may be two audo languages, English and Japanese.
# The app doesn't make it easy to switch languages, however, so don't have a easy way to validate this hypothesis.
# Either way, we can get the language from the filename.

# Homepage IP (nslookup funimation.com): 107.154.106.169
# No episode playing:
#   172.217.12.14 - This is a Google analytics server
#
# Playing episodes:
#   107.154.108.80:443
#   143.204.31.65:443
#   172.217.12.14:80
#   172.217.12.4:443
#   38.122.56.118:443

# "Discord_UpdatePresence() has a rate limit of one update per 15 seconds"
UPDATE_RATE = 15
DEBUG = True
unique_ips = set()


def get_episode_id(proc: psutil.Process) -> tuple:
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


def get_process(name: str = 'funimation') -> psutil.Process:
    for proc in psutil.process_iter():
        if name.lower() in proc.name().lower():
            logging.debug("Found process %s (PID: %d, Status: %s)", 
                          proc.name(), proc.pid, proc.status())
            return proc
    logging.warning(f"Couldn't find process {name}")


def lookup_episode(episode_id: str) -> dict:
    # maybe do some lookup dictionary
    details = {}
    id = int(episode_id)
    for size in ['large']:  # , 'small'
        # if episode_id.startswith('13451'):
        if (id >= 1755434 and id <= 1755450) or \
           (id >= 1345110 and id <= 1345140):
            details[f'{size}_image'] = f"full_metal_panic_{size}"
            details[f'{size}_text'] = "Full Metal Panic!"
        else:
            details[f'{size}_image'] = f"funimation_logo_{size}"
            details[f'{size}_text'] = "FunimationNow!"
    return details

def main():
    logging.basicConfig(datefmt="%H:%M:%S", level=logging.DEBUG,
                        format="%(asctime)s %(levelname)-7s %(name)-7s %(message)s")
    logging.getLogger('asyncio').setLevel(logging.ERROR)
    with open('app_config.json') as f:
        app_config = json.load(f)
    client_id = app_config["client_id"]
    # we probably don't need the secret for this
    # secret = app_config["secret"]

    RPC = Presence(client_id)  # Initialize the client class
    RPC.connect() # Start the handshake loop
    atexit.register(RPC.close)  # Ensure it get's closed on exit

    # Get the Funimation process
    process = get_process('funimation')  # TODO: check for none

    # There seems to be some...interesting permissions on the executable,
    # making it only spawnable by Ye Olde svchost. Will likely need to
    # open it the "canonical" way, whatever that is for UWP apps.
    # cmdline = process.cmdline()
    # logging.debug("Program cmdline: %s", ' '.join(cmdline))

    # TODO: when I make it a service, just wait around for process to respawn when it dies
    while process.is_running():
        try:
            episode_id, language = get_episode_id(process)
        except ValueError:
            logging.info("No episode playing")
        else:
            logging.info(f"Episode ID: {episode_id}\tLanguage: {language}")
            kwargs = {
                'pid': process.pid,
                'details': f"Watching episode {episode_id}",
                'state': f"Language: {language}"
            }
            kwargs.update(lookup_episode(episode_id))
            logging.debug(f"Updating presence...\n{pformat(kwargs)}")
            RPC.update(**kwargs)
        if DEBUG:
            # pprint(process.connections('all'))
            for conn in process.connections():
                unique_ips.add((conn.raddr.ip, conn.raddr.port))
            pprint(unique_ips)
        logging.debug(f"Sleeping for {UPDATE_RATE} seconds...")
        time.sleep(UPDATE_RATE)

    # print(process)
    # pprint(process.open_files())
    # pprint(process.connections('all'))
    # print(process.exe())
    # print(process.cwd())
    # print(process.cmdline())


    # Assets
    #   funimation_logo_large
    #   funimation_logo_small
    #   full_metal_panic_large
    #   full_metal_panic_small

if __name__ == '__main__':
    main()
