'''
Created on Sep 24, 2013

@package: Liveblog
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

from os import makedirs
from os.path import dirname, join
from build_common import copyPackage, buildEgg
from shutil import copy

# --------------------------------------------------------------------

buildDir = join(dirname(__file__), 'build-liveblog')

def buildLiveblogPackages(liveblogDir, buildDir):
    '''
    '''
    ignorePaths = ('__pycache__', '*.egg-info', 'setup.cfg', 'setup.py', '*.ant', 'MANIFEST.in')

    relocatePaths = ('gui-resources', 'gui-themes')

    packages = ('frontline', 'frontline-inlet',
                'livedesk', 'livedesk-embed', 'livedesk-sync', 'media-archive', 'media-archive-audio',
                'media-archive-image', 'media-archive-video', 'superdesk', 'superdesk-collaborator',
                'superdesk-language', 'superdesk-person', 'superdesk-person-icon', 'superdesk-post',
                'superdesk-security', 'superdesk-source', 'superdesk-user', 'support', 'url-info')

    print('\nPrepare build for Liveblog')

    makedirs(buildDir, exist_ok=True)

    for package in packages:
        packageDir = join(liveblogDir, 'plugins', package)
        copyPackage(packageDir, buildDir, ignorePaths, relocatePaths)

    copy(join(dirname(__file__), 'setup-liveblog', 'setup.py'), buildDir)
    copy(join(dirname(__file__), 'setup-liveblog', 'setup.cfg'), buildDir)
    copy(join(dirname(__file__), 'setup-liveblog', 'README'), buildDir)

    copyPackage(join(dirname(__file__), 'livedesk-embed'), buildDir, (), ())

    buildEgg(buildDir)

# --------------------------------------------------------------------

if __name__ == '__main__':
    buildDir = join(dirname(__file__), 'build-liveblog')
    liveblogDir = join(dirname(__file__), '..', '..', 'superdesk')
    buildLiveblogPackages(liveblogDir, buildDir)
