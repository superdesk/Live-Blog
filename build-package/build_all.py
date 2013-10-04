'''
Created on Sep 26, 2013

@package: Liveblog
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

from os.path import dirname, join
from build_allypy import buildAllyPyPackages
from build_liveblog import buildLiveblogPackages

# --------------------------------------------------------------------

if __name__ == '__main__':
    buildDir = join(dirname(__file__), 'build-allypy')
    allyPyDir = join(dirname(__file__), '..', '..')
    buildAllyPyPackages(allyPyDir, buildDir)

    buildDir = join(dirname(__file__), 'build-liveblog')
    liveblogDir = join(dirname(__file__), '..', '..', 'superdesk')
    buildLiveblogPackages(liveblogDir, buildDir)
