'''
Created on Mar 6, 2012

@package: superdesk person
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

APIs for person.
'''

from ally.api.config import service, query
from ally.api.criteria import AsLikeOrdered
from ally.support.api.entity_ided import Entity, IEntityService, QEntity
from superdesk.api.domain_superdesk import modelHR

# --------------------------------------------------------------------

@modelHR
class Person(Entity):
    '''    
    Provides the person model.
    '''
    FirstName = str
    LastName = str
    FullName = str
    Address = str
    EMail = str
    PhoneNumber = str

# --------------------------------------------------------------------

@query(Person)
class QPerson(QEntity):
    '''
    Query for person service
    '''
    firstName = AsLikeOrdered
    lastName = AsLikeOrdered
    email = AsLikeOrdered
    phoneNumber = AsLikeOrdered

# --------------------------------------------------------------------

@service((Entity, Person), (QEntity, QPerson))
class IPersonService(IEntityService):
    '''
    Person model service interface
    '''
