'''
Created on Jun 16, 2012

@package: Superdesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

from glob import glob
from os.path import join, dirname, isabs, abspath, isfile, normpath, relpath
import imp
import sys
from os import chdir, getcwd, stat, walk
import configparser
from tokenize import tokenize
from token import NAME, OP, STRING

# --------------------------------------------------------------------

def getDistDir(packageDir):
    if isfile(join(packageDir, 'setup.cfg')):
        p = configparser.ConfigParser()
        p.read(join(packageDir, 'setup.cfg'))
        return normpath(join(packageDir, p.get('bdist_egg', 'dist_dir')))
    else:
        return dirname(script)

def getPackageName(script):
    packageName, version = None, None
    with open(script, 'rb') as s:
        g = tokenize(s.readline)
        try:
            while True:
                toknum, tokval, _, _, _ = g.__next__()
                if toknum == NAME and tokval == 'name':
                    toknum, tokval, _, _, _ = g.__next__()
                    if toknum == OP:
                        toknum, tokval, _, _, _ = g.__next__()
                        if toknum == STRING:
                            packageName = tokval
                if toknum == NAME and tokval == 'version':
                    toknum, tokval, _, _, _ = g.__next__()
                    if toknum == OP:
                        toknum, tokval, _, _, _ = g.__next__()
                        if toknum == STRING:
                            version = tokval
        except StopIteration: pass
        finally:
            if not packageName: return None
            if version: return packageName.strip('"\'') + '-' + version.strip('"\'')
            else: return packageName.strip('"\'')

def dirMTime(srcDir):
    mtime = None
    for root, dirs, files in walk(srcDir):
        relPath = relpath(root, srcDir)
        if relPath.endswith('.egg-info') or relPath.startswith('build'): continue
        for file in files:
            filePath = join(root, file)
            if not mtime or mtime < stat(filePath).st_mtime: mtime = stat(filePath).st_mtime
        for dir in dirs:
            if dir.endswith('.egg-info') or dir == 'build': continue
            dirPath = join(root, dir)
            if not mtime or mtime < stat(dirPath).st_mtime: mtime = stat(dirPath).st_mtime
    return mtime

# --------------------------------------------------------------------

if __name__ == '__main__':
    sys.argv[0] = 'setup.py'
    sys.argv.insert(1, 'bdist_egg')
    currentDir = getcwd()
    filePath = __file__ if isabs(__file__) else abspath(__file__)
    setupScripts = glob(join(dirname(filePath), '*', 'setup.py'))
    for script in setupScripts:
        packageDir = dirname(script)
        distDir = getDistDir(packageDir)
        packageName = getPackageName(script)
        eggs = glob(join(distDir, packageName + '*'))
        packageDirMTime = dirMTime(packageDir)
        if len(eggs) == 1 and packageDirMTime <= stat(eggs[0]).st_mtime:
            print('*** UP TO DATE %s' % packageName)
            print("\n".rjust(79, '-'))
            continue
        print('*** START %s' % packageName)
        chdir(dirname(script))
        module = imp.load_source('setup', 'setup.py')
        print('*** END %s' % packageName)
        print("\n".rjust(79, '-'))
    chdir(currentDir)
