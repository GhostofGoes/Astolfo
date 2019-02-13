from astolfo import App


class VMware(App):
    """VMware Workstation.

    This includes Workstation Pro, Player, and (someday) Fusion.
    """
    full_name = 'VMware Workstation'
    client_id = None  # TODO
    process = 'vmware.exe'

    def __init__(self, config: dict):
        super().__init__(config)
