
from __future__ import print_function
import httplib2
import os
import json
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from datetime import date, timedelta

from tabulate import tabulate

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

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

def get_unanswered_count(service, group, start_date=None, end_date=None):
    query = 'to:(' + group + ')'
        
    if start_date is not None:
        query = query + ' after:'+start_date

    if end_date is not None:
        query = query + ' before:'+end_date

    results = service.users().threads().list(userId="me", q=query).execute()
    threads = results["threads"]

    while "nextPageToken" in results:
        page_token = results['nextPageToken']
        results = service.users().threads().list(userId="me", q=query, pageToken=page_token).execute()
        threads.extend(results['threads'])

    unanswered_count = 0
    thread_count = len(threads)

    for thread in threads:
        resp = service.users().threads().get(userId="me", id=thread["id"]).execute()
        if len((resp["messages"])) == 1:
            unanswered_count += 1

    return (unanswered_count, thread_count)

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    SUFFIX = "@nptel.iitm.ac.in"

    with open("groups.txt", "rb") as f:
        groups = f.read().strip().split("\n")

    counts_local = []
    ratios = []
    counts_global = []

    today = date.today()
    yesterday = today.replace(day=today.day-1)

    for g in groups:
        g_counts = get_unanswered_count(service, g + SUFFIX)
        counts_global.append(g_counts)
        g_counts = get_unanswered_count(service, g + SUFFIX, str(yesterday), str(today))
        counts_local.append(g_counts)
        ratios.append(float(g_counts[0])/float(g_counts[1]))

    x = zip(groups, counts_local, ratios, counts_global)
    x = sorted(x, key=lambda p: p[2], reverse=True)
    groups = [g for (g,_,_,_) in x]
    counts_local = [c for (_,c,_,_) in x]
    ratios = [r for (_,_,r,_) in x]
    counts_global = [c for (_,_,_,c) in x]

    table = zip(groups, [str(c[0]) for c in counts_local], [str(c[1]) for c in counts_local], [str(c[0]) for c in counts_global], [str(c[1]) for c in counts_global])
    headings = ["Group Name", "Unanswered Yesterday", "Total New Yesterday", "Unanswered Since Start", "Total Since Start"]

    with open("table.csv", "wb") as f:
        f.write(",".join(headings)+"\n")
        for t in table: 
            f.write(",".join(t)+"\n")

    print (tabulate(table, headers=headings) + "\n")
    

if __name__ == '__main__':
    main()  