'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the meta type API. 
'''

from ..api.meta_type import IMetaTypeService
from ..meta.meta_type import MetaType
from ally.container.ioc import injected
from sql_alchemy.impl.entity import EntityNQServiceAlchemy

# --------------------------------------------------------------------

@injected
class MetaTypeServiceAlchemy(EntityNQServiceAlchemy, IMetaTypeService):
    '''
    @see: IMetaTypeService
    '''

    def __init__(self):
        EntityNQServiceAlchemy.__init__(self, MetaType)
