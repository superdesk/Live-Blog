'''
Created on Mar 6, 2012

@package: superdesk person
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

APIs for person.
'''
from superdesk.api import modelSuperDesk
from ally.api.config import service, query
from sql_alchemy.api.entity import Entity, IEntityService, QEntity
from ally.api.criteria import AsLike

# --------------------------------------------------------------------

@modelSuperDesk
class Person(Entity):
    '''    
    Provides the person model.
    '''
    FirstName = str
    LastName = str
    Address = str

# --------------------------------------------------------------------

@query
class QPerson(QEntity):
    '''
    Query for person service
    '''
    firstName = AsLike
    lastName = AsLike

# --------------------------------------------------------------------

@service((Entity, Person), (QEntity, QPerson))
class IPersonService(IEntityService):
    '''
    Person model service interface
    '''
