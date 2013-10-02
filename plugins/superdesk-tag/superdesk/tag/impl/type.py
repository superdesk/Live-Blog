'''
Created on August 26, 2013

@package: superdesk tag
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for superdesk tag types API.
'''

from superdesk.tag.api.type import ITagTypeService
from superdesk.tag.meta.type import TagTypeMapped
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.keyed import EntityGetServiceAlchemy, EntityFindServiceAlchemy

# --------------------------------------------------------------------

@injected
@setup(ITagTypeService, name='tagTypeService')
class TagTypeServiceAlchemy(EntityGetServiceAlchemy, EntityFindServiceAlchemy, ITagTypeService):
    '''
    Implementation for @see: ITagTypeService
    '''

    def __init__(self):
        '''
        Construct the tag type service.
        '''
        EntityGetServiceAlchemy.__init__(self, TagTypeMapped)
