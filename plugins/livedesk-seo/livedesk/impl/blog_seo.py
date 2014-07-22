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
from livedesk.api.blog_seo import IBlogSeoService, QBlogSeo, BlogSeo
from livedesk.meta.blog_post import BlogPostMapped
from livedesk.meta.blog_seo import BlogSeoMapped
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sqlalchemy.sql.expression import or_, func
from ally.container import wire
from ally.cdm.spec import ICDM


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

@setup(IBlogSeoService, name='blogSeoService')
class BlogSeoServiceAlchemy(EntityServiceAlchemy, IBlogSeoService):
    '''
    Implementation for @see IBlogSeoService
    '''
    
    format_file_name = '%(id)s-%(theme_id)s.html'; wire.config('format_file_name', doc='''
    The format for the html files, it can contain blog id, blog title and theme name: %(id)s-%(title)s-%(theme)s.html''')
    html_storage_path = '/seo'; wire.config('html_storage_path', doc='''
    The path where will be stored the generated HTML files''')
    
    htmlCDM = ICDM; wire.entity('htmlCDM')
    # cdm service used to store the generated HTML files

    def __init__(self):
        '''
        Construct the blog seo service.
        '''
        EntityServiceAlchemy.__init__(self, BlogSeoMapped, QBlogSeo)
        
    
    def insert(self, blogSeo):
        '''
        @see: IBlogSeo.insert
        '''
        
        assert isinstance(blogSeo, BlogSeo), 'Invalid blog seo %s' % blogSeo
    
        if blogSeo.NextSync is None:
            blogSeo.NextSync = datetime.datetime.now().replace(microsecond=0)
            
        if blogSeo.LastCId is None:
            blogSeo.LastCId = 0     
            
        blogSeo.ChangedOn = datetime.datetime.now().replace(microsecond=0)  
        path = ''.join((self.html_storage_path, '/', self.format_file_name % {'id': blogSeo.Blog, 'theme_id': blogSeo.BlogTheme} ))  
        blogSeo.HtmlURL = self.htmlCDM.getURI(path)  
        
        return super().insert(blogSeo)
    
        
    def update(self, blogSeo):
        '''
        @see: IBlogSeo.update
        '''
       
        assert isinstance(blogSeo, BlogSeo), 'Invalid blog seo %s' % blogSeo
    
        if blogSeo.LastCId is None:
            blogSeo.LastCId = 0  
            blogSeo.NextSync = datetime.datetime.now().replace(microsecond=0)
            blogSeo.ChangedOn = blogSeo.NextSync  
        
        path = ''.join((self.html_storage_path, '/', self.format_file_name % {'id': blogSeo.Blog, 'theme_id': blogSeo.BlogTheme} ))  
        blogSeo.HtmlURL = self.htmlCDM.getURI(path)
                 
        return super().update(blogSeo)    
    
    
    def getLastCId(self, blogSeo):
        '''
        @see IBlogSeoService.getLastCId
        '''   
        sql = self.session().query(func.max(BlogPostMapped.CId).label("LastCId"))
        sql = sql.filter(BlogSeoMapped.Id == blogSeo.Id)
        blogSeo.LastCId = sql.one()[0]
        return blogSeo
        
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



    
 

