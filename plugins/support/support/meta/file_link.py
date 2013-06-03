'''
Created on May 28, 2013

@package: support
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for file-info links API.
'''

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from superdesk.media_archive.meta.meta_info import MetaInfoMapped

# --------------------------------------------------------------------

def abstractMapping(): raise Exception('Use a derived class')

class FileLinkDescription:
    '''
    Provides abstract mapping for FileLinks.
    '''
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    file = declared_attr(lambda cls: Column('meta_data', ForeignKey(MetaInfoMapped.Id, ondelete='CASCADE'), primary_key=True))
    parent = declared_attr(lambda cls: abstractMapping())

