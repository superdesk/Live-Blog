'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Meta data definition package.
'''

from sqlalchemy.schema import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sql_alchemy.support.mapper import DeclarativeMetaModel

# --------------------------------------------------------------------

meta = MetaData()
# Provides the meta object for SQL alchemy

Base = declarative_base(metadata=meta, metaclass=DeclarativeMetaModel)
# Provides the Base for declarative mapping.
