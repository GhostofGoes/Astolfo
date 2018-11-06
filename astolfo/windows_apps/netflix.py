"""Implements the functionality for the Netflix Windows 10 app."""

from ..app import App


class Netflix(App):
    full_name = 'Netflix'
    client_id = '471883383866392596'
    # TODO: this is incorrect, as WWAHost.exe is a generic host for UWP apps
    process = 'WWAHost.exe'

    def __init__(self, config: dict):
        super().__init__(config)
