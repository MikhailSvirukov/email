#!/usr/bin/env python3
import os
import smtplib
import sys
from argparse import ArgumentParser
from email.message import EmailMessage
import magic
import config
from email.mime.text import MIMEText


def connect():
    smtpobj = smtplib.SMTP(config.server_smtp, 587)
    smtpobj.starttls()
    smtpobj.login(config.mail, config.password)
    return smtpobj

def main():
    smtpobj = connect()
    if not smtpobj:
        print("Problems with connection")
        sys.exit(1)
    new_mes = EmailMessage()
    parser=ArgumentParser(description="Program to send email messages via SMTP protocol")
    parser.add_argument('-t', '--to',type=str, help="set email address of single receiver", metavar="")
    parser.add_argument('-g', '--group', type=str, help="set name of file, with several email addresses of receivers", metavar="")
    parser.add_argument('-s', '--source', required=True, help="set name of directory with files and message text (in 'text.txt' file)", metavar="")
    args = parser.parse_args()

    if args.group is None and args.to is None:
        print("required arguments either -t/--to or -g/--group")
        sys.exit(2)

    addresses=list()
    if not args.to is None:
        addresses.append(args.to)
    else:
        with open(args.group, "r") as f:
            addresses = f.read().splitlines()
    dir_name=config.folder_send+args.source+"/"
    files=os.listdir(dir_name)
    print(addresses)
    for file in files:
        if file!="text.txt":
            attributes=magic.Magic(mime=True).from_file(dir_name+file).split("/")
            with open(dir_name+file, 'rb') as f:
                attach = f.read()
            new_mes.add_attachment(attach, maintype=attributes[0], subtype=attributes[1], filename=file)

    with open(dir_name+"text.txt", "r") as f:
        subject=f.readline()
        new_mes.attach(MIMEText(f.read(), "plain"))
    new_mes["Subject"]=subject
    if len(addresses)>1:
        new_mes["To"]=', '.join(addresses)
    else:
        new_mes["To"] =addresses[0]
    new_mes["From"]=config.mail

    for item in addresses:
        smtpobj.sendmail(config.mail, item, new_mes.as_bytes())

if __name__ == "__main__":
    main()