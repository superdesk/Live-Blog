'''
Created on May 2, 2012

@package: superdesk collaborator
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for source API.
'''

from ..api.collaborator import Collaborator
from ally.support.sqlalchemy.mapper import validate
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.sql.expression import case
from superdesk.meta.metadata_superdesk import Base
from superdesk.person.meta.person import PersonMapped
from superdesk.source.meta.source import SourceMapped

# --------------------------------------------------------------------

@validate
class CollaboratorMapped(Base, Collaborator):
    '''
    Provides the mapping for Collaborator.
    '''
    __tablename__ = 'collaborator'
    __table_args__ = (UniqueConstraint('fk_person_id', 'fk_source_id', name='uix_1'), dict(mysql_engine='InnoDB'))

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Person = Column('fk_person_id', ForeignKey(PersonMapped.Id, ondelete='CASCADE'))
    Source = Column('fk_source_id', ForeignKey(SourceMapped.Id, ondelete='RESTRICT'), nullable=False)
    @hybrid_property
    def Name(self):
        if self.Person is None: return self.source.Name
        return self.person.FullName

    # Non REST model attributes --------------------------------------
    person = relationship(PersonMapped, uselist=False, lazy='joined')
    source = relationship(SourceMapped, uselist=False, lazy='joined')

    # Expression for hybrid ------------------------------------
    Name.expression(lambda cls: case([(cls.Person == None, SourceMapped.Name)], else_=PersonMapped.FirstName))
