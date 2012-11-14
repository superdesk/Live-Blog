'''
Created on Jan 9, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Provides unit testing for the local filesystem module.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

from ally.zip.util_zip import normOSPath
from cdm.impl.local_filesystem import HTTPDelivery, LocalFileSystemCDM, \
    LocalFileSystemLinkCDM
from cdm.spec import PathNotFound
from datetime import datetime
from io import BytesIO
from os import makedirs, remove, sep, stat
from os.path import join, dirname, isfile, isdir
from shutil import rmtree
from tempfile import NamedTemporaryFile, TemporaryDirectory
import json
import re
import unittest

normpath = lambda txt: re.sub('[\\W]+', '', txt)

class TestHTTPDelivery(unittest.TestCase):

    def testHTTPDelivery(self):
        d = HTTPDelivery()
        d.serverURI = 'http://localhost:8080/content/'
        self.assertEqual(d.getURI('somedir/somefile.jpg'),
                         'http://localhost:8080/content/somedir/somefile.jpg',
                         'Computing the URI')

    def testLocalFilesystemCDM(self):
        d = HTTPDelivery()
        rootDir = TemporaryDirectory()
        d.serverURI = 'http://localhost/content/'
        d.repositoryPath = rootDir.name
#        d.repositoryPath = '/var/www/repository'
#        ioc.Initializer.initialize(d)
        cdm = LocalFileSystemCDM()
        cdm.delivery = d

        # test publish from a file from the file system
        try:
            srcTmpFile = NamedTemporaryFile(delete=False)
            srcTmpFile.close()
            dstPath = 'testdir1/tempfile.txt'
            cdm.publishFromFile(dstPath, srcTmpFile.name)
            dstFilePath = join(d.getRepositoryPath(), normOSPath(dstPath))
            self.assertTrue(isfile(dstFilePath))
            self.assertEqual(datetime.fromtimestamp(stat(dstFilePath).st_mtime),
                             cdm.getTimestamp(dstPath))
        finally:
            rmtree(dirname(dstFilePath))
            remove(srcTmpFile.name)

        # test publish from a file from a zip archive
        try:
            inFileName = join('dir1', 'subdir2', 'file1.txt')
            dstPath = join('testdir2', 'tempfile2.txt')
            cdm.publishFromFile(dstPath,
                                join(dirname(__file__), 'test.zip', inFileName))
            dstFilePath = join(d.getRepositoryPath(), normOSPath(dstPath))
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
                self.assertEqual(datetime.fromtimestamp(stat(dstFilePath).st_mtime),
                                 cdm.getTimestamp(join('testdir3', dir, 'text.html')))
            # test remove path
            filePath = 'testdir3/test1/subdir1/text.html'
            self.assertTrue(isfile(join(d.getRepositoryPath(), filePath)))
            cdm.republish(filePath, filePath + '.new')
            self.assertTrue(isfile(join(d.getRepositoryPath(), filePath + '.new')))
            cdm.republish(filePath + '.new', filePath)
            cdm.remove(filePath)
            self.assertFalse(isfile(join(d.getRepositoryPath(), filePath)))
            dirPath = 'testdir3/test2'
            self.assertTrue(isdir(join(d.getRepositoryPath(), dirPath)))
            cdm.remove(dirPath)
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

        # test publish from a string
        try:
            path = join('testdir5', 'somecontent.txt')
            cdm.publishContent(path, 'test')
            dstFilePath = join(d.getRepositoryPath(), path)
            self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(join(d.getRepositoryPath(), dirname(path)))

        # test publish from a file object
        try:
            path = join('testdir6', 'somecontent2.txt')
            cdm.publishFromFile(path, BytesIO(b'test 2'))
            dstFilePath = join(d.getRepositoryPath(), path)
            self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(join(d.getRepositoryPath(), dirname(path)))

    def testLocalFileSystemLinkCDM(self):
        d = HTTPDelivery()
        rootDir = TemporaryDirectory()
        d.serverURI = 'http://localhost/content/'
        d.repositoryPath = rootDir.name
#        d.repositoryPath = '/var/www/repository'
#        ioc.Initializer.initialize(d)
        cdm = LocalFileSystemLinkCDM()
        cdm.delivery = d

        try:
            exceptionRaised = False
            cdm.publishFromFile('a/../../b', 'somefile.txt')
        except PathNotFound:
            exceptionRaised = True
        self.assertTrue(exceptionRaised, 'No exception was raised on out of repository path')

        # test publish from a file from the file system
        try:
            srcTmpFile = NamedTemporaryFile()
            dstFile = join('testdir7', 'tempfile.txt')
            cdm.publishFromFile(dstFile, srcTmpFile.name)
            dstLinkPath = join(d.getRepositoryPath(), dstFile + cdm._linkExt)
            self.assertTrue(isfile(dstLinkPath))
            with open(dstLinkPath) as f:
                links = json.load(f)
                self.assertIsInstance(links, list)
                self.assertEqual(links[0][0], 'FS')
                self.assertEqual(srcTmpFile.name, links[0][1])
                self.assertEqual(datetime.fromtimestamp(stat(srcTmpFile.name).st_mtime),
                                 cdm.getTimestamp('testdir7/tempfile.txt'))
        finally:
            rmtree(dirname(dstLinkPath))

        # test publish from a file from a zip archive
        try:
            dstFile = join('testdir8', 'tempfile2.txt')
            inFileName = join('dir1', 'subdir2', 'file1.txt')
            srcFilePath = join(dirname(__file__), 'test.zip', inFileName)
            cdm.publishFromFile(dstFile, srcFilePath)
            dstLinkPath = join(d.getRepositoryPath(), dstFile + cdm._linkExt)
            self.assertTrue(isfile(dstLinkPath))
            with open(dstLinkPath) as f:
                links = json.load(f)
                self.assertEqual(links[0][0], 'ZIP')
                zipPath = links[0][1]
                inPath = normOSPath(links[0][2], True)
                linkPath = join(zipPath, inPath)
                self.assertEqual(normpath(linkPath), normpath(srcFilePath))
                self.assertEqual(datetime.fromtimestamp(stat(join(dirname(__file__), 'test.zip')).st_mtime),
                                 cdm.getTimestamp('testdir8/tempfile2.txt'))
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
                links = json.load(f)
                self.assertEqual(links[0][0], 'FS')
                self.assertEqual(srcTmpDir.name, links[0][1])
                self.assertEqual(datetime.fromtimestamp(stat(join(srcTmpDir.name, 'test1/subdir1/text.html')).st_mtime),
                                 cdm.getTimestamp('testlink1/test1/subdir1/text.html'))
            # test path remove
            delPath1 = 'testlink1/test1/subdir1/text.html'
            cdm.remove(delPath1)
            self.assertTrue(isfile(join(d.getRepositoryPath(), delPath1 + '.deleted')))
            delPath2 = 'testlink1/test1'
            cdm.remove(delPath2)
            self.assertTrue(isfile(join(d.getRepositoryPath(), delPath2 + '.deleted')))
        finally:
            rmtree(join(d.getRepositoryPath(), 'testlink1'))
            remove(dstLinkPath)

        # test publish from a file from a zip archive
        try:
            srcFilePath = join(dirname(__file__), 'test.zip', 'dir1') + sep
            cdm.publishFromFile('testlink2', srcFilePath)
            dstLinkPath = join(d.getRepositoryPath(), 'testlink2' + cdm._linkExt)
            self.assertTrue(isfile(dstLinkPath))
            with open(dstLinkPath) as f:
                links = json.load(f)
                self.assertEqual(links[0][0], 'ZIP')
                zipPath = links[0][1]
                inPath = normOSPath(links[0][2], True)
                link = join(zipPath, inPath)
                self.assertEqual(link, srcFilePath)
                self.assertEqual(datetime.fromtimestamp(stat(join(dirname(__file__), 'test.zip')).st_mtime),
                                 cdm.getTimestamp('testlink2/subdir1/file1.txt'))
            # test path remove
            delPath1 = 'testlink2/subdir1/file1.txt'
            cdm.remove(delPath1)
            self.assertTrue(isfile(join(d.getRepositoryPath(), delPath1 + '.deleted')))
            delPath2 = 'testlink2/subdir1/'
            self.assertTrue(isdir(join(d.getRepositoryPath(), delPath2)))
            cdm.remove(delPath2)
            self.assertTrue(isfile(join(d.getRepositoryPath(), delPath2.rstrip('/') + '.deleted')))
            self.assertFalse(isdir(join(d.getRepositoryPath(), delPath2)))
            self.assertFalse(isfile(join(d.getRepositoryPath(), delPath1 + '.deleted')))
        finally:
            rmtree(join(d.getRepositoryPath(), 'testlink2'))
            remove(dstLinkPath)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
