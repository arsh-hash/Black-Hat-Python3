# Chapter 01 — Environment Setup

This chapter has no code files — it's purely about getting your environment
ready before touching any of the actual hacking scripts in the later chapters.
Skip this if you already have Kali + Python 3.10+ running.

---

## What You Need

| Requirement | Minimum Version |
|-------------|----------------|
| Python | 3.6+ (3.10+ recommended) |
| OS | Kali Linux (VM or bare metal) |
| Hypervisor | VMware / VirtualBox / Hyper-V |
| Windows VM | Windows 10 (needed for Ch. 09, 10, 11) |

---

## Step 1 — Get Kali Linux

Download the Kali VM image from https://www.kali.org/get-kali/  
Run it in your hypervisor of choice. Once booted, update it fully:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt dist-upgrade -y
sudo apt autoremove -y
```

---

## Step 2 — Verify Python 3

```bash
python3 --version
# Should output Python 3.x.x (3.6 minimum, 3.10+ preferred)
```

If your version is below 3.6:

```bash
sudo apt-get upgrade python3
```

---

## Step 3 — Create a Virtual Environment

A virtual environment keeps your project dependencies isolated and clean.

```bash
# Install venv if not already present
sudo apt-get install python3-venv -y

# Create your working directory
mkdir bhp && cd bhp

# Create and activate the virtual environment
python3 -m venv venv3
source venv3/bin/activate

# Your prompt will now show (venv3) — you're inside the environment
```

To deactivate later:

```bash
deactivate
```

---

## Step 4 — Install Core Dependencies

All packages used across the book's chapters:

```bash
pip install \
    requests \
    lxml \
    beautifulsoup4 \
    scapy \
    paramiko \
    cryptography \
    pywin32        # Windows only — Ch.09, 10, 11 \
    Pillow         # Ch.09 screenshots \
    volatility3    # Ch.12 memory forensics
```

Or install from the repo's requirements file:

```bash
pip install -r requirements.txt
```

---

## Step 5 — Install an IDE

The book recommends any IDE that supports Python. Good options:

- **VS Code** — `sudo apt install code` or download from https://code.visualstudio.com
- **PyCharm Community** — https://www.jetbrains.com/pycharm/download
- **Sublime Text** — lightweight, fast

VS Code setup for Python:
```bash
# Install the Python extension inside VS Code
# Ctrl+Shift+X → search "Python" → Install Microsoft's Python extension
```

---

## Step 6 — Windows VM (Optional but Recommended)

Chapters 09, 10, and 11 require a Windows environment.  
Get a free evaluation Windows 10 VM from:  
https://developer.microsoft.com/en-us/windows/downloads/virtual-machines/

---

## Code Hygiene Tips (from the book)

The book's philosophy: **make it work → make it readable → make it fast**

- Use f-strings over `.format()` or `%` formatting
- Use context managers (`with` statements) for file and socket handling
- Keep scripts short and single-purpose
- Use virtual environments — never install packages globally

---

## Quick Sanity Check

Run this after setup to confirm everything is working:

```python
import socket
import struct
import sys
import requests
from lxml import etree
import scapy.all as scapy
import paramiko

print(f"Python {sys.version}")
print("All core imports OK — you're ready to go.")
```

If it runs without errors, move on to Chapter 02.

---

## Chapter Map

| Chapter | What You'll Build |
|---------|-------------------|
| 02 | TCP/UDP clients, servers, netcat clone, TCP proxy |
| 03 | Raw socket sniffer, IP/ICMP decoder |
| 04 | Scapy — ARP poisoning, credential sniffing, pcap analysis |
| 05 | Web scraper, directory fuzzer, login brute-forcer |
| 06 | Burp Suite extensions in Python |
| 07 | GitHub-based C2 trojan framework |
| 08 | Keylogger, screenshot capture, shellcode execution |
| 09 | File encryption, email/FTP/web exfiltration |
| 10 | WMI process monitor, token privileges, code injection |
| 11 | Volatility3 memory forensics, custom plugins |
