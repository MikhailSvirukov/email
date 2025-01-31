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

def find_message_id(value, folder, msg):
    if msg["Message-ID"].lstrip("<").rstrip(">") == value:
        print("Bingo")

def find_message_email(value, folder, msg, count):
        if msg["From"].split(" ")[1].rstrip(">").lstrip("<") != value:
            folder.pop(count)
            return count+1
        return count


def find_message_sender(value, folder, msg, count):
        encoding=decode_header(msg["From"])[0][1]
        if not encoding is None:
            name = decode_header(msg["From"])[0][0].decode(encoding)
        else:
            name = decode_header(msg["From"])[0][0].split(" ")[0]
        if name != value:
            folder.pop(count)
            return count+1
        return count

def find_message_date(value, folder, msg, mark, count):
        date=msg["Date"].split(" ")
        date=date[2]+" "+date[1]+", " +date[3]
        date_email = datetime.strptime(date, "%b %d, %Y").date()
        date_value = datetime.strptime(value, "%Y-%m-%d").date()
        if mark=="from":
            if date_email < date_value:
                folder.pop(count)
                return count+1
        else:
            if date_email > date_value:
                folder.pop(count)
                return count+1
        return count


def main():
    argv=sys.argv
    imap = connect()
    if not imap:
        sys.exit()
    imap.select("INBOX")
    res, folder = imap.uid("search",  "ALL")
    folder = folder[0].decode().split(" ")
    count = 0
    check = len(folder)
    while count < len(folder):
        check=0
        res, msg = imap.uid("fetch", folder[count], "(RFC822)")
        msg = email.message_from_bytes(msg[0][1])
        for arg in argv:
            if arg[:5]=="--id=":
                find_message_id(arg[5:], folder, msg)
            elif arg[:8]=="--email=":
                if find_message_email(arg[8:], folder, msg, count)>count:
                    check=1
                    break
            elif arg[:9]=="--sender=":
                if find_message_sender(arg[9:], folder, msg, count)>count:
                    check = 1
                    break
            elif arg[:12]=="--date-from=":
                if find_message_date(arg[12:], folder, msg, "from", count)> count:
                    check = 1
                    break
            elif arg[:10]=="--date-to=":
                if find_message_date(arg[10:], folder, msg, "to", count)> count:
                    check = 1
                    break
        if check==0:
            count+=1
    print(folder)
    if not len(folder):
        print("No such email")
    imap.logout()









if __name__ == "__main__":
    main()









