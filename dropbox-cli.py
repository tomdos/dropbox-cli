#!/usr/bin/env python

import dropbox
import pprint
import sys

ACCESS_TOKEN="usGsZYtABmAAAAAAAAAAEKoa46Wm0f6FmcMsRChQlZ5EVlF88rMvva0KwsouAUXP"

class DropBox:
    def __init__(self, access_token):
        self._access_token = access_token


    def authorize(self, app_key, app_secret):
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

        # Have the user sign in and authorize this token
        authorize_url = flow.start()
        print '1. Go to: ' + authorize_url
        print '2. Click "Allow" (you might have to log in first)'
        print '3. Copy the authorization code.'
        code = raw_input("Enter the authorization code here: ").strip()

        # This will fail if the user enters an invalid authorization code
        access_token, user_id = flow.finish(code)

        return (access_token, user_id)


    def connect(self):
        client = dropbox.client.DropboxClient(self._access_token)
        return client



def printPretty(data):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)


def printDir(folder_metadata):
    pass


def processCommand(command):
    switch comma

#access_token, user_id = authorize()
#print access_token + " " + user_id

#client = dropbox.client.DropboxClient(ACCESS_TOKEN)
#print 'linked account: ', client.account_info()

#folder_metadata = client.metadata('/')
#print 'folder info: ', folder_metadata
#printPretty(folder_metadata)


def shell():
    while True:
        sys.stdout.write("dropbox> ")
        command = sys.stdin.readline()
        processCommand(command)


if __name__ == "__main__":
    #dbox = DropBox(ACCESS_TOKEN)
    #client = dbox.connect()
    shell()
