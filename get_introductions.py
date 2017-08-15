# from __future__ import print_function
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import httplib2
import os
import json
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from datetime import date, timedelta

from pprint import pprint

import base64
import re

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'

def get_credentials():

    store = Storage("_tmp.json")
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    flow.user_agent = APPLICATION_NAME
    credentials = tools.run_flow(flow, store)
    return credentials

def get_email_string_recurse(parts):
    email_str = ""
    for p in parts:
        if p["mimeType"] == "text/plain":
            email_str += base64.urlsafe_b64decode(p["body"]["data"].encode('UTF-8'))
            email_str += "\n"
        elif p["mimeType"].startswith("multipart"):
            email_str += get_email_string_recurse(p["parts"])

    return email_str

def get_email_string(parts):

    email_str = get_email_string_recurse(parts)
    email_str = "--".join(email_str.split("--")[:-1])

    datetime_pattern1 = r'On \w{6,9}\W\s\w{3,8}\s\d{1,2}\W\s\d{4} at \d{1,2}:\d{1,2}:\d{1,2}\s\w{2}'
    datetime_pattern2 = r'On \w{6,9}\W\s\d{1,2}\s\w{3,8}\s\d{4}\s\d{1,2}:\d{1,2}:\d{1,2}\s\w{2}'
    datetime_pattern3 = r'On \w{3}\W\s\w{3}\s\d{1,2}\W\s\d{4} at \d{1,2}:\d{1,2}\s\w{2}'

    combo_regex = '(%s)' % ('|'.join([
        datetime_pattern1, 
        datetime_pattern2,
        datetime_pattern3
    ]),)

    p = re.search(combo_regex, email_str)
    
    if p:
        email_str = email_str.split(p.group())[0]

    return email_str



def get_introductions(service, group):
    query = 'to:(' + group + ') and subject:(introduce yourself)'

    results = service.users().threads().list(userId="me", q=query).execute()
    threads = results["threads"]

    while "nextPageToken" in results:
        page_token = results['nextPageToken']
        results = service.users().threads().list(userId="me", q=query, pageToken=page_token).execute()
        threads.extend(results['threads'])

    intros = {}

    for thread in threads:
        resp = service.users().threads().get(userId="me", id=thread["id"]).execute()
        for msg in resp["messages"]:
            emailid = None
            full_msg = service.users().messages().get(userId="me", id=msg["id"]).execute()
            for h in msg["payload"]["headers"]:
                if h["name"] == "From":
                    emailid = h["value"]
            email_str = get_email_string(full_msg["payload"]["parts"])
            # print email.message_from_string(email_str)
            print email_str
            print "\n"
            intros[emailid] = email_str
    
    print "\n"

    return intros


def main():

    tools.argparser.add_argument('--group', help='group email id')
    args = tools.argparser.parse_args()

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    group = args.group + "@nptel.iitm.ac.in"

    intros = get_introductions(service, group)
        
    with open(args.group+"-intros.csv", "wb") as f:
        f.write("Email ID, Introduction\n")
        for t in intros: 
            print_str = intros[t].strip()
            print_str = print_str.replace(",", " ")
            print_str = print_str.replace("\r\n", "<br>")
            f.write(t + "," + print_str + "\n")

    print "Done"
    

if __name__ == '__main__':
    main()  