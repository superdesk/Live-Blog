'''
Created on Aug 23, 2011

@package: superdesk person
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Contains the SQL alchemy meta for person API.
'''

from ..api.person import Person
from ally.support.sqlalchemy.mapper import validate
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column
from sqlalchemy.sql.expression import case
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import Base

# --------------------------------------------------------------------

@validate
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
    EMail = Column('email', String(255))
    PhoneNumber = Column('phone_number', String(255), nullable=True, unique=True)
    @hybrid_property
    def FullName(self):
        if self.FirstName is None: return self.LastName
        if self.LastName is None: return self.FirstName
        return self.FirstName + ' ' + self.LastName

    # Expression for hybrid ------------------------------------
    FullName.expression = lambda cls : case([(cls.FirstName == None, cls.LastName)], else_=
                                            case([(cls.LastName == None, cls.FirstName)], else_=
                                                 cls.FirstName + ' ' + cls.LastName))
