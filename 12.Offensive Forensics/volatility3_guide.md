# Chapter 12 — Offensive Forensics (Volatility3)

This chapter has no standalone script files — the "code" here is a custom
Volatility3 plug-in (`aslrcheck.py`) plus CLI commands run against memory
images. This guide covers everything you need to reproduce all the chapter's
results from scratch.

---

## What Is Volatility3?

Volatility3 is an open-source **memory forensics framework** written in Python 3.
It analyzes RAM snapshots (`.vmem`, `.mem`, `.raw`) pulled from running VMs or
physical machines. Defenders use it post-breach. We use it offensively to:

- Profile a target user's behavior from a VM snapshot
- Dump password hashes without touching disk
- Find processes without ASLR protection (exploit candidates)
- Discover hidden network connections and suspicious processes
- Write custom plug-ins to automate recon

---

## Installation

### Windows (PowerShell)

```powershell
# Create isolated virtual environment
python3 -m venv vol3
.\vol3\Scripts\Activate.ps1
cd vol3

# Clone and install Volatility3
git clone https://github.com/volatilityfoundation/volatility3.git
cd volatility3
python setup.py install

# Required dependency
pip install pycryptodome pefile
```

### Linux / Kali

```bash
python3 -m venv vol3
source vol3/bin/activate
cd vol3

git clone https://github.com/volatilityfoundation/volatility3.git
cd volatility3
pip install -e .
pip install pycryptodome pefile
```

### Verify Install

```bash
# Windows
vol --help

# Linux/Mac
python vol.py --help
```

---

## Getting a Memory Image to Analyze

You need a `.vmem` or `.mem` file to work with. Three ways to get one:

**1. Snapshot your own Windows VM** (easiest)
- Boot your Windows 10 VM, open notepad/calc/browser
- Take a snapshot in VMware/VirtualBox
- Find the `.vmem` file in your hypervisor's VM storage directory

**2. Download public sample images**
- PassMark (used in the book): https://www.osforensics.com/tools/volatility-workbench.html
- Volatility Foundation samples: https://github.com/volatilityfoundation/volatility/wiki/Memory-Samples

**3. Cridex malware sample** (used for the ASLR plugin demo)
- Search "Volatility cridex vmem" — widely available on forensics training sites

---

## Core Volatility3 Commands (from the book)

### System Overview
```bash
vol -f WinDev2007Eval-Snapshot4.vmem windows.info
```
Shows OS version, kernel base, processor count, system time.

### List Running Processes
```bash
# Flat list
vol -f memory.vmem windows.pslist

# With parent-child hierarchy (most useful)
vol -f memory.vmem windows.pstree

# With full command line arguments
vol -f memory.vmem windows.cmdline
```

### Dump Password Hashes
```bash
vol -f memory.vmem windows.hashdump
```
Output: username, RID, LM hash, NT hash — feed NT hashes into hashcat or john.

### Network Connections
```bash
vol -f memory.vmem windows.netscan
```
Shows all TCP/UDP connections at snapshot time including LISTENING ports.
Look for: unknown processes on unusual ports (like `nc64.exe` on 4444).

### Check Registry
```bash
# List installed services
vol -f memory.vmem windows.registry.printkey --key "ControlSet001\Services"
```

### Find Suspicious Memory Regions
```bash
# Processes with RWX memory — possible injected code
vol -f memory.vmem windows.malfind
```

### Explore Windows Plugin Directory
```bash
# See all available plugins
ls volatility/framework/plugins/windows/
```
Key plugins: `pslist`, `pstree`, `cmdline`, `hashdump`, `netscan`, `malfind`,
`dlllist`, `filescan`, `handles`, `svcscan`, `cachedump`, `lsadump`

---

## Custom Plugin — `aslrcheck.py`

Checks every process in the memory image for ASLR protection.
Non-ASLR processes are exploit candidates.

### File Structure

```
your_project/
├── plugins/
│   └── windows/
│       └── aslrcheck.py   ← put it here
└── memory.vmem
```

### Running It

```bash
# Windows
vol -p .\plugins\windows -f memory.vmem aslrcheck.AslrCheck

# Linux
python vol.py -p ./plugins/windows -f memory.vmem aslrcheck.AslrCheck
```

### What the Output Means

```
PID     Filename        Base              ASLR
368     smss.exe        0x48580000        False   ← exploit candidate
316     smss.exe        0x7ff668020000    True    ← protected
```

- `False` on Windows XP = expected (XP has no ASLR)
- `False` on Windows 10 = interesting, worth investigating
- Memory smear errors = snapshot was taken while memory was changing, try re-acquiring

---

## volshell — Interactive Python Shell

Gives you a full Python REPL with Volatility embedded:

```powershell
# -w = Windows image, -f = file
volshell -w -f memory.vmem
```

```python
# Inside volshell
>>> from volatility.plugins.windows import pslist
>>> dpo(pslist.PsList, primary=self.current_layer, nt_symbols=self.config['nt_symbols'])
```

---

## Offensive Use Cases (from the book)

| Goal | Plugin / Method |
|------|----------------|
| Profile user behavior | `windows.cmdline` + `windows.pstree` |
| Steal password hashes | `windows.hashdump` → hashcat/john |
| Find C2 / backdoors | `windows.netscan` → look for unknown listeners |
| Find injectable processes | `windows.malfind` → RWX regions |
| Find unprotected processes | Custom `aslrcheck.py` plugin |
| Enumerate installed services | `windows.registry.printkey` |
| Check loaded DLLs | `windows.dlllist` |

---

## Cracking Dumped Hashes

After `windows.hashdump`, crack NT hashes on Kali:

```bash
# John the Ripper
john --format=NT hashes.txt --wordlist=/usr/share/wordlists/rockyou.txt

# Hashcat (faster, GPU)
hashcat -m 1000 hashes.txt /usr/share/wordlists/rockyou.txt

# Pass-the-Hash (no cracking needed)
# Use the NT hash directly with CME, impacket, etc.
crackmapexec smb <target> -u Administrator -H <NT_hash>
```

---

## Requirements Summary

```bash
pip install \
    volatility3 \
    pycryptodome \
    pefile \
    pywin32        # Windows only
```

---

## Related Resources

- Volatility3 Docs: https://volatility3.readthedocs.io
- Plugin Development Guide: https://volatility3.readthedocs.io/en/latest/development.html
- Volumetric (web GUI for Volatility): https://github.com/volatilityfoundation/volumetric
- Memory Samples for Practice: https://github.com/volatilityfoundation/volatility/wiki/Memory-Samples
- Book source code: https://nostarch.com/black-hat-python2E/
