'''
Created on Dec 22, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the extender for libraries packages.
'''

from inspect import stack
from os.path import dirname
from pkgutil import get_importer, iter_importers
from sys import modules
from types import ModuleType

# --------------------------------------------------------------------

_EXTEND = set()
# Used to keep the current extending package.
def deployExtendPackage():
    '''
    Provides the package extension for loaded libraries.
    '''
    loc = stack()[1][0].f_locals
    fullName, paths = loc['__name__'], loc['__path__']
    if fullName in _EXTEND: return
    
    _EXTEND.add(fullName)
    k = fullName.rfind('.')
    if k >= 0:
        package = modules[fullName[:k]]
        name = fullName[k + 1:]
        importers = [get_importer(path) for path in package.__path__]
    else:
        name = fullName
        importers = iter_importers()
    
    for importer in importers:
        moduleLoader = importer.find_module(name)
        if moduleLoader and moduleLoader.is_package(name):
            path = dirname(moduleLoader.get_filename(name))
            if path not in paths:
                paths.append(path)
                module = ModuleType(fullName)
                module.__dict__['__path__'] = paths
                exec(moduleLoader.get_code(name), module.__dict__)
                # We ensure that every __init__ is called at least once.
                if getattr(module, 'deployExtendPackage', None) != deployExtendPackage:
                    raise ImportError('The package %r in path %r does not allow extension' % (name, path))
    _EXTEND.remove(fullName)
