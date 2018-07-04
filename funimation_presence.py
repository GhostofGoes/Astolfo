#!/usr/bin/env python3

import atexit
import logging
import json
import time
import os.path

import pypresence
from pypresence import Presence
import psutil

# Full Metal Panic Season 2 episode 4
# \\AppData\\Local\\Packages\\FunimationProductionsLTD.FunimationNow_nat5s4eq2a0cr\\AC\\INetHistory\\mms\\HUOPOA32\\1345116_English_431a16b9-c95a-e711-8175-020165574d09[1].dat'

# Star blazers 2202 episode 6
# \\AppData\\Local\\Packages\\FunimationProductionsLTD.FunimationNow_nat5s4eq2a0cr\\AC\\INetHistory\\mms\\8R20Y2ZD\\1757485_English_4e54fc08-004f-e811-8175-020165574d09[1].dat'


def get_process(name='funimation'):
    for proc in psutil.process_iter():
        if name.lower() in proc.name().lower():
            logging.debug("Found process %s (PID: %d, Status: %s)", 
            proc.name(), proc.pid, proc.status())
            return proc
    logging.warning("Couldn't find process %s", name)


def get_episode_id(proc):
    # Returns Episode ID and Language
    open_files = proc.open_files()
    for file in open_files:
        if 'INetHistory' in file.path:
            base = os.path.basename(file.path)
            parts = base.split('_')
            return parts[0], parts[1] # Episode ID, Language
    # TODO: raise an error?
    return ()

# Full Metal Panic Episode 7: 1345122
# Full Metal Panic Episode 8: 1345124


def main():
    logging.basicConfig()
    with open('app_config.json') as f:
        app_config = json.load(f)
    client_id = app_config["client_id"]
    secret = app_config["secret"]

    RPC = Presence(client_id,pipe=0)  # Initialize the client class
    RPC.connect() # Start the handshake loop
    atexit.register(RPC.close)

    # Get the Funimation process
    process = get_process('funimation')
    # TODO: check for none

    # TODO: when I make it a service, just wait around for process to respawn when it dies

    while process.is_running():
        episode_id, language = get_episode_id(process)
        print(episode_id)
        print(language)
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
