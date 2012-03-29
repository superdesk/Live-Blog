'''
Created on Mar 6, 2012

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

@author: Mihai Balaceanu
'''
from superdesk.person.api.person import IPersonService
from ally.container.ioc import injected
from sql_alchemy.impl.entity import EntityServiceAlchemy
from ..meta.person import Person, QPerson
from superdesk.user.meta.user import User

# --------------------------------------------------------------------

@injected
class PersonServiceAlchemy(EntityServiceAlchemy, IPersonService):
    '''
    @see: IUserService
    '''
    def __init__(self):
        EntityServiceAlchemy.__init__(self, Person, QPerson)
        
    def getByUser(self, idUser):
        '''
        @see: IUserService.getByUser
        '''
        sqlQuery = self.session().query(Person).join(User)
        return self._getAll(User.Id == idUser, sqlQuery=sqlQuery)
