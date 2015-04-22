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
    """ Wrapper of DropBox's official module. """
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


    def metadata(self, path):
        """ 
        Return path's metadata. It means everything about file/directory and
        its content.
        """
        try:
            return self._client.metadata(path)
        except dropbox.rest.ErrorResponse:
            raise

            
    def create_folder(self, path):
        """ Create folder DB side. """
        try:
            self._client.file_create_folder(path)
        except dropbox.rest.ErrorResponse:
            raise
            
    def delete(self, path):
        """ 
        Delete destination of path no mather whether it is file, empty directory 
        or directory with content.
        """
        try:
            self._client.file_delete(path)
        except dropbox.rest.ErrorRersponse:
            raise
            

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
        """ 
        Path parser will clean up path. Returned value is the shortest path 
        without additional slash(/), single dots(.) and doule dots(..).
        """
        # What to check:
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
        
    def _generic_remote_path_complete(self, text, line, begidx, endidx):
        """ Path completion - on DropBox site """
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
        completions = self.drop.metadata(dirname)
        completions = [name['path'] for name in completions['contents'] 
            if name['is_dir'] and re.search(pattern, name['path'])]
        #print completions
        
        # if last path add slash at the end
        if len(completions) == 1:
            completions = [completions[0] + os.sep]

        return completions


    def _generic_local_path_complete(self, text, line, begidx, endidx):
        """ Path completion - local file system. """
        dirname = os.path.dirname(text)
        if not dirname:
            dirname = self.cwd

        prefix = os.path.basename(text)
        if not prefix:
            prefix = '.'

        pattern = "".join(["^", prefix, ".*"])
        completions = [name+os.sep for name in os.listdir(dirname) 
            if os.path.isdir(os.path.join(dirname,name)) and re.search(pattern, name)]

        try:
            #if len(completions) == 1:
            if text:
                dirname = os.path.dirname(text)
                completions = [os.path.join(dirname,name) for name in completions]
        except:
            print sys.exc_info()

        return completions
            
    
    def do_mkdir(self, line):
        """ Create directory - similar behaviour as mkdir on linux. """
        if not line:
            print "missing operand"
            return

        # FIXME - folder with white space        
        words = line.split()            
        for dir in words:
            self.drop.create_folder(dir)
                

    def do_pwd(self, line):
        """ Print current workind directory. """
        print self.cwd


    def do_cd(self, line):
        """ Change directory """
        path = self._parse_path(line)

        try:
            metadata = self.drop.metadata(path)
            self.cwd = path
        except:
            print 'cd: ' + path + ': No such file or directory'


    def do_ls(self, line):
        """ List directory - if line parameter is missing list current direcotry. """
        if not line:
            path = self.cwd
        else:
            path = self._parse_path(line)

        metadata = self.drop.metadata(path)
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
            
            
    def do_rmrf(self, line):
        """ 
        Remove file or directory - be aware that behaviour is similar to linux
        command rm -rf. 
        """
        if not line:
            print "missing operand"
            return
            
        words = line.split()
        for file in words:
            self.drop.delete(file)


    def do_put(self, line):
        print "execute: put ", line
            
            
    def complete_put(self, text, line, begidx, endidx):
        """ 
        Completion of put command. Put will upload a file to server therefor
        two kind of paths are used. The first path is local file and the second 
        is DB.
        """
        words = line.split()
        if len(words) <= 2:
            return self._generic_local_path_complete(text, line, begidx, endidx)
        elif len(words) > 2:
            return self._generic_remote_path_complete(text, line, begidx, endidx)
        
        return None
    
    def complete_mkdir(self, text, line, begidx, endidx):
        """ Completion of mkdir command. """
        return self._generic_remote_path_complete(text, line, begidx, endidx)

    def complete_ls(self, text, line, begidx, endidx):
        """ Completion of ls command. """
        return self._generic_remote_path_complete(text, line, begidx, endidx)

    def complete_cd(self, text, line, begidx, endidx):
        """ Completion of cd command. """
        return self._generic_remote_path_complete(text, line, begidx, endidx)
        
    def complete_rmrf(self, text, line, begidx, endidx):
        """ Completion of rmrf command. """
        return self._generic_remote_path_complete(text, line, begidx, endidx)



if __name__ == "__main__":
    dbs = DropBoxShell()
    dbs.cmdloop()
