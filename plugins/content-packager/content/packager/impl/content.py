'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for content.
'''

from ally.container.support import setup
from content.packager.api.content import IContentService
from sql_alchemy.impl.entity import EntityServiceAlchemy

# --------------------------------------------------------------------

@setup(IContentService, name='contentService')
class GroupServiceAlchemy(EntityServiceAlchemy, IContentService):
    '''
    Implementation for @see: IContentService
    '''
