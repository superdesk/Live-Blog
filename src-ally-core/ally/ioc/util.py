'''
Created on Dec 5, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods for IoC.
'''

from inspect import ismodule
import inspect
from ally.ioc.context import SetupError

# --------------------------------------------------------------------

def isPackage(module):
    '''
    Checks if the provided module is a package.
    
    @param module: module
        The module to be checked.
    '''
    assert ismodule(module), 'Invalid module %s' % module
    return hasattr(module, '__path__')

def callerRegistry(level=1):
    '''
    Provides the calling module locals (registry).
    
    @param level: integer
        The level from where to start finding the caller.
    '''
    stack = inspect.stack()
    currentModule = stack[level][1]
    for k in range(level + 1, len(stack)):
        if stack[k][1] != currentModule:
            frame = stack[k][0]
            break
    else: raise SetupError('There is no other module than the current one')
    return frame.f_locals
