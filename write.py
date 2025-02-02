import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path
import magic
import config
from email.mime.text import MIMEText


def main():
    smtpObj = smtplib.SMTP('smtp.mail.ru', 587)
    smtpObj.starttls()
    smtpObj.login(config.mail, config.password)
    new_mes = EmailMessage()
    source=None
    group=None
    to=None
    argv=sys.argv
    if len(argv)!=3:
        print("Invalid argument list!")
        sys.exit(2)
    for arg in argv:
        if arg[:5]=="--to=":
            to=arg[5:]
        elif arg[:8]=="--group=":
            group=arg[8:]
        elif arg[:9]=="--source=":
            source=arg[9:]
    if source is None or (group is None and to is None):
        print("Invalid arguments list!")
        sys.exit(2)

    addresses=list()
    if not to is None:
        addresses.append(to)
    else:
        with open(group, "r") as f:
            mail = f.readline()
            while mail is not None:
                addresses.append(mail)
                mail=f.readline()
    dir_name=config.folder_send+source+"/"
    files=os.listdir(dir_name)

    for file in files:

        if file!="text.txt":
            attributes=magic.Magic(mime=True).from_file(dir_name+file).split("/")
            with open(dir_name+file, 'rb') as fp:
                attach = fp.read()
            new_mes.add_attachment(attach, maintype=attributes[0], subtype=attributes[1])
    with open(dir_name+"text.txt", "r") as f:
        subject=f.readline()
        new_mes.attach(MIMEText(f.read(), "plain"))
    new_mes["Subject"]=subject
    if len(addresses)>1:
        new_mes["To"]=', '.join(addresses)
    else:
        new_mes["To"] =addresses[0]
    print(new_mes["To"])
    new_mes["From"]=config.mail

    smtpObj.sendmail("svmk17@mail.ru", to, new_mes.as_bytes())

if __name__ == "__main__":
    main()