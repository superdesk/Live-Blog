'''
Created on May 3, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy implementation for post type API.
'''

from ..api.type import IPostTypeService
from ..meta.type import PostTypeMapped
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.keyed import EntityGetServiceAlchemy, \
    EntityFindServiceAlchemy

# --------------------------------------------------------------------

@injected
@setup(IPostTypeService, name='postTypeService')
class PostTypeServiceAlchemy(EntityGetServiceAlchemy, EntityFindServiceAlchemy, IPostTypeService):
    '''
    Implementation for @see: IPostTypeService
    '''

    def __init__(self):
        '''
        Construct the post type service.
        '''
        EntityGetServiceAlchemy.__init__(self, PostTypeMapped)
