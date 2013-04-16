'''
Created on Mar 6, 2012

@package: superdesk person
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the implementation for right.
'''

from ..api.right_type import IRightTypeService, RightType
from ..meta.right_type import RightTypeMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from sql_alchemy.impl.entity import EntityNQServiceAlchemy
from sqlalchemy.orm.exc import NoResultFound

# --------------------------------------------------------------------

@injected
@setup(IRightTypeService, name='rightTypeService')
class RightTypeServiceAlchemy(EntityNQServiceAlchemy, IRightTypeService):
    '''
    @see: IRightTypeService
    '''
    
    def __init__(self):
        EntityNQServiceAlchemy.__init__(self, RightTypeMapped)
        
    def getByName(self, name):
        '''
        @see: IRightTypeService.getByName
        '''
        try: return self.session().query(RightTypeMapped).filter(RightTypeMapped.Name == name).one()
        except NoResultFound: raise InputError(Ref(_('Unknown name'), ref=RightType.Name))
