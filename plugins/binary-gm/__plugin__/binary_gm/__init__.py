'''
Created on Apr 19, 2012

@package: gm binary
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Provides the gm in the workspace tools.
'''

from ally.container import ioc, app
from ally.support.util_deploy import deploy as deployTool, MACHINE_ALL
from ally.support.util_sys import pythonPath
from os.path import join
import logging
import platform

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

NAME = 'GraphicsMagic binary'
GROUP = 'Binaries'
VERSION = '1.0'
DESCRIPTION = '''Populates the gm binary in the workspace tools.'''

# --------------------------------------------------------------------

@ioc.config
def gm_dir_path():
    '''
    The path to the gm tools.
    '''
    return join('workspace', 'tools', 'gm')

# --------------------------------------------------------------------

@app.populate
def deploy():
    if gm_dir_path():
        sys, rel, _ver, deployed = deployTool(join(pythonPath(), 'resources', 'gm'), gm_dir_path())
        if not deployed:
            import os
            # an attempt to make a symlink to gm from the tools/gm/bin directory
            if os.name in ('posix',):
                gmSystemPath = None
                sysPath = os.environ.get("PATH")
                if sysPath:
                    for onePathDir in sysPath.split(os.pathsep):
                        gmPathTest = os.path.join(onePathDir, 'gm')
                        if os.path.isfile(gmPathTest):
                            gmSystemPath = gmPathTest
                            break
                if gmSystemPath:
                    toolDirCreated = False
                    try:
                        os.makedirs(join(gm_dir_path(), 'bin'), 0o777, True)
                        toolDirCreated = True
                    except:
                        toolDirCreated = False
                    if toolDirCreated:
                        try:
                            os.symlink(gmSystemPath, join(gm_dir_path(), 'bin', 'gm.exe'))
                            deployed = True
                        except:
                            pass
        if not deployed:
            log.error('Unable to deploy GraphicsMagic on %s %s!\n    You must install it manually '
                      'and set the proper path in the plugins.properties\n    file for the property '
                      'gm_path (e.g. /usr/bin/gm).' % (sys, rel))
