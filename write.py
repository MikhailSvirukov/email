import smtplib
from email.message import EmailMessage

def main():
    msg = EmailMessage()
    msg['Subject'] = 'Our family reunion'
    msg['To'] = ', '.join(family)

    # Open the files in binary mode.  You can also omit the subtype
    # if you want MIMEImage to guess it.
    for file in pngfiles:
        with open(file, 'rb') as fp:
            img_data = fp.read()
        msg.add_attachment(img_data, maintype='image',
                                     subtype='png')

    # Send the email via our own SMTP server.
    with smtplib.SMTP('localhost') as s:
        s.send_message(msg)