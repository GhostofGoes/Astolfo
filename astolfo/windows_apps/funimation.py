"""Implements the functionality for the Funimation Windows 10 app."""

from ..app import App


class Funimation(App):
    full_name = 'FunimationNow'
    client_id = '463903446764879892'
    process = 'Funimation.exe'

    def __init__(self, config: dict):
        super().__init__(config)

