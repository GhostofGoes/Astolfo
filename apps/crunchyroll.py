from astolfo import App


class Crunchyroll(App):
    """The Crunchyroll Windows 10 Microsoft Store app."""
    full_name = 'Crunchyroll'
    client_id = '471880598668181555'
    process = 'CR.WinApp.exe'

    def __init__(self, config: dict):
        super().__init__(config)
