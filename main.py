import imaplib
import email
import sys
from email.header import decode_header
from datetime import datetime

def connect():
    mail_pass = "mry7SdQtf1fPXiMqekbi"
    username = "svmk17@mail.ru"
    imap_server = "imap.mail.ru"
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(username, mail_pass)
    return imap

def find_message_id(value, folder, msg, count):
    if msg["Message-ID"].lstrip("<").rstrip(">") == value:
        print("Bingo")

def function_factory(element):
    if element==arguments[0]:
        def find_message_email(value, folder, msg, count):
                if msg["From"].split(" ")[1].rstrip(">").lstrip("<") != value:
                    folder.pop(count)
                    return count+1
                return count
        return find_message_email

    elif element==arguments[1]:
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
        return find_message_sender

    elif element==arguments[2]:
        def find_message_date_from(value, folder, msg, count):
                date=msg["Date"].split(" ")
                date=date[2]+" "+date[1]+", " +date[3]
                date_email = datetime.strptime(date, "%b %d, %Y").date()
                date_value = datetime.strptime(value, "%Y-%m-%d").date()
                if date_email < date_value:
                    folder.pop(count)
                    return count+1
                return count
        return find_message_date_from
    elif element==arguments[3]:
        def find_message_date_to(value, folder, msg, count):
                date=msg["Date"].split(" ")
                date=date[2]+" "+date[1]+", " +date[3]
                date_email = datetime.strptime(date, "%b %d, %Y").date()
                date_value = datetime.strptime(value, "%Y-%m-%d").date()
                if date_email > date_value:
                    folder.pop(count)
                    return count+1
                return count
        return find_message_date_to

arguments = [
"--email=",
"--sender=",
"--date-from=",
"--date-to="
]

def arg_action(name, value, folder, msg, count):
    return name(value, folder, msg, count)

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
            for item in arguments:
                length=len(item)
                if arg[:length]==item:
                    if arg_action(function_factory(item), arg[length:],folder, msg, count )> count:
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
