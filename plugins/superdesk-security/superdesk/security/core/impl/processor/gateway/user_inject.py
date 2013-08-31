'''
Created on Aug 31, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Processor that provides the user id to be injected in filters.
'''

from ally.container.support import setup
from ally.design.processor.attribute import defines, requires
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessor, Handler
from superdesk.security.core.spec import AUTHENTICATED_NAME

# --------------------------------------------------------------------
    
class Solicit(Context):
    '''
    The solicit context.
    '''
    # ---------------------------------------------------------------- Defined
    replacements = defines(dict, doc='''
    @rtype: dictionary{string: object}
    The replacements for the markers in the filters paths.
    ''')
    # ---------------------------------------------------------------- Required
    acl = requires(object)
    
# --------------------------------------------------------------------

@setup(Handler, name='userInject')
class UserInjectHandler(HandlerProcessor):
    '''
    Provides the user id to be injected in filters.
    '''
    
    def process(self, chain, solicit:Solicit, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Adds the access permissions gateways.
        '''
        assert isinstance(solicit, Solicit), 'Invalid solicit %s' % solicit
        assert  isinstance(solicit.acl, int), 'Invalid acl value %s' % solicit.acl
        if solicit.replacements is None: solicit.replacements = {}
        solicit.replacements[AUTHENTICATED_NAME] = solicit.acl