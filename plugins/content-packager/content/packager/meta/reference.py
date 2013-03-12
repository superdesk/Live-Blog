'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

Contains SQL alchemy meta for reference API.
'''

from ally.support.sqlalchemy.mapper import validate
from superdesk.meta.metadata_superdesk import Base
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer
from content.packager.api.reference import Reference

# --------------------------------------------------------------------

@validate
class ReferenceMapped(Base, Reference):
    '''
    Provides the mapping for Reference.
    '''
    __tablename__ = 'reference'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Idref = Column('idref', String(255), primary_key=True)
    ItemClass = Column('item_class', String(255))
    ResidRef = Column('resid_ref', String(1000))
    Href = Column('href', String(1000))
    Size = Column('size', Integer(unsigned=True))
    Rendition = Column('rendition', String(1000))
    ContentType = Column('content_type', String(255))
    Format = Column('format', String(255))
