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
from cdm.impl.local_filesystem import HTTPDelivery, LocalFileSystemCDM, LocalFileSystemLinkCDM
from ally.container import ioc
from io import StringIO
from os import makedirs, remove, sep


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
        rootDir = TemporaryDirectory()
        d.documentRoot = rootDir.name
#        d.documentRoot = '/var/www'
        d.repositorySubdir = 'repository'
        d.port = 8080
#        ioc.Initializer.initialize(d)
        cdm = LocalFileSystemCDM()
        cdm.delivery = d

        # test publish from a file from the file system
        try:
            srcTmpFile = NamedTemporaryFile()
            dstFile = join('testdir1', 'tempfile.txt')
            cdm.publishFromFile(dstFile, srcTmpFile.name)
            dstFilePath = join(d.getRepositoryPath(), dstFile)
            self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(dirname(dstFilePath))

        # test publish from a file from a zip archive
        try:
            inFileName = join('dir1', 'subdir2', 'file1.txt')
            dstFile = join('testdir2', 'tempfile2.txt')
            cdm.publishFromFile(dstFile,
                                join(dirname(__file__), 'test.zip', inFileName))
            dstFilePath = join(d.getRepositoryPath(), dstFile)
            self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(dirname(dstFilePath))

        # test publish from a directory from the file system
        srcTmpDir = TemporaryDirectory()
        dirs = ('test1/subdir1', 'test2/subdir1')
        for dir in dirs:
            fullPath = join(srcTmpDir.name, dir)
            makedirs(fullPath)
            f = open(join(fullPath, 'text.html'), 'w')
            f.close()
        try:
            cdm.publishFromDir('testdir3', srcTmpDir.name)
            dstDirPath = join(d.getRepositoryPath(), 'testdir3')
            for dir in dirs:
                dstFilePath = join(dstDirPath, dir, 'text.html')
                self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(dstDirPath)

        # test publish from a directory from a zip file
        try:
            cdm.publishFromDir('testdir4', join(dirname(__file__), 'test.zip', 'dir1'))
            dstDirPath = join(d.getRepositoryPath(), 'testdir4')
            dstFilePath = join(dstDirPath, 'subdir1', 'file1.txt')
            self.assertTrue(isfile(dstFilePath))
            dstFilePath = join(dstDirPath, 'subdir2', 'file2.txt')
            self.assertTrue(isfile(dstFilePath))
            dstFilePath = join(dstDirPath, 'sometestfile.txt')
            tmpFile = open(dstFilePath, 'w')
            tmpFile.close()
            cdm.publishFromDir('testdir4', join(dirname(__file__), 'test.zip', 'dir1'))
            self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(dstDirPath)

        # test publish from a buffer
        try:
            path = join('testdir5', 'somecontent.txt')
            cdm.publishContent(path, 'test')
            dstFilePath = join(d.getRepositoryPath(), path)
            self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(join(d.getRepositoryPath(), dirname(path)))

        # test publish from a file handler
        try:
            path = join('testdir6', 'somecontent2.txt')
            ioStream = StringIO('test 2')
            cdm.publishFromStream(path, ioStream)
            dstFilePath = join(d.getRepositoryPath(), path)
            self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(join(d.getRepositoryPath(), dirname(path)))

    def testLocalFileSystemLinkCDM(self):
        d = HTTPDelivery()
        d.serverName = 'localhost'
        rootDir = TemporaryDirectory()
        d.documentRoot = rootDir.name
#        d.documentRoot = '/var/www'
        d.repositorySubdir = 'repository'
        d.port = 8080
#        ioc.Initializer.initialize(d)
        cdm = LocalFileSystemLinkCDM()
        cdm.delivery = d

        # test publish from a file from the file system
        try:
            srcTmpFile = NamedTemporaryFile()
            dstFile = join('testdir7', 'tempfile.txt')
            cdm.publishFromFile(dstFile, srcTmpFile.name)
            dstLinkPath = join(d.getRepositoryPath(), dstFile + cdm._linkExt)
            self.assertTrue(isfile(dstLinkPath))
            with open(dstLinkPath) as f:
                link = f.readline().strip()
                self.assertEqual(srcTmpFile.name, link)
        finally:
            rmtree(dirname(dstLinkPath))

        # test publish from a file from a zip archive
        try:
            dstFile = join('testdir8', 'tempfile2.txt')
            inFileName = join('dir1', 'subdir2', 'file1.txt')
            srcFilePath = join(dirname(__file__), 'test.zip', inFileName)
            cdm.publishFromFile(dstFile, srcFilePath)
            dstLinkPath = join(d.getRepositoryPath(), dstFile + cdm._zipLinkExt)
            self.assertTrue(isfile(dstLinkPath))
            with open(dstLinkPath) as f:
                zipPath = f.readline().strip()
                inPath = f.readline().strip()
                link = join(zipPath, inPath)
                self.assertEqual(link, srcFilePath)
        finally:
            rmtree(dirname(dstLinkPath))

        # test publish from a directory from the file system
        srcTmpDir = TemporaryDirectory()
        dirs = (join(srcTmpDir.name, 'test1/subdir1'), join(srcTmpDir.name, 'test2/subdir1'))
        for dir in dirs:
            makedirs(dir)
            f = open(join(dir, 'text.html'), 'w+')
            f.close()
        try:
            cdm.publishFromDir('testlink1', srcTmpDir.name)
            dstLinkPath = join(d.getRepositoryPath(), 'testlink1' + cdm._linkExt)
            self.assertTrue(isfile(dstLinkPath))
            with open(dstLinkPath) as f:
                link = f.readline().strip()
                self.assertEqual(srcTmpDir.name, link)
        finally:
            remove(dstLinkPath)

        # test publish from a file from a zip archive
        try:
            srcFilePath = join(dirname(__file__), 'test.zip', 'dir1') + sep
            cdm.publishFromFile('testlink2', srcFilePath)
            dstLinkPath = join(d.getRepositoryPath(), 'testlink2' + cdm._zipLinkExt)
            self.assertTrue(isfile(dstLinkPath))
            with open(dstLinkPath) as f:
                zipPath = f.readline().strip()
                inPath = f.readline().strip()
                link = join(zipPath, inPath)
                self.assertEqual(link, srcFilePath)
        finally:
            remove(dstLinkPath)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
