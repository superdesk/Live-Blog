'''
Created on Feb 5, 2014

@package: livedesk
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API implementation of liveblog seo.
'''

import datetime
import logging
from sched import scheduler
import socket
from threading import Thread
import time
from urllib.error import HTTPError
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from urllib.request import urlopen, Request

from ally.container import wire, app
from ally.container.ioc import injected
from ally.container.support import setup
from livedesk.api.blog_seo import BlogSeo, IBlogSeoService, QBlogSeo
from livedesk.api.blog_theme import IBlogThemeService
from ally.cdm.spec import ICDM
from livedesk.api.blog import IBlogService


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(name='seoSynchronizer')
class SeoSyncProcess:
    '''
    Seo sync process.
    '''

    blogSeoService = IBlogSeoService; wire.entity('blogSeoService')
    # blog seo service used to retrieve blogs set on auto publishing

    blogService = IBlogService; wire.entity('blogService')
    # blog service used to get the blog name
    
    blogThemeService = IBlogThemeService; wire.entity('blogThemeService')
    # blog theme service used to get the theme name
    
    htmlCDM = ICDM; wire.entity('htmlCDM')
    # cdm service used to store the generated HTML files
    
    syncThreads = {}
    # dictionary of threads that perform synchronization

    seo_sync_interval = 60; wire.config('seo_sync_interval', doc='''
    The number of seconds to perform sync for seo blogs.''')
    
    timeout_inteval = 3600#; wire.config('timeout_interval', doc='''
    #The number of seconds after the sync ownership can be taken.''')
    
    html_generation_server = 'http://nodejs-dev.sourcefabric.org'; wire.config('html_generation_server', doc='''
    The partial path used to construct the URL for blog html generation''')
    
    html_storage_path = '/seo'; wire.config('html_storage_path', doc='''
    The path where will be stored the generated HTML files''')
    
    host_url = 'http://liveblog16.sd-test.sourcefabric.org'; wire.config('host_url', doc='''
    The external URL of the live blog instance''')
    
    format_file_name = '%(id)s.html'; wire.config('format_file_name', doc='''
    The format for the html files, it can contain blog id, blog title and theme name: %(id)s-%(title)s-%(theme)s.html''')

    acceptType = 'text/json'
    # mime type accepted for response from remote blog
    encodingType = 'UTF-8'
    # character encoding type accepted for response from remove blog
    


    @app.deploy
    def startSeoSyncThread(self):
        '''
        Starts the seo sync thread.
        '''
        schedule = scheduler(time.time, time.sleep)
        def syncSeoBlogs():
            self.syncSeoBlogs()
            schedule.enter(self.seo_sync_interval, 1, syncSeoBlogs, ())
        schedule.enter(self.seo_sync_interval, 1, syncSeoBlogs, ())
        scheduleRunner = Thread(name='blog html for seo', target=schedule.run)
        scheduleRunner.daemon = True
        scheduleRunner.start()
        log.info('Started the blogs automatic html synchronization.')

    def syncSeoBlogs(self):
        '''
        Read all chained blog sync entries and sync with the corresponding blogs.
        '''
        
        crtTime = datetime.datetime.now().replace(microsecond=0) 
        
        q = QBlogSeo(refreshActive=True)
        q.nextSync.until = crtTime
        
        for blogSeo in self.blogSeoService.getAll(q=q): 
            assert isinstance(blogSeo, BlogSeo)
            
            nextSync = crtTime + datetime.timedelta(seconds=blogSeo.RefreshInterval)
            self.blogSeoService.updateNextSync(blogSeo.Id, nextSync) 
            
            if not self.blogSeoService.existsChanges(blogSeo.Id, blogSeo.LastCId): continue
            
            key = (blogSeo.Blog, blogSeo.BlogTheme)
            thread = self.syncThreads.get(key)
            if thread:
                assert isinstance(thread, Thread), 'Invalid thread %s' % thread
                if thread.is_alive(): continue

                if not self.blogSeoService.checkTimeout(blogSeo.Id, self.timeout_inteval): continue

            self.syncThreads[key] = Thread(name='blog %d seo' % blogSeo.Blog,
                                           target=self._syncSeoBlog, args=(blogSeo,))
            self.syncThreads[key].daemon = True
            self.syncThreads[key].start()
            log.info('Thread started for blog id %d and theme id %d', blogSeo.Blog, blogSeo.BlogTheme)   


    def _syncSeoBlog(self, blogSeo):
        '''
        Synchronize the blog for the given sync entry.

        @param blogSync: BlogSync
            The blog sync entry declaring the blog and source from which the blog
            has to be updated.
        '''
        assert isinstance(blogSeo, BlogSeo), 'Invalid blog seo %s' % blogSeo
        
        self.blogSeoService.getLastCId(blogSeo)
        blog = self.blogService.getBlog(blogSeo.Blog)
        theme = self.blogThemeService.getById(blogSeo.BlogTheme)
                   
        (scheme, netloc, path, params, query, fragment) = urlparse(self.html_generation_server)

        q = parse_qsl(query, keep_blank_values=True)
        q.append(('id', blogSeo.Blog))
        q.append(('theme', theme.Name))
        q.append('host', self.host_URL)
        if blogSeo.MaxPosts is not None:
            q.append(('limit', blogSeo.MaxPosts))

        url = urlunparse((scheme, netloc, path, params, urlencode(q), fragment))
        req = Request(url, headers={'Accept' : self.acceptType, 'Accept-Charset' : self.encodingType,
                                    'User-Agent' : 'Magic Browser'})
        
        try: resp = urlopen(req)
        except (HTTPError, socket.error) as e:
            log.error('Read error on %s: %s' % (self.html_generation_server, e))
            blogSeo.LastBlocked = None 
            self.blogSeoService.update(blogSeo)
            return
        
        if str(resp.status) != '200':
            log.error('Read problem on %s, status: %s' % (self.html_generation_server, resp.status))
            blogSeo.LastBlocked = None 
            self.blogSeoService.update(blogSeo)
            return
 
        try: 
            path = self.format_file_name % {'id': blogSeo.Blog, 'title': blog.Title, 'theme': theme.Name}
            path = ''.join((self.html_storage_path, '/', path))
        
            self.htmlCDM.publishContent(path, resp) 
        except ValueError as e:
            log.error('Fail to publish the HTML file on CDM %s' % e)
            blogSeo.LastBlocked = None 
            self.blogSeoService.update(blogSeo)
            return
        
        blogSeo.HtmlURL = self.htmlCDM.getURI(path)

        if blogSeo.CallbackActive:
            (scheme, netloc, path, params, query, fragment) = urlparse(blogSeo.CallbackURL)
            
            if not scheme: scheme = self.schema
            if not netloc: 
                netloc = path
                path = ''
    
            q = parse_qsl(query, keep_blank_values=True)
            q.append(('blogId', blogSeo.Blog))
            q.append(('blogTitle', blog.Title))
            q.append(('theme', theme.Name))
            q.append(('htmlFile', self.host_URL + self.htmlCDM.getURI(path)))
                
            url = urlunparse((scheme, netloc, path, params, urlencode(q), fragment))
            req = Request(url, headers={'Accept' : self.acceptType, 'Accept-Charset' : self.encodingType,
                                        'User-Agent' : 'Magic Browser'})
            
            try: resp = urlopen(req)
            except Exception as e:
                log.error('Read error on %s: %s' % (blogSeo.CallbackURL, e))
                blogSeo.CallbackStatus = 'Error opening URL:' + url  
            else: 
                if str(resp.status) != '200':
                    log.error('Read problem on %s, status: %s' % (blogSeo.CallbackURL, resp.status))
                    blogSeo.CallbackStatus = resp.status
                else: blogSeo.CallbackStatus = 'OK'    
        
        blogSeo.LastSync = datetime.datetime.now().replace(microsecond=0) 
        blogSeo.LastBlocked = None 
        self.blogSeoService.update(blogSeo)
