import base64

import config
import functions
import imaplib
import email
import quopri
import sys
from email.header import decode_header
from datetime import datetime
from bs4 import BeautifulSoup
import os

def connect():
    mail_pass = config.password
    username = config.mail
    imap_server = config.server
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(username, mail_pass)
    return imap

def find_message_id(value, folder, msg, count):
    if msg["Message-ID"].lstrip("<").rstrip(">") != value:
        folder.pop(count)
        return count + 1
    return count


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

def find_message_date_from(value, folder, msg, count):
    date=msg["Date"].split(" ")
    date=date[2]+" "+date[1]+", " +date[3]
    date_email = datetime.strptime(date, "%b %d, %Y").date()
    date_value = datetime.strptime(value, "%Y-%m-%d").date()
    if date_email < date_value:
        folder.pop(count)
        return count+1
    return count

def find_message_date_to(value, folder, msg, count):
    date=msg["Date"].split(" ")
    date=date[2]+" "+date[1]+", " +date[3]
    try:
        date_email = datetime.strptime(date, "%b %d, %Y").date()
    except:
        date_email = datetime.strptime(date, "%d %b, %Y").date()
    date_value = datetime.strptime(value, "%Y-%m-%d").date()
    if date_email > date_value:
        folder.pop(count)
        return count+1
    return count


arguments = [
"--email=",
"--sender=",
"--date-from=",
"--date-to=",
    "--id="
]

list_of_functions=[
    find_message_email,
    find_message_sender,
    find_message_date_from,
    find_message_date_to,
    find_message_id
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
    count = 95
    print(len(folder))
    while count < len(folder):

        print(count)
        check=0
        res, msg = imap.uid("fetch", folder[count], "(RFC822)")
        msg = email.message_from_bytes(msg[0][1])
        for arg in argv:
            item=0
            while item<len(arguments):
                length=len(arguments[item])
                if arg[:length]==arguments[item]:
                    if arg_action(list_of_functions[item], arg[length:],folder, msg, count ) > count:
                        check = 1
                        break
                item+=1
        if check==0:
            if not functions.print_message(folder, imap, config.folder, count):
                functions.get_attachments(folder, imap, config.folder, count)
            else:
                os.chdir(config.base_dir)
            count += 1
    if not len(folder):
        print("No such email")
    imap.logout()






if __name__ == "__main__":
    main()
