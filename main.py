import imaplib
import email
import sys

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









if __name__ == "__main__":
    main()









