'''
Created on May 2, 2012

@package: superdesk collaborator
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for source API.
'''

from ..api.collaborator import Collaborator
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from superdesk.meta.metadata_superdesk import Base
from superdesk.person.meta.person import Person
from superdesk.source.meta.source import SourceMapped

# --------------------------------------------------------------------

class CollaboratorMapped(Base, Collaborator):
    '''
    Provides the mapping for Collaborator.
    '''
    __tablename__ = 'collaborator'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Person = Column('fk_person_id', ForeignKey(Person.Id, ondelete='CASCADE'))
    Source = Column('fk_source_id', ForeignKey(SourceMapped.Id, ondelete='RESTRICT'), nullable=False)
