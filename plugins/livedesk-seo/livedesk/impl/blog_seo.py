'''
Created on Feb 5, 2014

@package: livedesk
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API implementation for liveblog seo.
'''

import datetime
import logging

from ally.api.extension import IterPart
from ally.container.support import setup
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from livedesk.api.blog_seo import IBlogSeoService, QBlogSeo
from livedesk.meta.blog_post import BlogPostMapped
from livedesk.meta.blog_seo import BlogSeoMapped
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sqlalchemy.sql.expression import or_


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

@setup(IBlogSeoService, name='blogSeoService')
class BlogSeoServiceAlchemy(EntityServiceAlchemy, IBlogSeoService):
    '''
    Implementation for @see IBlogSeoService
    '''

    def __init__(self):
        '''
        Construct the blog seo service.
        '''
        EntityServiceAlchemy.__init__(self, BlogSeoMapped, QBlogSeo)
        
        
    def getAll(self, blogId=None, themeId=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IBlogSeo.getAll
        '''     
        
        sql = self.session().query(BlogSeoMapped)
        
        if blogId: sql = sql.filter(BlogSeoMapped.Blog == blogId)
        if themeId: sql = sql.filter(BlogSeoMapped.BlogTheme == themeId)
        
        if q:
            assert isinstance(q, QBlogSeo), 'Invalid query %s' % q
            sql = buildQuery(sql, q, BlogSeoMapped)
       
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all() 
        
    def existsChanges(self, blogSeoId, lastCId):
        '''
        @see IBlogSeoService.checkChanges
        '''  
        sql = self.session().query(BlogPostMapped)
        sql = sql.filter(BlogPostMapped.Blog == blogSeoId)
        sql = sql.filter(BlogPostMapped.CId > lastCId)
        
        return sql.first() != None       
        
    def checkTimeout(self, blogSeoId, timeout):
        '''
        @see IBlogSeoService.checkTimeout
        '''  
        crtTime = datetime.datetime.now().replace(microsecond=0)  
        referenceTime = crtTime - datetime.timedelta(seconds=timeout)
        
        sql = self.session().query(BlogSeoMapped)
        sql = sql.filter(BlogSeoMapped.Id == blogSeoId)
        sql = sql.filter(or_(BlogSeoMapped.LastBlocked == None, BlogSeoMapped.LastBlocked < referenceTime))
        result = sql.update({BlogSeoMapped.LastBlocked : crtTime}) 
        self.session().commit()       

        return result
    
    def updateNextSync(self, blogSeoId, nextSync):
        '''
        @see IBlogSeoService.checkTimeout
        '''   
        sql = self.session().query(BlogSeoMapped)
        sql = sql.filter(BlogSeoMapped.Id == blogSeoId)
        
        sql.update({BlogSeoMapped.NextSync : nextSync}) 
        self.session().commit()       

    

    
 

