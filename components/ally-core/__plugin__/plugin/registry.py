'''
Created on Jan 12, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup registry for the plugins.
'''

from __setup__.ally_core.resources import services
from ally.container.bind import processBinders
from ally.container.impl.proxy import proxyWrapFor
from functools import partial

# --------------------------------------------------------------------

def registerService(service, binders=None):
    '''
    A listener to register the service.
    
    @param service: object
        The service instance to be registered.
    @param binders: list[Callable]|tuple(Callable)
        The binders used for the registered services.
    '''
    if binders:
        service = proxyWrapFor(service)
        if binders:
            for binder in binders: binder(service)
    services().append(service)

def addService(*binders):
    '''
    Create listener to register the service with the provided binders.
    
    @param binders: arguments[Callable]
        The binders used for the registered services.
    '''
    binders = processBinders(binders)
    assert binders, 'At least a binder is required, if you want the register without binders use the \'registerService\' function'
    return partial(registerService, binders=binders)

