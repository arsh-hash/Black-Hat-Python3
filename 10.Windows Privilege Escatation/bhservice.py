import os
import servicemanager
import shutil
import subprocess
import sys
import win32event
import win32service
import win32serviceutil

# WHERE the original vbs script lives (your working dir)
SRCDIR = f'C:\\Users\\Downloads\\ch10'

# WHERE the service will copy + execute it from
TGTDIR = 'C:\\Windows\\TEMP'


class BHServerSvc(win32serviceutil.ServiceFramework):
    # These three define how Windows sees the service
    _svc_name_         = "BlackHatService"
    _svc_display_name_ = "Black Hat Service"
    _svc_description_  = ("Executes VBScripts at regular intervals."
                           " What could possibly go wrong?")

    def __init__(self, args):
        # Full path of the script in the TEMP directory
        self.vbs     = os.path.join(TGTDIR, 'bhservice_task.vbs')

        # 1000ms * 60 = 60 seconds between each execution
        self.timeout = 1000 * 60

        win32serviceutil.ServiceFramework.__init__(self, args)

        # Event object — used to signal the service to stop cleanly
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        # Tell SCM we're stopping, then fire the stop event
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        # Tell SCM we're running, jump into main loop
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.main()

    def main(self):
        while True:
            # Block here for self.timeout ms OR until stop signal
            # whichever comes first
            ret_code = win32event.WaitForSingleObject(
                self.hWaitStop,
                self.timeout
            )

            # If stop signal fired — log it and break the loop
            if ret_code == win32event.WAIT_OBJECT_0:
                servicemanager.LogInfoMsg("Service is stopping")
                break

            # Copy the vbs from SRCDIR → TGTDIR (C:\Windows\TEMP)
            src = os.path.join(SRCDIR, 'bhservice_task.vbs')
            shutil.copy(src, self.vbs)

            # Execute the script as SYSTEM (because service runs as SYSTEM)
            # shell=False means no cmd.exe wrapper — direct execution
            subprocess.call(f'cscript.exe {self.vbs}', shell=False)

            # Delete the file immediately after execution
            # This is the race condition window we'll exploit later
            os.unlink(self.vbs)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # No args = being started by Windows SCM
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(BHServerSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Args present = manual install/start/stop/remove commands
        win32serviceutil.HandleCommandLine(BHServerSvc)