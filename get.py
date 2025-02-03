#!/usr/bin/env python3

import functions
import email
import sys

def main():
    argv=sys.argv
    imap = functions.connect()
    if not imap:
        print("Problems with connection")
        sys.exit(1)
    imap.select("INBOX")
    res, folder = imap.uid("search",  "ALL")
    folder = folder[0].decode().split(" ")
    count=0
    check=0
    if len(argv)!=2:
        print("Message id required!")
    while count < len(folder):
        res, msg = imap.uid("fetch", folder[count], "(RFC822)")
        msg = email.message_from_bytes(msg[0][1])
        if functions.find_message_id(argv[1], folder, msg, count)==count:
            functions.save_message(folder, imap, count)
            check=1
            break
    if check==1:
        print("Found!")
    else:
        print("No such email!")
        sys.exit(1)

if __name__ == "__main__":
    main()