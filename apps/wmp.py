from astolfo import App


class WMP(App):
    """Windows Media Player."""
    full_name = 'Windows Media Player'
    client_id = '471884051259588609'
    process = 'wmplayer.exe'

    def __init__(self, config: dict):
        super().__init__(config)
