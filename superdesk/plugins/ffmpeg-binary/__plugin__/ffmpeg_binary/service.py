'''
Created on Sep 14, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the services setups for ffmpeg binary.
'''

import logging
from os.path import join
from ally.support.util_sys import pythonPath
from ally.container import ioc
from ally.support.util_deploy import deploy as deployTool

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@ioc.config
def ffmpeg_dir_path():
    '''
    The path to the ffmpeg tools.
    '''
    return join('workspace', 'tools', 'ffmpeg')

# --------------------------------------------------------------------

@ioc.start
def deploy():
    if ffmpeg_dir_path(): deployTool(join(pythonPath(), 'resources', 'ffmpeg'), ffmpeg_dir_path())
