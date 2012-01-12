'''
Created on Nov 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the AOP (aspect oriented programming) support.
'''

from ..support.util_sys import searchModules, packageModules, isPackage
from ._impl.aop import AOPModules
from inspect import ismodule

# --------------------------------------------------------------------

class AOPError(Exception):
    '''
    Exception thrown when there is a AOP problem.
    '''

# --------------------------------------------------------------------

def modulesIn(*paths):
    '''
    Provides all the modules that are found in the provided package paths.
    
    @param paths: arguments[string|module]
        The package paths to load modules from.
    '''
    new = {}
    for path in paths:
        if isinstance(path, str):
            for modulePath in searchModules(path): new[modulePath] = modulePath
        elif ismodule(path):
            if not isPackage(path):
                raise AOPError('The provided module %r is not a package' % path)
            for modulePath in packageModules(path): new[modulePath] = modulePath
        else: raise AOPError('Cannot use path %s' % path)
    return AOPModules(new)

