'''
Created on Mar 6, 2012

@package: superdesk person
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

SQL alchemy implementation for person APIs.
'''
from superdesk.person.api.person import IPersonService, QPerson
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.entity import EntityServiceAlchemy
from ..meta.person import PersonMapped

# --------------------------------------------------------------------

@injected
@setup(IPersonService, name='personService')
class PersonServiceAlchemy(EntityServiceAlchemy, IPersonService):
    '''
    Implementation for @see: IPersonService
    '''
    def __init__(self):
        EntityServiceAlchemy.__init__(self, PersonMapped, QPerson)
