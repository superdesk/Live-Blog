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

# --------------------------------------------------------------------

NAME = 'GraphicsMagic binary'
GROUP = 'Binaries'
VERSION = '1.0'
DESCRIPTION = '''Populates in the workspace tools the gm binary.'''

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
    if gm_dir_path(): deployTool(join(pythonPath(), 'resources', 'gm'), gm_dir_path())
