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
from os.path import join, dirname, isfile, isdir
from shutil import rmtree
from cdm.impl.local_filesystem import HTTPDelivery, LocalFileSystemCDM, LocalFileSystemLinkCDM
from ally.container import ioc
from io import StringIO
from os import makedirs, remove, sep
from cdm.spec import PathNotFound


class TestHTTPDelivery(unittest.TestCase):

    def testHTTPDelivery(self):
        d = HTTPDelivery()
        d.serverURI = 'http://localhost:8080/content/'
        d.repositoryPath = '/var/www/repository'
        ioc.Initializer.initialize(d)
        self.assertEqual(d.getRepositoryPath(), '/var/www/repository',
                         'Computing the repository path')
        self.assertEqual(d.getURI('somedir/somefile.jpg'),
                         'http://localhost:8080/content/somedir/somefile.jpg',
                         'Computing the URI')

    def testLocalFilesystemCDM(self):
        d = HTTPDelivery()
        rootDir = TemporaryDirectory()
        d.serverURI = 'http://localhost/content/'
#        d.repositoryPath = '/var/www/repository'
        d.repositoryPath = rootDir.name
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
            with open(join(fullPath, 'text.html'), 'w') as _f: pass
        try:
            cdm.publishFromDir('testdir3', srcTmpDir.name)
            dstDirPath = join(d.getRepositoryPath(), 'testdir3')
            for dir in dirs:
                dstFilePath = join(dstDirPath, dir, 'text.html')
                self.assertTrue(isfile(dstFilePath))
            # test remove path
            filePath = 'testdir3/test1/subdir1/text.html'
            self.assertTrue(isfile(join(d.getRepositoryPath(), filePath)))
            cdm.removePath(filePath)
            self.assertFalse(isfile(join(d.getRepositoryPath(), filePath)))
            dirPath = 'testdir3/test2'
            self.assertTrue(isdir(join(d.getRepositoryPath(), dirPath)))
            cdm.removePath(dirPath)
            self.assertFalse(isdir(join(d.getRepositoryPath(), dirPath)))
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
            # Test whether republishing the same directory checks the last modified date
            # The file created manually in the repository should not be deleted because
            # the zip archive was not modified from the last publish
            dstFilePath = join(dstDirPath, 'sometestfile.txt')
            with open(dstFilePath, 'w') as _f: pass
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
        rootDir = TemporaryDirectory()
        d.serverURI = 'http://localhost/content/'
#        d.repositoryPath = '/var/www/repository'
        d.repositoryPath = rootDir.name
#        ioc.Initializer.initialize(d)
        cdm = LocalFileSystemLinkCDM()
        cdm.delivery = d

        try:
            exceptionRaised = False
            cdm.publishFromFile('a/../../b', 'somefile.txt')
        except PathNotFound:
            exceptionRaised = True
        self.assertTrue(exceptionRaised, 'No exception was rased on out of repository path')

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
            with open(join(dir, 'text.html'), 'w+') as _f: pass
        try:
            cdm.publishFromDir('testlink1', srcTmpDir.name)
            dstLinkPath = join(d.getRepositoryPath(), 'testlink1' + cdm._linkExt)
            self.assertTrue(isfile(dstLinkPath))
            with open(dstLinkPath) as f:
                link = f.readline().strip()
                self.assertEqual(srcTmpDir.name, link)
            # test path remove
            delPath = 'testlink1/test1/subdir1/text.html'
            cdm.removePath(delPath)
            self.assertTrue(isfile(join(d.getRepositoryPath(), delPath + '.deleted')))
            delPath = 'testlink1/test1'
            cdm.removePath(delPath)
            self.assertTrue(isfile(join(d.getRepositoryPath(), delPath + '.deleted')))
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
            # test path remove
            delPath1 = 'testlink2/subdir1/file1.txt'
            cdm.removePath(delPath1)
            self.assertTrue(isfile(join(d.getRepositoryPath(), delPath1 + '.deleted')))
            delPath2 = 'testlink2/subdir1/'
            self.assertTrue(isdir(join(d.getRepositoryPath(), delPath2)))
            cdm.removePath(delPath2)
            self.assertTrue(isfile(join(d.getRepositoryPath(), delPath2.rstrip('/') + '.deleted')))
            self.assertFalse(isdir(join(d.getRepositoryPath(), delPath2)))
            self.assertFalse(isfile(join(d.getRepositoryPath(), delPath1 + '.deleted')))
        finally:
            remove(dstLinkPath)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
