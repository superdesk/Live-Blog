'''
Created on December 20, 2012

@package: url info
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for URL info service.
'''

from ally.api.config import service, call
from ally.api.type import Reference, List
from superdesk.api.domain_superdesk import model
from datetime import datetime

# --------------------------------------------------------------------

@model(id='URL')
class URLInfo:
    '''
    Provides the URL info model.
    '''
    URL = Reference
    ContentType = str
    Title = str
    Description = str
    SiteIcon = Reference
    Date = datetime
    Picture = List(Reference)

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service
class IURLInfoService:
    '''
    Provides the service methods for URL info.
    '''

    @call
    def getURLInfo(self, url:URLInfo.URL) -> URLInfo:
        '''
        Provides the info entity based on the URL.

        @param url: URLInfo.Reference
            The url for which to return information.
        @raise InputError: If the URL is not valid.
        '''
