'''
Created on Apr 19, 2012

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Meta data definition package.
'''

from sqlalchemy.schema import MetaData
from sqlalchemy.ext.declarative import declarative_base
from ally.support.sqlalchemy.mapper import DeclarativeMetaModel

# --------------------------------------------------------------------

meta = MetaData()
# Provides the meta object for SQL alchemy.

Base = declarative_base(metadata=meta, metaclass=DeclarativeMetaModel)
# Provides the Base for declarative mapping.
