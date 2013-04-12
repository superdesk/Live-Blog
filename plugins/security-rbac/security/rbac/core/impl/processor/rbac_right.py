'''
Created on Feb 21, 2013

@package: support acl
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Processor that populates the rights based on the RBAC structure.
'''

from acl.spec import TypeAcl
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed, Handler
from collections import Iterable
from itertools import chain
from security.rbac.core.spec import IRbacSupport

# --------------------------------------------------------------------

class Solicitation(Context):
    '''
    The solicitation context.
    '''
    # ---------------------------------------------------------------- Required
    rbacId = requires(int, doc='''
    @rtype: integer
    The id of the rbac to fetch the rights for.
    ''')
    types = requires(Iterable, doc='''
    @rtype: Iterable(TypeAcl)
    The ACL types to provide rights for.
    ''')
    # ---------------------------------------------------------------- Defined
    rights = defines(Iterable, doc='''
    @rtype: Iterable(RightAcl)
    The default rights for the types.
    ''')
    
# --------------------------------------------------------------------

@injected
@setup(Handler, name='rbacPopulateRights')
class RbacPopulateRights(HandlerProcessorProceed):
    '''
    Provides the handler that populates the rights based on RBAC structure.
    '''
    
    rbacSupport = IRbacSupport; wire.entity('rbacSupport')
    # Rbac support to use for complex role operations.
    
    def __init__(self):
        assert isinstance(self.rbacSupport, IRbacSupport), 'Invalid rbac support %s' % self.rbacSupport
        super().__init__()
    
    def process(self, solicitation:Solicitation, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Populate the rights.
        '''
        assert isinstance(solicitation, Solicitation), 'Invalid solicitation %s' % solicitation
        assert isinstance(solicitation.rbacId, int), 'Invalid rbac Id %s' % solicitation.rbacId
        
        allTypes, rights, types = {aclType.name: aclType for aclType in solicitation.types}, [], []
        for typeName, names in self.rbacSupport.iterateTypeAndRightsNames(solicitation.rbacId):
            aclType = allTypes.get(typeName)
            if not aclType: continue
            types.append(aclType)
            assert isinstance(aclType, TypeAcl)
            rights.extend(aclType.rightsFor(names))
            
        solicitation.types = types
        if solicitation.rights is not None: solicitation.rights = chain(solicitation.rights, rights)
        else: solicitation.rights = rights
