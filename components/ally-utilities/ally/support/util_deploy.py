'''
Created on Sep 14, 2012

@package ally utilities
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Contains ZIP utils
'''

from os.path import join, isdir
from ally.support.util_io import synchronizeURIToDir
from ally.zip.util_zip import getZipFilePath
from platform import system, machine

# --------------------------------------------------------------------

SYSTEM_ALL = 'all'
MACHINE_ALL = 'all'

# --------------------------------------------------------------------

def deploy(source, destination, systemName=None, machineName=None):
    #TODO: Mugur: add comments and explain what is going one here.
    # THis should not be placed here a separate plugin needs to be created.
    assert isinstance(source, str), 'Invalid source path %s' % source
    assert isinstance(destination, str), 'Invalid destination path %s' % destination
    assert not systemName or isinstance(systemName, str), 'Invalid system name %s' % systemName
    assert not machineName or isinstance(machineName, str), 'Invalid machine name %s' % machineName

    systemName = systemName if systemName else system()
    machineName = machineName if machineName else machine()

    systems = {SYSTEM_ALL:True} if systemName == SYSTEM_ALL else {systemName:True, SYSTEM_ALL:False}
    machines = {MACHINE_ALL:True} if machineName == MACHINE_ALL else {machineName:True, MACHINE_ALL:False}

    for systemName, systemRequired in systems.items():
        for machineName, machineRequired in machines.items():
            srcDir = join(source, systemName, machineName)
            if not isdir(srcDir):
                try: getZipFilePath(srcDir)
                except IOError:
                    if systemRequired and machineRequired:
                        raise IOError('Cannot locate required dependency \'%s\' for system %s with architecture %s'
                                      % (srcDir, systemName, machineName))
                    else: continue
            synchronizeURIToDir(srcDir, destination)
