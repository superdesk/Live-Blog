'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the deployment of the distribution that contains this deploy.
'''

import sys
import traceback
import inspect
import pkgutil
import os

# --------------------------------------------------------------------

_EXTEND = set()
# Used to keep the current extending package.
def deployExtendPackage():
    '''
    Provides the package extension for loaded libraries.
    '''
    loc = inspect.stack()[1][0].f_locals
    fullName, paths = loc['__name__'], loc['__path__']
    if name in _EXTEND: return
    _EXTEND.add(name)
    k = name.rfind('.')
    
    if k >= 0:
        package = sys.modules[name[:k]]
        name = name[k + 1:]
        importers = [pack[0] for pack in pkgutil.iter_modules(package.__path__)]
    else: importers = pkgutil.iter_importers()
    
    for importer in importers:
        moduleLoader = importer.find_module(name)
        if moduleLoader and moduleLoader.is_package(name):
            path = os.path.dirname(moduleLoader.get_filename(name))
            if path not in paths:
                paths.append(path)
                module = {'__name__':name, '__path__':paths}
                exec(moduleLoader.get_code(name), module) # We ensure that every __init__ is called at least once.
                if module.get('deployExtendPackage') != deployExtendPackage:
                    raise ImportError('The package %r in path %r does not allow extension' % (name, path))
    _EXTEND.remove(name)

# --------------------------------------------------------------------

def findLibraries(folder):
    '''
    Finds all the libraries (that have extension .egg) if the provided folder.
    '''
    eggs = []
    for name in os.listdir(folder):
        fullPath = os.path.join(folder, name)
        if os.path.isfile(fullPath) and fullPath.endswith('.egg'): eggs.append(fullPath)
    return eggs


if __name__ == '__main__':
    for path in findLibraries(os.path.join(os.path.dirname(__file__), 'components')):
        if not path.count('ally-ioc'): sys.path.append(path)
    sys.path.append('e:/Sourcefabric/Workspace/src-ally-ioc')
    try:
        from ally import ioc
        ioc.assembleSys().assemble()
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while deploying the application', file=sys.stderr)
        traceback.print_exc()
        print('-' * 150, file=sys.stderr)
