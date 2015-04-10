#!/usr/bin/env python

import unittest
import dbox


class DropBoxTest(unittest.TestCase):
    def setUp(self):
        self.dbs = dbox.DropBoxShell()
        
    def test_parsePath(self):
        self.assertEqual(self.dbs._parsePath("/.././"), "/")
        self.assertEqual(self.dbs._parsePath("/a/b//c/"), "/a/b/c")
        self.assertEqual(self.dbs._parsePath("/a/b/../b"), "/a/b")
        self.assertEqual(self.dbs._parsePath("../a/b/../"),"/a")
        self.assertEqual(self.dbs._parsePath("/./.././a/../b/../c/."),"/c")
        
if __name__ == "__main__":
    unittest.main()