'''
Created on Apr 19, 2012

@package: security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

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
