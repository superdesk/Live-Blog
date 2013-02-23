'''
Created on Feb 21, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Processor that adds default Gateway objects.
'''

from ally.api.operator.type import TypeProperty
from ally.container.ioc import injected
from ally.container.support import setup
from ally.design.processor.attribute import defines, requires
from ally.design.processor.context import Context
from ally.design.processor.execution import Chain
from ally.design.processor.handler import HandlerProcessor, Handler
from ally.support.sqlalchemy.session import SessionSupport
from collections import Callable
from sqlalchemy.orm.exc import NoResultFound
from superdesk.security.meta.security_intern import RbacUser
from superdesk.user.api.user import User

# --------------------------------------------------------------------
    
class Solicitation(Context):
    '''
    The solicitation context.
    '''
    # ---------------------------------------------------------------- Required
    userId = requires(int, doc='''
    @rtype: integer
    The user id to create gateways for.
    ''')
    # ---------------------------------------------------------------- Defined
    rbacId = defines(int, doc='''
    @rtype: integer
    The id of the rbac to create gateways for.
    ''')
    provider = defines(Callable, doc='''
    @rtype: callable(TypeProperty) -> string|None
    Callable used for getting the authenticated value.
    ''')
    
# --------------------------------------------------------------------

@injected
@setup(Handler, name='userRbacProvider')
class UserRbacProvider(HandlerProcessor, SessionSupport):
    '''
    Provides the handler that extracts the rbac id for the user id.
    '''
    
    def process(self, chain, solicitation:Solicitation, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Populate the rbac id.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(solicitation, Solicitation), 'Invalid solicitation %s' % solicitation
        assert isinstance(solicitation.userId, int), 'Invalid solicitation user id %s' % solicitation.userId

        try: solicitation.rbacId, = self.session().query(RbacUser.Id).filter(RbacUser.userId == solicitation.userId).one()
        except NoResultFound: return
        solicitation.provider = UserProvider(str(solicitation.userId))
        
        chain.proceed()

# --------------------------------------------------------------------

class UserProvider:
    '''
    Implementation for @see: IAuthenticatedProvider that provides the authenticated user id.
    '''
    __slots__ = ('userId',)
    
    def __init__(self, userId):
        '''
        Construct the provider for the user id.
        
        @param userId: string
            The user id.
        '''
        assert isinstance(userId, str), 'Invalid user id %s' % userId
        self.userId = userId
    
    def __call__(self, propertyType):
        '''
        Provide the value for the property type.
        '''
        assert isinstance(propertyType, TypeProperty), 'Invalid property type %s' % propertyType
        if propertyType.parent.clazz == User or issubclass(propertyType.parent.clazz, User): return self.userId
        
