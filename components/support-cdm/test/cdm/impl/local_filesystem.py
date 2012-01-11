'''
Created on Jan 9, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Provides unit testing for the local filesystem module.
'''

import unittest
from tempfile import NamedTemporaryFile, TemporaryDirectory
from os.path import join, dirname, isfile
from shutil import rmtree
from cdm.impl.local_filesystem import HTTPDelivery, LocalFileSystemCDM
from ally.container import ioc
from io import StringIO
from os import makedirs


class TestHTTPDelivery(unittest.TestCase):

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
        try:
            cdm.publishFromFile(srcTmpFile.name, srcTmpFile.name)
            dstFilePath = join(d.getRepositoryPath(), srcTmpFile.name.lstrip('/'))
            self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(dirname(dstFilePath))
        srcTmpDir = TemporaryDirectory()
        dirs = (join(srcTmpDir.name, 'test1/subdir1'), join(srcTmpDir.name, 'test2/subdir1'))
        for dir in dirs:
            makedirs(dir)
            f = open(join(dir, 'text.html'), 'w+')
            f.close()
        try:
            cdm.publishFromDir('tmp', srcTmpDir.name)
            dstDirPath = join(d.getRepositoryPath(), 'tmp')
            for dir in dirs:
                dstFilePath = join(dstDirPath, dir, 'text.html')
                self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(dstDirPath)
        try:
            path = join('somedir', 'somecontent.txt')
            cdm.publishContent(path, 'test')
            dstFilePath = join(d.getRepositoryPath(), path)
            self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(join(d.getRepositoryPath(), dirname(path)))
        try:
            path = join('somedir2', 'somecontent2.txt')
            ioStream = StringIO('test 2')
            cdm.publishFromStream(path, ioStream)
            dstFilePath = join(d.getRepositoryPath(), path)
            self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(join(d.getRepositoryPath(), dirname(path)))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
