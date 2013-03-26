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
# Provides the meta object for SQL alchemy

# Important! Removed because the utf8mb4 charset does not permit creating varchar foreign keys
# def after_create(target, connection, **kw):
#    '''
#    Converts tables to utf8mb5 for MySQL dialect and version greater or equal to 5.5.3
#    '''
#    if connection.dialect.server_version_info >= (5, 5, 3):
#        connection.execute("ALTER TABLE %s CONVERT TO CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci'" % target.name)
#
# # Registers event on table creation
# event.listen(Table, "after_create", after_create)

Base = declarative_base(metadata=meta, metaclass=DeclarativeMetaModel)
# Provides the Base for declarative mapping.
