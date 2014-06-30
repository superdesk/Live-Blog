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
from superdesk.language.api.language import ILanguageService


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
    
    languageService = ILanguageService; wire.entity('languageService')
    # blog language service used to get the language code
    
    htmlCDM = ICDM; wire.entity('htmlCDM')
    # cdm service used to store the generated HTML files
    
    syncThreads = {}
    # dictionary of threads that perform synchronization

    sync_interval = 59; wire.config('sync_interval', doc='''
    The number of seconds to perform sync for seo blogs.''')
    
    timeout_inteval = 4#; wire.config('timeout_interval', doc='''
    #The number of seconds after the sync ownership can be taken.''')
    
    html_generation_server = 'http://nodejs-dev.sourcefabric.org/'; wire.config('html_generation_server', doc='''
    The partial path used to construct the URL for blog html generation''')
    
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
            schedule.enter(self.sync_interval, 1, syncSeoBlogs, ())
        schedule.enter(self.sync_interval, 1, syncSeoBlogs, ())
        scheduleRunner = Thread(name='blog html for seo', target=schedule.run)
        scheduleRunner.daemon = True
        scheduleRunner.start()
        log.info('Started the seo html synchronization.')

    def syncSeoBlogs(self):
        '''
        Read all chained blog sync entries and sync with the corresponding blogs.
        '''
        log.info('Start seo blog synchronization')
        
        crtTime = datetime.datetime.now().replace(microsecond=0) 
        
        q = QBlogSeo(refreshActive=True)
        q.nextSync.until = crtTime
        
        for blogSeo in self.blogSeoService.getAll(q=q): 
            assert isinstance(blogSeo, BlogSeo)
            
            nextSync = crtTime + datetime.timedelta(seconds=blogSeo.RefreshInterval)
            self.blogSeoService.updateNextSync(blogSeo.Id, nextSync) 
            
            existsChanges = self.blogSeoService.existsChanges(blogSeo.Blog, blogSeo.LastCId)
            
            if blogSeo.LastSync is not None and not existsChanges: 
                log.info('Skip blog seo %d for blog %d', blogSeo.Id, blogSeo.Blog)
                continue
            
            key = (blogSeo.Blog, blogSeo.BlogTheme)
            thread = self.syncThreads.get(key)
            if thread:
                assert isinstance(thread, Thread), 'Invalid thread %s' % thread
                if thread.is_alive(): continue

                if not self.blogSeoService.checkTimeout(blogSeo.Id, self.timeout_inteval * self.sync_interval): continue

            self.syncThreads[key] = Thread(name='blog %d seo' % blogSeo.Blog,
                                           target=self._syncSeoBlog, args=(blogSeo,))
            self.syncThreads[key].daemon = True
            self.syncThreads[key].start()
            log.info('Seo thread started for blog id %d and theme id %d', blogSeo.Blog, blogSeo.BlogTheme)   
        log.info('End seo blog synchronization')

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
        language = self.languageService.getById(blog.Language, ())
                   
        (scheme, netloc, path, params, query, fragment) = urlparse(self.html_generation_server)

        q = parse_qsl(query, keep_blank_values=True)
        q.append(('liveblog[id]', blogSeo.Blog))
        q.append(('liveblog[theme]', theme.Name))
        q.append(('liveblog[servers][rest]', self.host_url))
        q.append(('liveblog[fallback][language]', language.Code))
        if blogSeo.MaxPosts is not None:
            q.append(('liveblog[limit]', blogSeo.MaxPosts))

        url = urlunparse((scheme, netloc, path, params, urlencode(q), fragment))
        req = Request(url, headers={'Accept' : self.acceptType, 'Accept-Charset' : self.encodingType,
                                    'User-Agent' : 'LiveBlog REST'})
        
        try: resp = urlopen(req)
        except HTTPError as e:
            blogSeo.CallbackStatus = e.read().decode(encoding='UTF-8')
            blogSeo.LastBlocked = None 
            self.blogSeoService.update(blogSeo)
            log.error('Read problem on %s, error code with message: %s ' % (str(url), blogSeo.CallbackStatus))
            return
        except Exception as e:  
            blogSeo.CallbackStatus = 'Can\'t access the HTML generation server: ' + self.html_generation_server
            blogSeo.LastBlocked = None 
            self.blogSeoService.update(blogSeo)
            log.error('Read problem on accessing %s' % (self.html_generation_server, ))
            return
 
        try: 
            baseContent = self.htmlCDM.getURI('')
            path = blogSeo.HtmlURL[len(baseContent):]
            self.htmlCDM.publishContent(path, resp)
        except ValueError as e:
            log.error('Fail to publish the HTML file on CDM %s' % e)
            blogSeo.CallbackStatus = 'Fail to publish the HTML file on CDM'
            blogSeo.LastBlocked = None 
            self.blogSeoService.update(blogSeo)
            return
        
        blogSeo.CallbackStatus = None  

        if blogSeo.CallbackActive:
            (scheme, netloc, path, params, query, fragment) = urlparse(blogSeo.CallbackURL)
            
            if not scheme: scheme = 'http'
            if not netloc: 
                netloc = path
                path = ''
    
            q = parse_qsl(query, keep_blank_values=True)
            q.append(('blogId', blogSeo.Blog))
            q.append(('blogTitle', blog.Title))
            q.append(('theme', theme.Name))
            q.append(('htmlFile', self.host_url + self.htmlCDM.getURI(path)))
                
            url = urlunparse((scheme, netloc, path, params, urlencode(q), fragment))
            req = Request(url, headers={'Accept' : self.acceptType, 'Accept-Charset' : self.encodingType,
                                        'User-Agent' : 'Magic Browser'})
            
            try: resp = urlopen(req)
            except HTTPError as e:
                log.error('Error opening URL %s; error status: %s' % (blogSeo.CallbackURL, resp.status))
                blogSeo.CallbackStatus = 'Error opening callback URL: ' + blogSeo.CallbackURL + '; error status: ' + resp.status
            except Exception as e:
                log.error('Error opening URL %s: %s' % (blogSeo.CallbackURL, e))
                blogSeo.CallbackStatus = 'Error opening callback URL:' + blogSeo.CallbackURL 
            else: 
                blogSeo.CallbackStatus = None    
        
        blogSeo.LastSync = datetime.datetime.now().replace(microsecond=0) 
        blogSeo.LastBlocked = None 
        self.blogSeoService.update(blogSeo)
