'''
Created on Jan 12, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support functions for the container.
'''

from ..support.util_sys import callerLocals, callerGlobals
from ._impl.aop import AOPClasses, AOPResources
from ._impl.ioc import SetupError, SetupEntityProxy, SetupEntityCreate, Assembly, \
    CallEntity, register
from inspect import isclass

# --------------------------------------------------------------------
# Functions available in setup modules.

def createEntitySetup(*classes, prefix='', suffix=''):
    '''
    Creates entity setup functions for the provided classes. The name of the setup functions that will be generated are
    formed based on the class name of the provided classes.
    
    @param classes: arguments(class|AOPClasses)
        The classes to be added setup functions.
    @param prefix: string
        The prefix to add for the setup name (before the class name), if empty or None it will automatically add as a
        prefix the module performing the call.
    @param suffix: string
        The suffix to add for the setup name (after the class name).
    @return: References
        The entities repository for the classes setup functions.
    '''
    assert isinstance(prefix, str), 'Invalid prefix %s' % prefix
    assert isinstance(suffix, str), 'Invalid suffix %s' % suffix
    clazzes = []
    for clazz in classes:
        if isclass(clazz): clazzes.append(clazz)
        elif isinstance(clazz, AOPClasses):
            assert isinstance(clazz, AOPClasses)
            clazzes.extend(clazz.asList())
        else: raise SetupError('Cannot use class %s' % clazz)
    
    registry = callerLocals()
    if not prefix:
        if '__name__' not in registry:
            raise SetupError('The create call needs to be made directly from the module, or provide a prefix')
        prefix = registry['__name__'] + '.'
    for clazz in clazzes:
        register(SetupEntityCreate(prefix + clazz.__name__ + suffix, clazz), registry)

def createEntityProxy(*classes, prefix='', listeners=None):
    '''
    Creates entity proxies that are for the provided classes.
    
    @param classes: arguments(class|AOPClasses)
        The classes to be proxied.
    @param prefix: string
        The prefix for the entities name to create the proxies for.
    @param listeners: None|Callable|list[Callable]|tuple(Callable)
        The listeners to be invoked when a proxy is created.
    '''
    assert isinstance(prefix, str), 'Invalid prefix %s' % prefix
    
    clazzes = []
    for clazz in classes:
        if isclass(clazz): clazzes.append(clazz)
        elif isinstance(clazz, AOPClasses):
            assert isinstance(clazz, AOPClasses)
            clazzes.extend(clazz.asList())
        else: raise SetupError('Cannot use class %s' % clazz)
    
    if not listeners: listeners = []
    elif not isinstance(listeners, (list, tuple)): listeners = [listeners]
            
    assert isinstance(listeners, (list, tuple)), 'Invalid listeners %s' % listeners
    register(SetupEntityProxy(prefix, clazzes, listeners), callerLocals())

# --------------------------------------------------------------------
# Functions available in setup functions calls.

def entities():
    '''
    !Attention this function only available from within a setup functions!
    Provides all the entities references found in the current assembly wrapped in a AOP class.
    
    @return: AOP
        The resource AOP.
    '''
    return AOPResources({name:name for name, call in Assembly.current().calls.items() if isinstance(call, CallEntity)})

def entitiesLocal():
    '''
    !Attention this function only available from within a setup functions!
    Provides all the entities references for the module from where the call is made found in the current assembly.
    
    @return: AOP
        The resource AOP.
    '''
    registry = callerGlobals()
    if '__name__' not in registry:
        raise SetupError('The create call needs to be made from a module function')
    rsc = AOPResources({name:name for name, call in Assembly.current().calls.items() if isinstance(call, CallEntity)})
    rsc.filter(registry['__name__'] + '.*')
    return rsc

def entityFor(clazz):
    '''
    !Attention this function only available from within a setup functions!
    Provides the entity for the provided class (only if the setup function exposes a return type that is either the
    provided class or a super class) found in the current assembly.
    
    @param clazz: class
        The class to find the entity for.
    @return: object
        The instance for the provided class.
    @raise SetupError: In case there is no entity for the required class or there are to many.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    entities = [name for name, call in Assembly.current().calls.items()
                if isinstance(call, CallEntity) and call.type and (call.type == clazz or issubclass(call.type, clazz))]
    if not entities:
        raise SetupError('There is no entity setup function having a return type of class or subclass %s' % clazz)
    if len(entities) > 1:
        raise SetupError('To many entities setup functions %r having a return type of class or subclass %s' % 
                         (', '.join(entities), clazz))
    return Assembly.process(entities[0])
