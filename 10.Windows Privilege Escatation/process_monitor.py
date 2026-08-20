import os
import sys
import win32api
import win32con
import win32security
import wmi


def log_to_file(message):
    with open('process_monitor_log.csv', 'a') as fd:
        fd.write(f'{message}\r\n')


def get_process_privileges(pid):
    """
    Given a PID, open its token and return
    all ENABLED privileges as a pipe-separated string.
    
    This is where we find gems like:
    SeDebugPrivilege    → can inject into any process
    SeLoadDriverPrivilege → can load kernel drivers
    SeTcbPrivilege      → act as part of the OS
    """
    try:
        # Get a handle to the process
        # PROCESS_QUERY_INFORMATION = we only want to read, not modify
        hproc = win32api.OpenProcess(
            win32con.PROCESS_QUERY_INFORMATION,
            False,
            pid
        )

        # Crack open the process token
        # TOKEN_QUERY = read-only access to token info
        htok = win32security.OpenProcessToken(
            hproc,
            win32con.TOKEN_QUERY
        )

        # Pull the full privilege list from the token
        # Returns list of tuples: (privilege_id, flags)
        privs = win32security.GetTokenInformation(
            htok,
            win32security.TokenPrivileges
        )

        privileges = ''
        for priv_id, flags in privs:
            # We only care about ENABLED privileges
            # A privilege can exist in a token but be disabled
            # Both bits must be set for it to be active
            if flags == (win32security.SE_PRIVILEGE_ENABLED |
                         win32security.SE_PRIVILEGE_ENABLED_BY_DEFAULT):
                
                # Convert the LUID (numeric ID) → human readable name
                # e.g. 20 → "SeDebugPrivilege"
                privileges += f'{win32security.LookupPrivilegeName(None, priv_id)}|'

    except Exception:
        # Common reasons this fails:
        # - Process died before we could query it
        # - Access denied (even as admin, some protected processes block this)
        privileges = 'N/A'

    return privileges


def monitor():
    # CSV header for our log file
    head = 'CommandLine,Time,Executable,ParentPID,PID,User,Privileges'
    log_to_file(head)

    # Instantiate WMI — this is our connection to the WMI service
    c = wmi.WMI()

    # Tell WMI we want a callback on every process CREATION event
    # This is non-destructive — we're just watching, no hooking
    process_watcher = c.Win32_Process.watch_for('creation')

    print('[*] Process monitor started. Waiting for events...\n')

    while True:
        try:
            # BLOCKING call — sits here until a new process spawns
            # then returns a Win32_Process WMI object
            new_process = process_watcher()

            # Pull everything useful off the WMI object
            cmdline     = new_process.CommandLine
            create_date = new_process.CreationDate
            executable  = new_process.ExecutablePath
            parent_pid  = new_process.ParentProcessId
            pid         = new_process.ProcessId

            # GetOwner() returns tuple: (domain, type, username)
            # e.g. ('NT AUTHORITY', 0, 'SYSTEM')
            proc_owner = new_process.GetOwner()

            # Get enabled privileges for this PID
            privileges = get_process_privileges(pid)

            process_log_message = (
                f'{cmdline} , {create_date} , {executable} , '
                f'{parent_pid} , {pid} , {proc_owner} , {privileges}'
            )

            # Highlight SYSTEM processes so they stand out
            if proc_owner and 'SYSTEM' in str(proc_owner):
                print(f'[!!!] SYSTEM PROCESS DETECTED')
                print(f'      CMD  : {cmdline}')
                print(f'      EXE  : {executable}')
                print(f'      PID  : {pid} (parent: {parent_pid})')
                print(f'      PRIVS: {privileges}')
                print()
            else:
                print(f'[+] {proc_owner[2] if proc_owner else "?"} '
                      f'→ {executable}')

            log_to_file(process_log_message)

        except Exception:
            # Process died mid-query, or WMI hiccupped — keep going
            pass


if __name__ == '__main__':
    monitor()