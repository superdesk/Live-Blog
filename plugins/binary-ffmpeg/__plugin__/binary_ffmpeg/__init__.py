'''
Created on Apr 19, 2012

@package: ffmpeg binary
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Provides the ffmpeg in the workspace tools.
'''

from ally.container import ioc, app
from ally.support.util_deploy import deploy as deployTool
from ally.support.util_sys import pythonPath
from os.path import join
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

NAME = 'FFmpeg binary'
GROUP = 'Binaries'
VERSION = '1.0'
DESCRIPTION = '''Populates in the workspace tools the FFMpeg binary.'''

# --------------------------------------------------------------------

@ioc.config
def ffmpeg_dir_path():
    '''
    The path to the ffmpeg tools.
    '''
    return join('workspace', 'tools', 'ffmpeg')

# --------------------------------------------------------------------

@app.populate
def deploy():
    if ffmpeg_dir_path():
        sys, rel, _ver, deployed = deployTool(join(pythonPath(), 'resources', 'ffmpeg'), ffmpeg_dir_path())
        if not deployed:
            log.error('Unable to deploy FFMpeg on %s %s!\n    You must install it manually '
                      'and set the proper path in the plugins.properties\n    file for the property '
                      'ffmpeg_path (e.g. /usr/bin/ffmpeg).' % (sys, rel))
