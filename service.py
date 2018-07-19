import os
import pathlib
import json

import servicemanager
import win32service
import win32serviceutil
import win32event


INFO = 1
WARN = 2
ERR = 3
STARTING = servicemanager.PYS_SERVICE_STARTING
STOPPING = servicemanager.PYS_SERVICE_STOPPING

# TODO: config file (JSON)
# TODO: configure logging output to go to some standard directory?


# So...wasted 45 minutes trying to get this darn thing to just start
# Turns out you need to run post-install script for pywin32
# Hopefully won't have to do this if I bundle as a exe...we'll see
# python 'C:\Program Files\Python36\Scripts\pywin32_postinstall.py' -install

# To install as automatic service: python service.py --startup=auto install
class AstolfoService(win32serviceutil.ServiceFramework):
    """Windows Service for Astolfo. Pulled from various sources:

    Chris Umbel (chrisumbel.com/article/windows_services_in_python)
    Zen_Z (codeproject.com/Articles/1115336/Using-Python-to-Make-a-Windows-Service)
    pywin32 (github.com/mhammond/pywin32/win32/Demos/service/serviceEvents.py)
            (github.com/mhammond/pywin32/win32/Lib/win32serviceutil.py#L747)
    django-windows-tools (github.com/antoinemartin/django-windows-tools)"""

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

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
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

        # Run the main logic
        self.service_main()

    # Uncomment these to implement "Pause" functionality
    # def SvcPause(self):
    #     pass
    #
    # def SvcContinue(self):
    #     pass

    # Uncomment this to implement logic that should occur at system shutdown
    # def SvcShutdown(self):
    #     pass

    def service_main(self):
        """Core logic of the service."""
        # TODO: set timeout to be more than the 15 seconds for each presence update
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
