'''
Created on Aug 31, 2013

@package: superdesk security
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Register the user inject into filters invokers.
'''

from ally.api.operator.type import TypeProperty
from ally.container.ioc import injected
from ally.container.support import setup
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessor, Handler
from ally.support.api.util_service import isCompatible
from superdesk.security.core.spec import AUTHENTICATED_MARKER
from superdesk.user.api.user import User
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Register(Context):
    '''
    The register context.
    '''
    # ---------------------------------------------------------------- Required
    invokers = requires(list)
    
class Invoker(Context):
    '''
    The invoker context.
    '''
    # ---------------------------------------------------------------- Defined
    filterInjected = defines(dict, doc='''
    @rtype: dictionary{Context: string}
    A dictionary containing as a key the path elements that are injected and as a value the marker to place in path.
    ''')
    # ---------------------------------------------------------------- Required
    path = requires(list)
    filterName = requires(str)

class Element(Context):
    '''
    The element context.
    '''
    # ---------------------------------------------------------------- Required
    property = requires(TypeProperty)

# --------------------------------------------------------------------

@injected
@setup(Handler, name='filterUserInject')
class FilterUserInjectHandler(HandlerProcessor):
    '''
    Implementation for a processor that register the user injection for filters.
    '''
    
    def __init__(self):
        super().__init__(Invoker=Invoker, Element=Element)

    def process(self, chain, register:Register, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Register the user injection for filters.
        '''
        assert isinstance(register, Register), 'Invalid register %s' % register
        if not register.invokers: return
        
        for invoker in register.invokers:
            assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
            if invoker.filterName is None: continue
            
            pelements = [el for el in invoker.path if el.property]
            if len(pelements) < 2: continue
            
            for el in pelements:
                assert isinstance(el, Element), 'Invalid element %s' % el
                if not isCompatible(User.Id, el.property): continue
                if invoker.filterInjected is None: invoker.filterInjected = {}
                invoker.filterInjected[el] = AUTHENTICATED_MARKER
                break  # We only register for the first user id.
