#!/usr/bin/env python3

import logging
import time

from client import PresenceClient

# "Discord_UpdatePresence() has a rate limit of one update per 15 seconds"
UPDATE_RATE = 15


def main():
    logging.basicConfig(datefmt="%H:%M:%S", level=logging.DEBUG,
                        format="%(asctime)s %(levelname)-7s %(message)s")
    logging.getLogger('asyncio').setLevel(logging.ERROR)

    client_name = 'funimation'
    client = PresenceClient(client_name)

    # TODO: when I make it a service, just wait around for proc to respawn when it dies
    while client.proc.is_running():
        client.update()
        logging.debug(f"Sleeping for {UPDATE_RATE} seconds...")
        time.sleep(UPDATE_RATE)


if __name__ == '__main__':
    main()
