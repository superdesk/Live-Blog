'''
Created on Mar 14, 2013

@package: content article file
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for article file.
'''

from ally.container.support import setup
from sql_alchemy.impl.entity import EntityServiceAlchemy
from content.article.api.article import IArticleService
from ally.container.ioc import injected
from ally.container import wire
from content.article.api.article_file import IArticleFileService, QArticleFile
from content.article.meta.article_file import ArticleFileMapped

# --------------------------------------------------------------------

@injected
@setup(IArticleFileService, name='articleFileService')
class ArticleFileServiceAlchemy(EntityServiceAlchemy, IArticleFileService):
    '''
    Implementation for @see: IArticleFileService
    '''

    articleService = IArticleService; wire.entity('articleService')
    # TODO: comment

    def __init__(self):
        '''
        Construct the article file service.
        '''
        EntityServiceAlchemy.__init__(self, ArticleFileMapped, QArticleFile)
