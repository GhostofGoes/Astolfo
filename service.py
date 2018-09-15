from pathlib import Path

import servicemanager
import win32service
import win32serviceutil
import win32event

from .astolfo import Client, get_config


# Constants - DO NOT CHANGE
INFO = 1
WARN = 2
ERR = 3
STARTING = servicemanager.PYS_SERVICE_STARTING
STOPPING = servicemanager.PYS_SERVICE_STOPPING

# TODO: configure logging output to go to some standard directory?
WORKDIR = Path(__file__).absolute()
CONFIG_FILE = WORKDIR / 'config.ini'


def info(message: str):
    servicemanager.LogInfoMsg(str(message))


def warn(message: str):
    servicemanager.LogWarningMsg(str(message))


def error(message: str):
    servicemanager.LogErrorMsg(str(message))


def get_config(file=CONFIG_FILE):
    if not file.is_file():
        error(f"Could not find configuration file {file}!")


class AstolfoService(win32serviceutil.ServiceFramework):
    """Windows Service for Astolfo.

    To install as automatic service: `python service.py --startup=auto install`"""

    # Name of the service (Use with `net` command, e.g. `net start Astolfo`)
    _svc_name_ = "Astolfo"

    # Service name in the Service Control Manager (SCM)
    _svc_display_name_ = "Astolfo (Discord Rich Presence for Windows 10 Apps)"

    # Description in the SCM
    _svc_description_ = "Discord Rich Presence (status updates) for " \
                        "Windows 10 Microsoft Store apps, such as " \
                        "Crunchyroll, Funimation, or Netflix."

    # _exe_args_ = None  # Default to no arguments
    # _svc_deps_ = None  # Sequence of service names on which this depends

    _config_filename = 'config.ini'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.dir = Path(__file__).resolve().parent()
        self.config_file = self.dir / self._config_filename
        self.config = None

        # Create an event to listen for stop requests on
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        """Called when we're being shut down."""
        # Tell the SCM we're shutting down
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.log_state(servicemanager.PYS_SERVICE_STOPPING)
        win32event.SetEvent(self.stop_event)  # Fire the stop event
        self.log_state(servicemanager.PYS_SERVICE_STOPPED)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.log_state(servicemanager.PYS_SERVICE_STARTING)
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.log_state(servicemanager.PYS_SERVICE_STARTED)
        self.log(f"Working directory is {self.dir}.\n"
                 f"Configuration file is {self._config_filename}")
        self.config = get_config(self.config_file)

        # Run the main logic
        self.service_main()

    def service_main(self):
        """Core logic of the service."""
        # TODO: set timeout to be more than the 15 seconds for each presence update
        # self.client = Client()
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
        # while rc != win32event.WAIT_OBJECT_0:
        #     # block for 5 seconds and listen for a stop event
        #     rc = win32event.WaitForSingleObject(self.stop_event, 5000)

    def log_state(self, state: int):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              state, (self._svc_name_, ""))

    @staticmethod
    def log(message: str, msg_type: int = INFO):
        """Log a message to the Windows Event Log."""
        if msg_type == INFO:
            servicemanager.LogInfoMsg(str(message))
        if msg_type == WARN:
            servicemanager.LogWarningMsg(str(message))
        elif msg_type == ERR:
            servicemanager.LogErrorMsg(str(message))
        else:
            servicemanager.LogMsg(str(message))


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AstolfoService)
