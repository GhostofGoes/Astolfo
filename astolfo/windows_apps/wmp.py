"""Implements the functionality for Windows Media Player."""

from ..app import App


class Netflix(App):
    full_name = 'Windows Media Player'
    client_id = '471884051259588609'
    process = 'wmplayer.exe'

    def __init__(self, config: dict):
        super().__init__(config)
