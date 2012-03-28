'''
Created on Mar 7, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for localized files.
'''

from ally.api.config import service, query
from ally.api.criteria import AsLike, AsDateTime
from introspection.api import modelDevel
from introspection.api.plugin import Plugin
from sql_alchemy.api.entity import Entity, QEntity, IEntityService
from introspection.api.component import Component
from datetime import datetime

# --------------------------------------------------------------------

@modelDevel
class File(Entity):
    '''
    Model for the files.
    '''
    Component = Component
    Plugin = Plugin
    Path = str
    LastModified = datetime

# --------------------------------------------------------------------

@query
class QFile(QEntity):
    '''
    Provides the query for the files.
    '''
    component = AsLike
    plugin = AsLike
    path = AsLike
    lastModified = AsDateTime

# --------------------------------------------------------------------

@service((Entity, File), (QEntity, QFile))
class IFileService(IEntityService):
    '''
    The files service.
    '''
