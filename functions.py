import base64
import imaplib
import email
import quopri
import sys
from email.header import decode_header
from datetime import datetime
from bs4 import BeautifulSoup
import os

import config


def letter_type(part):
    if part["Content-Transfer-Encoding"] == "base64":
        encoding = part.get_content_charset()
        return base64.b64decode(part.get_payload()).decode(encoding)
    elif part["Content-Transfer-Encoding"] == "quoted-printable":
        encoding = part.get_content_charset()
        return quopri.decodestring(part.get_payload()).decode(encoding)
    else:
        return part.get_payload()

def get_letter_text_from_html(body):
    body = body.replace("<div><div>", "<div>").replace("</div></div>", "</div>")
    try:
        soup = BeautifulSoup(body, "html.parser")
        paragraphs = soup.find_all("div")
        text = ""
        for paragraph in paragraphs:
            text += paragraph.text
        return text
    except (Exception) as exp:
        print("text ftom html err ", exp)
        return False

def get_letter_text(msg):
    if msg.is_multipart():
        for part in msg.walk():
            count = 0
            if part.get_content_maintype() == "text" and count == 0:
                extract_part = letter_type(part)
                if part.get_content_subtype() == "html":
                    letter_text = get_letter_text_from_html(extract_part)
                else:
                    letter_text = extract_part
                count += 1
                return (
                    letter_text.replace("<", "").replace(">", "").replace("\xa0", " ")
                )
    else:
        count = 0
        if msg.get_content_maintype() == "text" and count == 0:
            extract_part = letter_type(msg)
            if msg.get_content_subtype() == "html":
                letter_text = get_letter_text_from_html(extract_part)
            else:
                letter_text = extract_part
            count += 1
            return letter_text.replace("<", "").replace(">", "").replace("\xa0", " ")

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

#works only with list with single element
def print_message(folder, imap, folder_save, count):
    res, msg = imap.uid("fetch", folder[count], "(RFC822)")
    msg = email.message_from_bytes(msg[0][1])
    try:
        dir_name = msg["From"].split(" ")[1].rstrip(">").lstrip("<") + msg["Date"].replace(" ", "")
    except:
        dir_name = msg["From"].split(" ")[0].rstrip(">").lstrip("<") + msg["Date"].replace(" ", "")

    if not os.path.isdir(folder_save + dir_name):
        os.mkdir(folder_save + dir_name)
    else:
        return 1
    os.chdir(folder_save + dir_name)
    subj=" "
    if msg["Subject"] is not None:
        encoding_subj = decode_header(msg["Subject"])[0][1]
        if not encoding_subj is None:
            if encoding_subj  in ("unknown-8bit"):
                subj = decode_header(msg["Subject"])[0][0].decode("8bit")
            else:
                subj = decode_header(msg["Subject"])[0][0].decode(encoding_subj)
        else:
            subj = decode_header(msg["Subject"])[0][0]
    with open("text.txt", 'w') as f:
        f.write("Тема: "+subj)
        if get_letter_text(msg) is not None:
            f.write(get_letter_text(msg))
    return 0



def get_attachments(folder, imap, folder_save, count):
    res, msg = imap.uid("fetch", folder[count], "(RFC822)")
    msg = email.message_from_bytes(msg[0][1])
    for part in msg.walk():
        if part.get_content_disposition() == 'attachment':
            encoding=decode_header(part.get_filename())[0][1]
            if encoding is not None:
                with open(decode_header(part.get_filename())[0][0].decode(encoding), 'wb') as f:
                    f.write(part.get_payload(decode=True))
            else:
                with open(decode_header(part.get_filename())[0][0], 'wb') as f:
                    f.write(part.get_payload(decode=True))
    os.chdir(config.base_dir)
