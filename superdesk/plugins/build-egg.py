'''
Created on Jun 16, 2012

@package: Newscoop
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

from glob import glob
from os.path import join, dirname, sep, split
import imp
import sys
from os import chdir, getcwd
from os.path import isdir, normpath, basename
from shutil import move, copy2

# --------------------------------------------------------------------

distComponents = '../../distribution/components'
distPlugins = '../../distribution/plugins'
sdComponents = '../distribution/components'
sdPlugins = '../distribution/plugins'

def copyDir(srcDir, dstDir, filter=None):
    if isdir(srcDir):
        files = glob(join(srcDir, filter)) if isinstance(filter, str) else srcDir
        for file in files:
            fName = basename(file)
            newPath = join(dstDir, fName)
            print("* copy %s\n  to   %s" % (file, newPath))
            copy2(file, newPath + '.new')
            move(newPath + '.new', newPath)

if __name__ == '__main__':
    sys.argv[0] = 'setup.py'
    sys.argv.insert(1, 'bdist_egg')
    currentDir, fileDir = getcwd(), dirname(__file__)
    setupScripts = glob(join(fileDir, '*', 'setup.py'))
    for script in setupScripts:
        chdir(dirname(script))
        module = imp.load_source('setup', script)
        print("\n".rjust(79, '-'))
    chdir(currentDir)

    componentsDir = normpath(join(fileDir, distComponents))
    sdComponentsPath = normpath(join(fileDir, sdComponents))
    copyDir(componentsDir, sdComponentsPath, '*.egg')

    pluginsDir = normpath(join(fileDir, distPlugins))
    sdPluginsPath = normpath(join(fileDir, sdPlugins))
    copyDir(pluginsDir, sdPluginsPath, '*.egg')
