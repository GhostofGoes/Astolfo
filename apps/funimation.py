from astolfo import App


class Funimation(App):
    """The Funimation Windows 10 Microsoft Store app."""
    full_name = 'FunimationNow'
    client_id = '463903446764879892'
    process = 'Funimation.exe'

    def __init__(self, config: dict):
        super().__init__(config)
