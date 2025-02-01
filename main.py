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
    date_email = datetime.strptime(date, "%b %d, %Y").date()
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
    count = 0
    while count < len(folder):
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
            count+=1

    if not len(folder):
        print("No such email")
    else:
        print_folder(folder, imap)
    imap.logout()

def print_folder(folder, imap):
    count = 0
    while count < len(folder):
        res, msg = imap.uid("fetch", folder[count], "(RFC822)")
        msg = email.message_from_bytes(msg[0][1])

        objects = dict()

        encoding_send = decode_header(msg["From"])[0][1]
        if not encoding_send is None:
            name = decode_header(msg["From"])[0][0].decode(encoding_send)
        else:
            name = decode_header(msg["From"])[0][0].split(" ")[0]

        encoding_subj = decode_header(msg["Subject"])[0][1]
        if not encoding_subj is None:
            subj = decode_header(msg["Subject"])[0][0].decode(encoding_subj)
        else:
            subj = decode_header(msg["Subject"])[0][0]

        objects["from"]=name
        objects["date"]=msg["Date"]
        objects["email"]=msg["From"].split(" ")[1].rstrip(">").lstrip("<")
        objects["subject"]=subj
        objects["message-id"]=msg["Message-ID"].lstrip("<").rstrip(">")

        print(objects)
        count+=1

if __name__ == "__main__":
    main()
