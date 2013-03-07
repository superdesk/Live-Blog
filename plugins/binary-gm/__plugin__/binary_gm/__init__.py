'''
Created on Apr 19, 2012

@package: ffmpeg binary
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Provides the ffmpeg in the workspace tools.
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
            log.error('Unable to deploy GraphicsMagic on %s %s!\n    You must install it manually '
                      'and set the proper path in the plugins.properties\n    file for the property '
                      'gm_path (e.g. /usr/bin/gm).' % (sys, rel))
