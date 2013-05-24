'''
Created on May 22, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for blog configuration API.
'''

from ..api.configuration import IBlogConfigurationService
from ..meta.configuration import BlogConfigurationMapped
#from support.impl.configuration import createConfigurationImpl
from support.impl.configuration import ConfigurationServiceAlchemy
from ally.container.ioc import injected
from ally.container.support import setup

# --------------------------------------------------------------------

@injected
@setup(IBlogConfigurationService, name='blogConfigurationService')
class BlogConfigurationServiceAlchemy(ConfigurationServiceAlchemy, IBlogConfigurationService):
    '''
    Implementation for @see: IBlogConfigurationService
    '''

    ConfigurationMapped = BlogConfigurationMapped
    # actual DB mapping class to be used

'''
@injected
@setup(IBlogConfigurationService, name='blogConfigurationService')
createConfigurationImpl(IBlogConfigurationService, BlogConfigurationMapped)
'''
