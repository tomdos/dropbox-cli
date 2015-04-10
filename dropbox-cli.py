#!/usr/bin/env python

import dropbox
import pprint
import sys

ACCESS_TOKEN="usGsZYtABmAAAAAAAAAAEKoa46Wm0f6FmcMsRChQlZ5EVlF88rMvva0KwsouAUXP"

class DropBox:
    def __init__(self, access_token = None):
        self._access_token = access_token
        self._client = None

    def setAccessToken(self, access_token):
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
        self._client = dropbox.client.DropboxClient(self._access_token)

    def _metadata(self, path):
        return self._client.metadata(path)



class DropBoxShell(DropBox):
    def __init__(self):
        self._cwd = "/"
        self._shellLoop = True

        # DropBox
        #self._dropbox = DropBox()
        #self.
        DropBox().__init__(self)

    def _dbgPrintPretty(self, data):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(data)


    def _cmdHelp(self):
        print "help\tshow this help information"
        print "ls\t..."
        print "cd\t..."


    def _cmdLs(self, path = None):
        if path == None:
            path = self._cwd
            
        metadata = self._metadata(path)
        #self._dbgPrintPretty(metadata)
        for item in metadata['contents']:
            if item['is_dir']:
                type = "d"
            else:
                type = "f"
                
            size = item['size']
            date = item['modified']
            name = item['path'].split('/')[-1]
            print("{} {}\t{}\t{}".format(type, size, date, name))


    def _cmdCd(self, command):
        pass


    def _commandParser(self, command):
        if command == None:
            return

        commandFull = command.strip()
        if commandFull == "":
            return

        command = commandFull.split()[0]

        if command == "help":
            self._cmdHelp()
        elif command == "ls":
            self._cmdLs()
        elif command == "get":
            print 'get'
        elif command == "put":
            print 'put'
        elif command == "cd":
            print 'cd'
        elif command == "exit":
            print 'exit'
            self._shellLoop = False
        else:
            print 'command not found'


    def shell(self):
        while self._shellLoop:
            sys.stdout.write("dropbox:" + self._cwd + "> ")
            command = sys.stdin.readline()
            self._commandParser(command)


def printDir(folder_metadata):
    pass

#access_token, user_id = authorize()
#print access_token + " " + user_id

#client = dropbox.client.DropboxClient(ACCESS_TOKEN)
#print 'linked account: ', client.account_info()

#folder_metadata = client.metadata('/')
#print 'folder info: ', folder_metadata
#printPretty(folder_metadata)


if __name__ == "__main__":
    #dbox = DropBox(ACCESS_TOKEN)
    #client = dbox.connect()
    dbs = DropBoxShell()
    dbs.setAccessToken(ACCESS_TOKEN)
    dbs.connect()
    dbs.shell()
