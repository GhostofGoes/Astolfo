from astolfo import App

# Tooling/interface:
#   https://github.com/sethmlarson/virtualbox-python
#   https://pythonhosted.org/pyvbox/virtualbox/library.html
#   https://pypi.org/project/pyvbox/


class VirtualBox(App):
    """The VirtualBox Virtual Machine Manager (VMM)."""
    full_name = 'VirtualBox'
    client_id = None  # TODO
    process = 'VirtualBox.exe'

    def __init__(self, config: dict):
        super().__init__(config)

    # Strategy:
    #   Scrape Window title
    #   Search VMs for the one in the title
    #   Get: name, guest OS, and status (on/off/suspended)
    # Include: VirtualBox version
