'''
Created on Mar 14, 2013

@package: content article
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the services for content article.
'''

from ..plugin.registry import addService
from ..superdesk.db_superdesk import bindSuperdeskSession, bindSuperdeskValidations
from ally.container import support, bind, ioc
from itertools import chain
from content.article.api.search_provider import IArticleSearchProvider
from content.article.impl.db_search import SqlArticleSearchProvider


# --------------------------------------------------------------------

SERVICES = 'content.article.api.**.I*Service'
@ioc.entity
def binders(): return [bindSuperdeskSession]
@ioc.entity
def bindersService(): return list(chain((bindSuperdeskValidations,), binders()))

bind.bindToEntities('content.article.impl.**.*Alchemy', binders=binders)
support.createEntitySetup('content.article.impl.**.*')
support.listenToEntities(SERVICES, listeners=addService(bindersService))
support.loadAllEntities(SERVICES)

@ioc.config
def article_search_provider():
    ''' Specify the search provider that will be used for articles. The possible values are db for database provider and solr for solr provider'''
    return 'db'

# --------------------------------------------------------------------

@ioc.entity
def articleSearchProvider() -> IArticleSearchProvider:

    if article_search_provider() == 'solr':
        from content.article.impl.solr_search import SolrArticleSearchProvider
        b = SolrArticleSearchProvider()
    else:
        b = SqlArticleSearchProvider()

    return b

# --------------------------------------------------------------------