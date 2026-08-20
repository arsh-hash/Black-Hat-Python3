# save as debug_modules.py
import github3
import base64

with open('mytoken.txt') as f:
    token = f.read().strip()

sess = github3.login(token=token)
me = sess.me()
repo = sess.repository(me.login, 'bhptrojan')

print("[*] Checking GitHub repo contents...")

# Check modules folder
print("\n[*] Files in /modules:")
try:
    for f in repo.directory_contents('modules'):
        print(f"    - {f[0]}")
except Exception as e:
    print(f"    ERROR: {e}")

# Check config folder
print("\n[*] Files in /config:")
try:
    for f in repo.directory_contents('config'):
        print(f"    - {f[0]}")
except Exception as e:
    print(f"    ERROR: {e}")

# Try reading dirlister directly
print("\n[*] Trying to read dirlister.py...")
try:
    content = repo.file_contents('modules/dirlister.py')
    decoded = base64.b64decode(content.content).decode()
    print(f"    [+] SUCCESS! Content:\n{decoded}")
except Exception as e:
    print(f"    [-] FAILED: {e}")