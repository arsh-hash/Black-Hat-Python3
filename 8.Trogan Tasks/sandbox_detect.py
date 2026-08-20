"""
Black Hat Python - Chapter 8
Sandbox Detection using ctypes and win32api

HOW IT WORKS:
-------------
Sandboxes are automated — no real human uses them.
This script detects sandbox environments by checking:
1. How long since the last user input (idle time)
2. Number of real mouse clicks
3. Number of real keystrokes
4. Number of double-clicks
5. Whether double-clicks are happening suspiciously fast (fake input)

If it smells like a sandbox — it exits silently.
If it detects enough real human activity — it returns True (safe to proceed).

Requirements:
    pip install pywin32

Run:
    python sandbox_detect.py
"""

from ctypes import byref, c_uint, c_ulong, sizeof, Structure, windll

import random
import sys
import time
import win32api


# ---------------------------------------------------------------
# Windows API Structure to get last input timestamp
# Must match the Windows LASTINPUTINFO struct exactly
# ---------------------------------------------------------------
class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),   # size of this structure in bytes
        ('dwTime', c_ulong)   # tick count of when last input occurred
    ]


def get_last_input():
    """
    Returns how many milliseconds have passed since the last
    mouse or keyboard input on the system.

    Logic:
    - GetLastInputInfo fills dwTime with the tick of last input
    - GetTickCount returns total ticks since system boot
    - Difference = idle time in milliseconds

    Why this matters:
    A real machine has a user actively using it.
    A sandbox just booted and has no real user — so idle time is huge.
    """
    struct_lastinputinfo = LASTINPUTINFO()

    # cbSize MUST be initialized before passing to Windows API
    struct_lastinputinfo.cbSize = sizeof(LASTINPUTINFO)

    # Windows fills in dwTime with timestamp of last input event
    windll.user32.GetLastInputInfo(byref(struct_lastinputinfo))

    # Total milliseconds the system has been running
    run_time = windll.kernel32.GetTickCount()

    # How long since last input
    elapsed = run_time - struct_lastinputinfo.dwTime

    print(f'[*] It has been {elapsed} milliseconds since last input.')
    return elapsed


# ---------------------------------------------------------------
# Main Detector Class
# ---------------------------------------------------------------
class Detector:
    def __init__(self):
        self.double_clicks = 0   # counts double-click events
        self.keystrokes    = 0   # counts keyboard keypresses
        self.mouse_clicks  = 0   # counts single mouse clicks

    def get_key_press(self):
        """
        Scans all 255 virtual key codes to check if any key
        or mouse button was pressed since the last call.

        Returns:
        - timestamp (float) if left mouse button was clicked
        - None for keyboard presses or no input detected

        Why scan all keys?
        GetAsyncKeyState checks the state of a specific key.
        We loop through all possible keys to catch anything.
        The 0x0001 bit means "was this key pressed since last check".
        """
        for i in range(0, 0xff):
            state = win32api.GetAsyncKeyState(i)

            if state & 0x0001:  # key was pressed since last call

                if i == 0x1:
                    # 0x1 = left mouse button click
                    self.mouse_clicks += 1
                    return time.time()  # return timestamp for double-click detection

                elif i > 32 and i < 127:
                    # Printable ASCII range = real keyboard character typed
                    self.keystrokes += 1

        return None  # no relevant input detected

    def detect(self):
        """
        Main sandbox detection loop.

        Strategy:
        1. Check idle time first — if too long, exit (sandbox indicator)
        2. Monitor mouse clicks, keystrokes, double-clicks
        3. Use RANDOMIZED thresholds so sandbox can't predict and fake them
        4. Check if double-clicks are happening unnaturally fast (fake input)
        5. Only return True when enough REAL human activity is detected
        """
        previous_timestamp  = None
        first_double_click  = None

        # A real human double-click happens within ~0.35 seconds
        double_click_threshold = 0.35

        # Randomized targets — sandbox can't hardcode exact values to fake
        max_double_clicks   = 10
        max_keystrokes      = random.randint(10, 25)
        max_mouse_clicks    = random.randint(5, 25)
        max_input_threshold = 30000  # 30 seconds idle = likely sandbox

        # --- Check 1: Idle time ---
        # If the machine has had no input for 30+ seconds, suspicious
        last_input = get_last_input()
        if last_input >= max_input_threshold:
            print('[!] No recent input detected. Looks like a sandbox. Exiting.')
            sys.exit(0)

        print(f'[*] Targets -> Keystrokes: {max_keystrokes} | '
              f'Mouse clicks: {max_mouse_clicks} | '
              f'Double clicks: {max_double_clicks}')
        print('[*] Waiting for human activity...\n')

        detection_complete = False

        while not detection_complete:
            keypress_time = self.get_key_press()

            if keypress_time is not None and previous_timestamp is not None:

                # Calculate time between this click and previous click
                elapsed = keypress_time - previous_timestamp

                # --- Check 2: Double-click detection ---
                if elapsed <= double_click_threshold:
                    # Two clicks within 0.35s = double-click
                    self.mouse_clicks  -= 2   # remove the 2 individual clicks
                    self.double_clicks += 1   # count as one double-click

                    if first_double_click is None:
                        first_double_click = time.time()  # record first double-click time
                    else:
                        # --- Check 3: Suspiciously rapid double-clicks ---
                        # A sandbox might spam fake double-clicks very fast
                        # Real humans can't do 10 double-clicks that quickly
                        if self.double_clicks >= max_double_clicks:
                            if (keypress_time - first_double_click) <= \
                               (max_double_clicks * double_click_threshold):
                                print('[!] Rapid double-clicks detected. Looks like a sandbox. Exiting.')
                                sys.exit(0)

            # --- Check 4: Have we seen enough real human activity? ---
            if (self.keystrokes  >= max_keystrokes  and
                self.double_clicks >= max_double_clicks and
                self.mouse_clicks >= max_mouse_clicks):
                detection_complete = True

            # Update timestamp for next iteration
            if keypress_time is not None:
                previous_timestamp = keypress_time

        return True


# ---------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------
if __name__ == '__main__':
    d = Detector()
    result = d.detect()

    if result:
        print('\n[+] Real human activity detected. Not a sandbox.')
        print('[+] Safe to proceed with payload.')
    else:
        print('\n[!] Sandbox detected. Exiting.')
        sys.exit(0)