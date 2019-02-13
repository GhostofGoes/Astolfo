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

    # Strategy:
    #   Scrape Window title
    #   Search VMs for the one in the title
    #   Get: name, guest OS, and status (on/off/suspended)
    #   https://naim94a.github.io/vix/vix.html#vix.VixVM.guest_os
    # Include: VMware version, VMware distribution (Player, Pro, etc.)
    #   Change Rich Presence client image based on the distribution
    # https://naim94a.github.io/vix/vix.html#vix.VixHost.host_info
