"""Implements the functionality for VMware Workstation.
This includes Workstation Pro, Player, and (someday) Fusion."""

from ..app import App


class VMware(App):
    full_name = 'VMware Workstation'
    client_id = None  # TODO
    process = 'vmware.exe'

    def __init__(self, config: dict):
        super().__init__(config)
