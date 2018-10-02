from pathlib import Path
import os
import json
import time
import logging.config

import servicemanager
import win32service
import win32serviceutil
import win32event
import psutil

from .astolfo import Client, get_config, CLIENTS


# Constants - DO NOT CHANGE
INFO = 1
WARN = 2
ERR = 3
STARTING = servicemanager.PYS_SERVICE_STARTING
STOPPING = servicemanager.PYS_SERVICE_STOPPING

# TODO: configure logging output to go to some standard directory?
WORKDIR = Path(__file__).resolve()
CONFIG_FILE = WORKDIR / 'config.ini'
WAIT_TIME = 5.0

# TODO: generic identification methods?
PROCS = {
    'crunchyroll': {
        'id_val': 'CR.WinApp.exe',
        'id_type': 'process',
        'alive': False,
    },
    'funimation': {
        'id_val': 'Funimation.exe',
        'id_type': 'process',
        'alive': False,
    },
    # TODO: this is incorrect, as wwahost is a host for apps, not an app
    'netflix': {
        'id_val': 'WWAHost.exe',
        'id_type': 'process',
        'alive': False,
    },
    'windows media player': {
        'id_val': 'wmplayer.exe',
        'id_type': 'process',
        'alive': False,
    },
}


def info(message: str):
    servicemanager.LogInfoMsg(str(message))


def warn(message: str):
    servicemanager.LogWarningMsg(str(message))


def error(message: str):
    servicemanager.LogErrorMsg(str(message))


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
        self.log_config = None

        self.apps = PROCS
        self.client = None
        self.client_name = None

        self.processes = {}

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

        # Load configuration
        self.config = get_config(self.config_file)

        # Configure logging
        log_output_file = self._get_path('General', 'LOG_FILE')
        log_config_file = self._get_path('General', 'LOG_CONFIG')
        self.log_config = json.loads(log_config_file.read_text())
        self.log_config['handlers']['file']['filename'] = log_output_file
        logging.config.dictConfig(self.log_config)
        if self.config.getboolean('General', 'CAPTURE_WARNINGS'):
            logging.captureWarnings(True)

        # Run the main logic
        self.service_main()

    def _get_path(self, section: str, value: str) -> Path:
        file = self.config.get(section, value)
        if os.pathsep in file:  # If they specify the path, assume it's absolute
            file = Path(file).resolve()
        else:  # Otherwise, it's relative to the WORKDIR
            file = self.dir / file
        return file

    def service_main(self):
        """Core logic of the service."""
        # TODO: set timeout to be more than the 15 seconds for each presence update
        stopped = False
        while not stopped:
            status = win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            if status == win32event.WAIT_OBJECT_0:
                stopped = True
            else:
                active = self.update_active_clients()
                # If no apps are found, wait for a few seconds then check again
                if not active:
                    time.sleep(WAIT_TIME)

    def update_active_clients(self) -> bool:
        # Update what apps are active, and which was the most recently started
        # We determine this using Process.create_time()
        self.processes = {p.name: p for p in psutil.process_iter()}
        none_alive = True
        for app_name, app in self.apps.items():
            if app['id_type'] == 'process':
                process_alive = True if app['id_val'] in self.processes else False

                # App just became active, set as current client
                if process_alive:
                    none_alive = False
                    if not app['alive']:
                        app['alive'] = True
                        self.client_name = app_name

                # App just died
                elif not process_alive and app['alive']:
                    app['alive'] = False

        # If no apps are active, return False for "inactive"
        if none_alive:
            self.client_name = None
            return False
        else:
            # If current client is dead, replace it with a live app
            if not self.apps[self.client_name]['alive']:
                for app_name, app in self.apps.items():
                    if app['alive']:
                        self.client_name = app_name
                        self.client = Client(app_name)
                        break
            return True

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
