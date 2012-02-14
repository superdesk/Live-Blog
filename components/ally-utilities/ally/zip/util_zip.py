'''
Created on Feb 9, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Contains ZIP utils
'''

import os
from os.path import normpath

# --------------------------------------------------------------------

# The path separator inside a ZIP archive
ZIPSEP = '/'

def normOSPath(filePath, keepEndSep = False):
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
