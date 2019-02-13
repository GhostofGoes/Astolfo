from astolfo import App

# Tooling/interface:
#   https://wiki.videolan.org/PythonBinding
#   https://www.olivieraubert.net/vlc/python-ctypes/doc/
#   https://pypi.org/project/python-vlc/


class VLC(App):
    """The VLC media player."""
    full_name = 'VLC'
    client_id = None  # TODO
    process = 'vlc.exe'

    def __init__(self, config: dict):
        super().__init__(config)
