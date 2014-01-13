'''
Created on Oct 1, 2012

@package: airtime file
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Airtime database mapping for the file model.
'''

from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer
from superdesk.airtime.api.file import File
from superdesk.meta.metadata_superdesk import Base

# --------------------------------------------------------------------

class FileMapped(Base, File):
    '''
    Provides the mapping for MetaData.
    '''
    __tablename__ = 'cc_files'

    Id = Column('id', Integer, primary_key=True)
    Name = Column('name', String(255), nullable=False, default='')
