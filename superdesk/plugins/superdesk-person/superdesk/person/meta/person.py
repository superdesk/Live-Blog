'''
Created on Aug 23, 2011

@package: superdesk person
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Contains the SQL alchemy meta for person API.
'''

from ..api.person import Person
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import Base
from sqlalchemy.ext.hybrid import hybrid_property
from ally.container.binder_op import validateManaged
from ally.support.sqlalchemy.mapper import registerValidation
from sqlalchemy.orm.mapper import reconstructor

# --------------------------------------------------------------------

class PersonMapped(Base, Person):
    '''
    Provides the mapping for Person entity.
    '''
    __tablename__ = 'person'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    FirstName = Column('first_name', String(255))
    LastName = Column('last_name', String(255))
    Address = Column('address', String(255))

    # Calculated model attributes ------------------------------------
    @hybrid_property
    def Name(self):
        name = '%s %s' % ('' if self.FirstName is None else self.FirstName,
                          '' if self.LastName is None else self.LastName)
        #TODO: remove
        print('name: %s' % name)
        return name.strip()

#    @reconstructor
#    def init_on_load(self):
#        self.Name = '%s %s' % ('' if self.FirstName is None else self.FirstName,
#                               '' if self.LastName is None else self.LastName)
#        self.Name = self.Name.strip()

#validateManaged(PersonMapped.Name)
#registerValidation(PersonMapped)
