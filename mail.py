#!/usr/bin/env python3
"""
Quick IMAP fetcher for Zimbra (Univ-Lille)
------------------------------------------
• Authenticates over SSL (port 993)
• Lists the 10 newest messages in INBOX
"""

import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv
import re

# ---------- 1. Load credentials ----------
load_dotenv()                                      # reads .env in the same dir
IMAP_HOST = "zimbra.univ-lille.fr"
IMAP_PORT = 993

creds = dict(re.findall(r"^(\w+)=([^\n]+)", open(
    "/home/bastien/Downloads/secret_creds/creds.txt").read(), re.M))
USER, PASSWORD = creds["ULILLE_USER"], creds["ULILLE_PASS"]


SEARCH_SENDER = "aghiles.hamroun@chu-lille.fr"

def decode_subject(raw_subject):
    parts = decode_header(raw_subject or "")
    return "".join(
        frag.decode(cs or "utf-8") if isinstance(frag, bytes) else frag
        for frag, cs in parts
    )

with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as imap:
    imap.login(USER, PASSWORD)
    imap.select("INBOX", readonly=True)

    # ---- SEARCH ----
    # Quoting matters:  FROM "sender@example.com"
    status, data = imap.search(None, 'FROM', f'"{SEARCH_SENDER}"')
    if status != "OK":
        raise RuntimeError("IMAP search failed")

    uids = data[0].split()
    print(f"Found {len(uids)} messages from {SEARCH_SENDER}\n")

    for uid in uids:                               # chronological order; reverse() if you prefer newest first
        status, msg_data = imap.fetch(uid, "(RFC822.HEADER)")
        if status != "OK":
            print(f"Could not fetch UID {uid.decode()}")
            continue

        msg = email.message_from_bytes(msg_data[0][1])
        subject = decode_subject(msg.get("Subject"))
        date    = msg.get("Date", "(no date)")
        print(f"[{date}]  {subject}")

    imap.logout()