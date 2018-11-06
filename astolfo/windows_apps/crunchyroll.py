"""Implements the functionality for the Crunchyroll Windows 10 app."""

from ..app import App


class Crunchyroll(App):
    full_name = 'Crunchyroll'
    client_id = '471880598668181555'
    process = 'CR.WinApp.exe'

    def __init__(self, config: dict):
        super().__init__(config)
