'''
Created on Sep 30, 2013

@package: Ally-Py
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

from glob import glob
from shutil import copytree, copy, ignore_patterns
from os.path import isfile, join, isdir, basename
from fnmatch import fnmatch
from os import makedirs, chdir, getcwd
import sys
import imp
from io import StringIO

# --------------------------------------------------------------------

def matchPaths(path, pathPatterns=()):
    '''
    Return True if the given path matches any of the patterns in the given
    touple of patterns.
    '''
    for pattern in pathPatterns:
        if fnmatch(path, pattern): return True
    return False

def _copyPackage(srcDir, dstDir, ignorePaths=()):
    '''
    Copy package from the source directory to the destination directory.
    The directories from srcDir are copied into dstDir. The original directory
    (srcDir) is not copied.
    '''
    if not isdir(srcDir): return

    if matchPaths(basename(srcDir), ignorePaths): return

    if not isdir(dstDir):
        print('Copy tree ', srcDir, '\n    to ', dstDir)
        copytree(srcDir, dstDir, ignore=ignore_patterns(*ignorePaths))
        return
    files = glob(join(srcDir, '*'))
    for file in files:
        if isfile(file):
            if matchPaths(basename(file), ignorePaths): continue
            print('Copy file ', file, '\n    to ', dstDir)
            copy(file, dstDir)
        elif isdir(file):
            copyPackage(file, join(dstDir, basename(file)), ignorePaths)

def copyPackage(srcDir, dstDir, ignorePaths=(), relocatePaths=()):
    '''
    Copy package from the source directory to the destination directory.
    The directories from srcDir are copied into dstDir. The original directory
    (srcDir) is not copied.
    '''
    if not isdir(srcDir): return

    if matchPaths(basename(srcDir), ignorePaths): return

    if not isdir(dstDir): makedirs(dstDir, exist_ok=True)

    files = glob(join(srcDir, '*'))
    for file in files:
        if matchPaths(basename(file), ignorePaths): continue

        if isfile(file):
            copy(file, dstDir)
        elif isdir(file):
            if matchPaths(basename(file), relocatePaths):
                relDstDir = join(dstDir, '__plugin__', basename(srcDir).replace('-', '_'), basename(file))
            else:
                relDstDir = join(dstDir, basename(file))

            copyPackage(file, relDstDir, ignorePaths)

def buildEgg(buildDir):
    # make arguments for build and clean operations
    origArgv = list(sys.argv)

    cleanArgv = ['setup.py', 'clean', '--all']
    buildArgv = ['setup.py', 'bdist_egg', 'sdist', 'upload']

    currentDir = getcwd()
    stdout = sys.stdout
    stderr = sys.stderr

    # do a pre-clean
    chdir(buildDir)

    print('Clean dist from %s' % buildDir)
    sys.argv = cleanArgv
    sys.stdout, sys.stderr = StringIO(), StringIO()
    imp.load_source('setup', 'setup.py')
    sys.stdout, sys.stderr = stdout, stderr

    print('Build and upload dist from %s' % buildDir)
    sys.argv = buildArgv
    sys.stdout = StringIO()
    imp.load_source('setup', 'setup.py')
    sys.stdout = stdout

    chdir(currentDir)
    sys.argv = origArgv
