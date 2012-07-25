'''
Created on Jun 16, 2012

@package: Newscoop
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

from glob import glob
from os.path import join, dirname, isabs, abspath
import imp
import sys
from os import chdir, getcwd

# --------------------------------------------------------------------

if __name__ == '__main__':
    sys.argv[0] = 'setup.py'
    sys.argv.insert(1, 'bdist_egg')
    currentDir = getcwd()
    filePath = __file__ if isabs(__file__) else abspath(__file__)
    setupScripts = glob(join(dirname(filePath), '*', 'setup.py'))
    for script in setupScripts:
        chdir(dirname(script))
        module = imp.load_source('setup', 'setup.py')
        print("\n".rjust(79, '-'))
    chdir(currentDir)
