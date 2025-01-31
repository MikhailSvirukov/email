import imaplib
import email
import sys
from email.header import decode_header
from datetime import datetime
from tabnanny import check


def connect():
    mail_pass = "mry7SdQtf1fPXiMqekbi"
    username = "svmk17@mail.ru"
    imap_server = "imap.mail.ru"
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(username, mail_pass)
    return imap

def find_message_id(value, folder, imap):
    check = 0
    for item in folder:
        res, msg = imap.uid("fetch", item, "(RFC822)")
        msg = email.message_from_bytes(msg[0][1])

        if msg["Message-ID"].lstrip("<").rstrip(">") == value:
            print("Bingo")
            check = 1
            break
    if not check:
        print("No such email")

def find_message_email(value, folder, imap):
    print(folder)
    count=0
    check=len(folder)
    while count<len(folder):
        res, msg = imap.uid("fetch", folder[count], "(RFC822)")
        msg = email.message_from_bytes(msg[0][1])
        if msg["From"].split(" ")[1].rstrip(">").lstrip("<") == value:
            count += 1
        else:
            folder.pop(count)
    if len(folder)<check:
        print("No such email")


def find_message_sender(value, folder, imap):
    count = 0
    check = len(folder)
    while count < len(folder):
        res, msg = imap.uid("fetch", folder[count], "(RFC822)")
        msg = email.message_from_bytes(msg[0][1])
        encoding=decode_header(msg["From"])[0][1]
        if not encoding is None:
            name = decode_header(msg["From"])[0][0].decode(encoding)
        else:
            name = decode_header(msg["From"])[0][0].split(" ")[0]
        if name == value:
            count+=1
        else:
            folder.pop(count)
    if  check>len(folder):
        print("No such sender")

def find_message_date(value, folder, imap, mark):
    count = 0
    while count < len(folder):
        res, msg = imap.uid("fetch", folder[count], "(RFC822)")
        msg = email.message_from_bytes(msg[0][1])
        date=msg["Date"].split(" ")
        date=date[2]+" "+date[1]+", " +date[3]
        date_email = datetime.strptime(date, "%b %d, %Y").date()
        date_value = datetime.strptime(value, "%Y-%m-%d").date()
        if mark=="from":
            if date_email >= date_value:
                count+=1
            else:
                folder.pop(count)
        else:
            if date_email <= date_value:
                count+=1
            else:
                folder.pop(count)


def main():
    argv=sys.argv
    imap = connect()
    if not imap:
        sys.exit()
    imap.select("INBOX")
    res, folder = imap.uid("search",  "ALL")
    folder = folder[0].decode().split(" ")
    for arg in argv:
        if arg[:5]=="--id=":
            find_message_id(arg[5:], folder, imap)
        elif arg[:8]=="--email=":
            find_message_email(arg[8:], folder, imap)
        elif arg[:9]=="--sender=":
            find_message_sender(arg[9:], folder, imap)
        elif arg[:12]=="--date-from=":
            find_message_date(arg[12:], folder, imap, "from")
        elif arg[:10]=="--date-to=":
            find_message_date(arg[10:], folder, imap, "to")
    imap.logout()









if __name__ == "__main__":
    main()









