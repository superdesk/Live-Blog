'''
Created on Jun 16, 2012

@package: Superdesk
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
    sys.argv.insert(1, 'clean')
    sys.argv.insert(2, '--all')
    currentDir = getcwd()
    filePath = __file__ if isabs(__file__) else abspath(__file__)
    setupScripts = glob(join(dirname(filePath), '*', 'setup.py'))
    for script in setupScripts:
        chdir(dirname(script))
        module = imp.load_source('setup', script)
        print("\n".rjust(79, '-'))
    chdir(currentDir)
