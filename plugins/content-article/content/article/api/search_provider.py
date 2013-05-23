'''
Created on Mar 21, 2013

@package: content article
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API for article search provider.
'''
from content.article.api.article import Article

class IArticleSearchProvider:
    '''
    Provides the methods for search related functionality.
    '''

    def buildQuery(self, session, scheme, offset, limit, q=None):
        '''
        Provides the query for the articles based on received criteria.
        '''

    # --------------------------------------------------------------------

    def update(self, article:Article):
        '''
        Provides the update of data on search indexes.
        '''

    # --------------------------------------------------------------------

    def delete(self, id:Article.Id):
        '''
        Provides the delete of data from search indexes.
        '''
        