#!/usr/bin/env python

import dropbox
import pprint
import sys
import os
import re
import readline
import rlcompleter
import cmd

ACCESS_TOKEN="usGsZYtABmAAAAAAAAAAEKoa46Wm0f6FmcMsRChQlZ5EVlF88rMvva0KwsouAUXP"

class DropBoxHelper:
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
        try:
            return self._client.metadata(path)
        except dropbox.rest.ErrorResponse:
            raise


    def _createFolder(self, path):
        try:
            return self._client.file_create_folder(path)
        except:
            raise




# class DropBoxShell_(DropBox):
#     def __init__(self):
#         self._cwd = "/"
#         self._shellLoop = True
#
#         # DropBox
#         #self._dropbox = DropBox()
#         #self.
#         DropBox().__init__(self)
#
#     def _dbgPrintPretty(self, data):
#         pp = pprint.PrettyPrinter(indent=4)
#         pp.pprint(data)
#
#
#     def _cmdHelp(self):
#         print "help\tshow this help information"
#         print "ls\t..."
#         print "cd\t..."
#
#
#     def _cmdLs(self, path = None):
#         if path == None:
#             path = self._cwd
#
#         metadata = self._metadata(path)
#         #self._dbgPrintPretty(metadata)
#         for item in metadata['contents']:
#             if item['is_dir']:
#                 type = "d"
#             else:
#                 type = "f"
#
#             size = item['size']
#             date = item['modified']
#             name = item['path'].split('/')[-1]
#             print("{} {}\t{}\t{}".format(type, size, date, name))
#
#     def _parsePath(self, path):
#         """ Path parser - should work same as in linux shell """
#         # /dir
#         # dir
#         # ..
#         # ../dir
#         # /./
#         # /dirA/../dirB
#
#         # relative path - add curret cwd
#         if path[0] != '/':
#             path = self._cwd + '/' + path
#
#         pathSplit = path.split('/')
#         newPath = '/'
#         for directory in pathSplit:
#             # empty item means multiple slashes '///'
#             if not directory:
#                 continue
#
#             # current direcctory
#             if directory == '.':
#                 continue
#
#             # go back - test for root dir
#             if directory == '..':
#                 newPath = re.sub(r'/[^/]*/$','/', newPath)
#                 if not newPath:
#                     newPath = '/'
#
#                 continue
#
#             # directories
#             newPath = newPath + directory + '/'
#
#         # if last character is shash remove it
#         if len(newPath) > 1 and newPath[-1] == '/':
#             newPath = newPath[:-1]
#
#         return newPath
#
#
#     def _cmdCd(self, path = '/'):
#         path = self._parsePath(path)
#         try:
#             metadata = self._metadata(path)
#             self._cwd = path
#         except:
#             print 'cd: ' + path + ': No such file or directory'
#
#     def _cmdMkdir(self, path):
#         path = self._parsePath(path)
#         try:
#             metadata = self._createFolder(path)
#         except:
#             print 'Can\'t create folder: ' + path
#
#
#     def _commandParser(self, command):
#         if command == None:
#             return
#
#         commandFull = command.strip().split()
#         if commandFull == False:
#             return
#
#         command = commandFull[0]
#
#         if command == "help":
#             self._cmdHelp()
#         elif command == "ls":
#             self._cmdLs()
#         elif command == "get":
#             print 'get'
#         elif command == "put":
#             print 'put'
#         elif command == "cd":
#             if len(commandFull) > 1:
#                 self._cmdCd(commandFull[1])
#             else:
#                 self._cmdCd()
#
#         elif command == "exit":
#             print 'exit'
#             self._shellLoop = False
#         elif command == "mkdir":
#             if len(commandFull) > 1:
#                 self._cmdMkdir(commandFull[1])
#             else:
#                 print "mkdir: missing operand"
#         else:
#             print 'command not found'
#
#
#     def shell(self):
#         while self._shellLoop:
#             sys.stdout.write("dropbox:" + self._cwd + "> ")
#             command = sys.stdin.readline()
#             self._commandParser(command)
#

class DropBoxShell(cmd.Cmd):
    def __init__(self):
        self.cwd = "/"
        self.drop = DropBoxHelper()
        self.drop.setAccessToken(ACCESS_TOKEN)
        self.drop.connect()


        # Change behavior for OSX which implement libedit
        if "libedit" in readline.__doc__:
            readline.parse_and_bind("bind '\t' rl_complete")
        else:
            readline.parse_and_bind('tab: complete')
        
        readline.set_completer_delims(' \t\n;')
        
        cmd.Cmd.__init__(self)


    def _parse_path(self, path):
        """ Path parser - should work same as in linux shell """
        # /dir
        # dir
        # ..
        # ../dir
        # /./
        # /dirA/../dirB

        # relative path - add curret cwd
        if path[0] != '/':
            path = self.cwd + '/' + path

        pathSplit = path.split('/')
        newPath = '/'
        for directory in pathSplit:
            # empty item means multiple slashes '///'
            if not directory:
                continue

            # current direcctory
            if directory == '.':
                continue

            # go back - test for root dir
            if directory == '..':
                newPath = re.sub(r'/[^/]*/$','/', newPath)
                if not newPath:
                    newPath = '/'

                continue

            # directories
            newPath = newPath + directory + '/'

        # if last character is shash remove it
        if len(newPath) > 1 and newPath[-1] == '/':
            newPath = newPath[:-1]

        return newPath
        
    def _generic_path_complete(self, text, line, begidx, endidx):
        dirname = os.path.dirname(text)
        if not dirname:
            dirname = self.cwd

        prefix = os.path.basename(text)
        if not prefix:
            prefix = '.'

        filter_path = self._parse_path(dirname+"/"+prefix)
        pattern = "".join(["^", filter_path, ".*"])
        #print "*",dirname," ",prefix," ", filter_path, "*"

        dirname = self._parse_path(dirname)
        completions = self.drop._metadata(dirname)
        completions = [name['path'] for name in completions['contents'] if name['is_dir'] and re.search(pattern, name['path'])]
        #print completions
        
        # if last path add slash at the end
        if len(completions) == 1:
            completions = [completions[0] + os.sep]

        return completions
            
            
    def do_mkdir(self, line):
        pass
                

    def do_pwd(self, line):
        print self.cwd


    def do_cd(self, line):
        path = self._parse_path(line)

        try:
            metadata = self.drop._metadata(path)
            self.cwd = path
        except:
            print 'cd: ' + path + ': No such file or directory'


    def do_ls(self, line):
        if not line:
            path = self.cwd
        else:
            path = self._parse_path(line)

        metadata = self.drop._metadata(path)
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
            

    def complete_mkdir(self, text, line, begidx, endidx):
        return self._generic_path_complete(text, line, begidx, endidx)

    def complete_ls(self, text, line, begidx, endidx):
        return self._generic_path_complete(text, line, begidx, endidx)

    def complete_cd(self, text, line, begidx, endidx):
        return self._generic_path_complete(text, line, begidx, endidx)



if __name__ == "__main__":
    dbs = DropBoxShell()
    dbs.cmdloop()
