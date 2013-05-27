'''
Created on May 24, 2013

@package: content newsml
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Specifications for the newsml content export.
'''

from ally.api.config import service, call
from ally.api.type import Reference, Scheme
from content.packager.api.domain_content import modelContent

# --------------------------------------------------------------------

@modelContent(id='GUId')
class ItemNewsML:
    '''
    The item NewsML export model.
    '''
    GUId = str
    NewsML = Reference

# --------------------------------------------------------------------

@service
class IItemNewsMLService:
    '''
    The item NewsML export service.
    '''

    @call
    def getNewsML(self, guid:ItemNewsML.GUId, scheme:Scheme) -> ItemNewsML.NewsML:
        '''
        Provides the NewsML export for the provided item GUID.
        '''
