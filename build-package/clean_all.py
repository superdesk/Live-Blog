'''
Created on Sep 26, 2013

@package: Liveblog
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

from os.path import dirname, join
from shutil import rmtree
from os import remove
from os.path import isfile, basename, isdir
from glob import glob

# --------------------------------------------------------------------

keepFiles = ('plugins-linux.properties', 'INSTALL', 'requirements.txt')
cleanDirs = ('build-allypy', 'build-liveblog', join('distribution', 'workspace'))
eggDirs = ('components', 'plugins')

# --------------------------------------------------------------------

if __name__ == '__main__':
    for dir in cleanDirs:
        if isdir(join(dirname(__file__), dir)):
            rmtree(join(dirname(__file__), dir))
    for eggDir in eggDirs:
        for file in glob(join(dirname(__file__), '..', 'distribution', eggDir, '*.egg')):
            remove(file)
    for file in glob(join(dirname(__file__), 'distribution', '*')):
        if isfile(file) and basename(file) not in keepFiles:
            remove(file)
