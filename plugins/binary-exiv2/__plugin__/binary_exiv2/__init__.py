'''
Created on Apr 19, 2012

@package: ffmpeg binary
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Provides the ffmpeg in the workspace tools.
'''

from ally.container import ioc
from ally.support.util_deploy import deploy as deployTool, MACHINE_ALL
from ally.support.util_sys import pythonPath
from distribution.container import app
from os.path import join
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

NAME = 'Exiv2 binary'
GROUP = 'Binaries'
VERSION = '1.0'
DESCRIPTION = '''Populates in the workspace tools the Exiv2 binary.'''

# --------------------------------------------------------------------

@ioc.config
def exiv2_dir_path():
    '''
    The path to the exiv2 tools.
    '''
    return join('workspace', 'tools', 'exiv2')

# --------------------------------------------------------------------

@app.populate
def deploy():
    if exiv2_dir_path():
        sys, rel, _ver, deployed = deployTool(join(pythonPath(), 'resources', 'exiv2'), exiv2_dir_path())
        if not deployed:
            log.error('Unable to deply Exiv2 on %s %s!\n    You must install it manually '
                      'and set the proper path in the plugins.properties\n    file for the property '
                      'metadata_extractor_path (e.g. /usr/bin/exiv2).' % (sys, rel))
