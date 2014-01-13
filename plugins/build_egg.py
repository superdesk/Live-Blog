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
from copy import copy
from io import StringIO

# --------------------------------------------------------------------

def getDistDir(packageDir):
    '''
    Return the distribution directory corresponding to the given package.
    '''
    if isfile(join(packageDir, 'setup.cfg')):
        p = configparser.ConfigParser()
        p.read(join(packageDir, 'setup.cfg'))
        return normpath(join(packageDir, p.get('bdist_egg', 'dist_dir')))
    else:
        return dirname(script)

def getPackageName(script):
    '''
    Return the package name for the given setup script.
    '''
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
    '''
    Return the last modified time for the given directory (the modified time of the
    file which was modified last in that directory)
    '''
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
    clean = not(len(sys.argv) > 1 and sys.argv[1] == '-b')

    # make arguments for build and clean operations
    buildArgv, cleanArgv = copy(sys.argv), copy(sys.argv)
    buildArgv = sys.argv
    buildArgv[0] = 'setup.py'
    buildArgv.insert(1, 'bdist_egg')
    cleanArgv.insert(1, 'clean')
    cleanArgv.insert(2, '--all')

    currentDir = getcwd()
    stdout = sys.stdout
    stderr = sys.stderr

    filePath = __file__ if isabs(__file__) else abspath(__file__)
    setupScripts = glob(join(dirname(filePath), '*', 'setup.py'))
    for script in setupScripts:
        packageDir = dirname(script)
        distDir = getDistDir(packageDir)
        packageName = getPackageName(script)

        # do a preclean
        chdir(dirname(script))
        sys.argv = cleanArgv
        sys.stdout, sys.stderr = StringIO(), StringIO()
        module = imp.load_source('setup', script)
        sys.stdout, sys.stderr = stdout, stderr

        eggs = glob(join(distDir, packageName + '*'))
        packageDirMTime = dirMTime(packageDir)
        if len(eggs) == 1 and packageDirMTime <= stat(eggs[0]).st_mtime:
#            print('*** UP TO DATE %s' % packageName)
#            print("\n".rjust(79, '-'))
            continue

        print('*** BUILD %s' % packageName)
        sys.argv = buildArgv
        sys.stdout = StringIO()
        module = imp.load_source('setup', 'setup.py')
        sys.stdout = stdout

        if clean:
            print("\n".rjust(79, '-'))
            print('*** CLEAN %s' % packageName)
            sys.argv = cleanArgv
            sys.stdout, sys.stderr = StringIO(), StringIO()
            module = imp.load_source('setup', script)
            sys.stdout, sys.stderr = stdout, stderr

        print("\n".rjust(79, '-'))

    chdir(currentDir)
