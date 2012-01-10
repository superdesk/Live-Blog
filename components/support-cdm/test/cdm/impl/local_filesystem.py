'''
Created on Jan 9, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Provides unit testing for the local filesystem module.
'''

import unittest
from tempfile import NamedTemporaryFile, tempdir
from os.path import join, dirname
import shutil

from cdm.impl.local_filesystem import HTTPDelivery, LocalFileSystemCDM
from ally.container import ioc


class TestHTTPDelivery(unittest.TestCase):

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testHTTPDelivery(self):
        d = HTTPDelivery()
        d.serverName = 'localhost'
        d.documentRoot = '/var/www'
        d.repositorySubdir = 'repository'
        d.port = 8080
        ioc.Initializer.initialize(d)
        self.assertEqual(d.getRepositoryPath(), '/var/www/repository',
                         'Computing the repository path')
        self.assertEqual(d.getURI('somedir/somefile.jpg'),
                         'http://localhost:8080/repository/somedir/somefile.jpg',
                         'Computing the URI')
        d.port = 80
        self.assertEqual(d.getURI('somedir/somefile.jpg'),
                         'http://localhost/repository/somedir/somefile.jpg',
                         'Computing the URI')
        d.port = None
        self.assertEqual(d.getURI('somedir/somefile.jpg'),
                         'http://localhost/repository/somedir/somefile.jpg',
                         'Computing the URI')
        d.repositorySubdir = ''
        self.assertEqual(d.getRepositoryPath(), '/var/www',
                         'Computing the repository path')
        self.assertEqual(d.getURI('somedir/somefile.jpg'),
                         'http://localhost/somedir/somefile.jpg',
                         'Computing the URI')

    def testLocalFilesystemCDM(self):
        d = HTTPDelivery()
        d.serverName = 'localhost'
        d.documentRoot = '/var/www'
        d.repositorySubdir = 'repository'
        d.port = 8080
        ioc.Initializer.initialize(d)
        cdm = LocalFileSystemCDM()
        cdm.delivery = d
        srcTmpFile = NamedTemporaryFile()
        cdm.publishFromFile(srcTmpFile.name, join(tempdir, srcTmpFile.name))
        path = 'somedir/somecontent.txt'
        cdm.publishContent(path, 'test')
        shutil.rmtree(join(d.getRepositoryPath(), dirname(path)))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
