'''
Created on May 22, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for configurations API.
'''

from sqlalchemy.schema import Column
from sqlalchemy.types import String
from sqlalchemy.ext.declarative import declared_attr

# --------------------------------------------------------------------

class ConfigurationDescription:
    '''
    Provides abstract mapping for Configuration.
    '''
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Name = declared_attr(lambda cls: Column('name', String(255), primary_key=True))
    Value = declared_attr(lambda cls: Column('value', String(1024)))
    # None REST model attribute --------------------------------------
    parent = declared_attr(lambda(cls: raise Exception('Use a derived class')))

