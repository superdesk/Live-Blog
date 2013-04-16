'''
Created on Feb 21, 2013

@package: support acl
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Processor that adds default rights from the ACL types.
'''

from acl.spec import TypeAcl
from ally.container.ioc import injected
from ally.container.support import setup
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed, Handler
from collections import Iterable
from itertools import chain

# --------------------------------------------------------------------

class Solicitation(Context):
    '''
    The solicitation context.
    '''
    
    # ---------------------------------------------------------------- Required
    types = requires(Iterable, doc='''
    @rtype: Iterable(TypeAcl)
    The ACL types to add the default rights for.
    ''')
    # ---------------------------------------------------------------- Defined
    rights = defines(Iterable, doc='''
    @rtype: Iterable(RightAcl)
    The default rights for the types.
    ''')
    
# --------------------------------------------------------------------

@injected
@setup(Handler, name='registerDefaultRights')
class RegisterDefaultRights(HandlerProcessorProceed):
    '''
    Provides the handler that populates the default rights for ACL types.
    '''
    
    def process(self, solicitation:Solicitation, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Adds the default rights.
        '''
        assert isinstance(solicitation, Solicitation), 'Invalid solicitation %s' % solicitation
        if solicitation.types is None: return
        
        rights = []
        for typeAcl in solicitation.types:
            assert isinstance(typeAcl, TypeAcl), 'Invalid ACL type %s' % typeAcl
            rights.extend(typeAcl.defaults)
        
        if solicitation.rights is not None: solicitation.rights = chain(solicitation.rights, rights)
        else: solicitation.rights = rights
