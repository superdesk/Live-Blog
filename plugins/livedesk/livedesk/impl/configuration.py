'''
Created on May 22, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for blog configuration API.
'''

# --------------------------------------------------------------------

impl = createConfigurationImpl(IBlogConfigurationService, BlogConfigurationMapped)

#@injected
#@setup(IBlogConfigurationService, name='blogConfigurationService')
#class BlogConfigurationServiceAlchemy(SessionSupport, IBlogConfigurationService):
#    '''
#    Implementation for @see: IBlogConfigurationService
#    '''
#
#    def __init__(self):
#        '''
#        Construct the blog configuration service.
#        '''
#        ConfigurationServiceAlchemy.__init__(self, BlogConfigurationMapped, QBlogConfiguration)

