'''
Created on Feb 9, 2012

@package ally utilities
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Contains ZIP utils
'''

import os
from os.path import normpath, dirname
from zipfile import is_zipfile, ZipFile

# --------------------------------------------------------------------

# The path separator inside a ZIP archive
ZIPSEP = '/'

def normOSPath(filePath, keepEndSep=False):
    '''
    Normalizes the given path and replaces all ZIP path separators
    with system path separators.
    '''
    if not filePath:
        return filePath
    if os.sep == ZIPSEP:
        hasEndSep = filePath.endswith(os.sep)
    else:
        filePath = filePath.replace(ZIPSEP, os.sep)
        hasEndSep = filePath.endswith(os.sep)
    return normpath(filePath) + os.sep if hasEndSep and keepEndSep else normpath(filePath)

def normZipPath(inZipPath):
    '''
    Replaces all system path separators with ZIP path separators
    and removes the path separator from the start of the path if needed.
    '''
    if not inZipPath:
        return inZipPath
    if os.sep == ZIPSEP:
        return inZipPath.lstrip(ZIPSEP)
    else:
        return inZipPath.replace(os.sep, ZIPSEP).lstrip(ZIPSEP)

def getZipFilePath(filePath, stopPath=''):
    '''
    Detect if part or all of the given path points to a ZIP file

    @param filePath: string
        The full path to the resource

    @return: tuple(string, string)
        Returns a tuple with the following content:
        1. path to the ZIP file in OS format (using OS path separator)
        2. ZIP internal path to the requested file in ZIP format
    '''
    assert isinstance(filePath, str), 'Invalid file path %s' % filePath
    assert isinstance(stopPath, str), 'Invalid stop path %s' % stopPath
    # make sure the file path is normalized and uses the OS separator
    filePath = normOSPath(filePath, True)
    if is_zipfile(filePath): return filePath, ''
    
    parentPath = filePath
    stopPathLen = len(stopPath)
    while len(parentPath) > stopPathLen:
        if is_zipfile(parentPath):
            return parentPath, normZipPath(filePath[len(parentPath):])
        nextSubPath = dirname(parentPath)
        if nextSubPath == parentPath: break
        parentPath = nextSubPath
    raise IOError('Invalid ZIP path %s' % filePath)

def validateInZipPath(zipFile, inFilePath):
    '''
    Verify if the given ZIP file object contains the given path. Returns nothing.
    If the path does not exist in the ZIP file raises KeyError exception.
    
    @param zipFile: ZipFile
        The ZIP file object to check
    @param inFilePath: str
        The path that should be validated to exist in the ZIP file
    '''
    assert isinstance(zipFile, ZipFile), 'Invalid zip file object %s' % zipFile
    assert isinstance(inFilePath, str), 'Invalid file path %s' % inFilePath
    try: zipFile.getinfo(inFilePath)
    except KeyError as k:
        found = False
        if inFilePath.endswith(ZIPSEP):
            names = zipFile.namelist()
            for name in names:
                if name.startswith(inFilePath):
                    found = True; break
        if not found: raise k
