'''
Created on Oct 22, 2013

@package: frontline-inlet
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API implementation of sms sync.
'''


import logging
import time
import datetime
from sched import scheduler
from threading import Thread
from superdesk.source.api.source import ISourceService, Source
from livedesk.api.blog_post import IBlogPostService
from sqlalchemy.sql.functions import current_timestamp
from superdesk.collaborator.api.collaborator import ICollaboratorService,\
    Collaborator
from ally.container import wire, app
from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.user.api.user import IUserService
from superdesk.post.api.post import Post, IPostService, QPost
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from sqlalchemy.orm.exc import NoResultFound
from livedesk.api.blog_sync import IBlogSyncService, BlogSync


# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(name='smsSynchronizer')
class SmsSyncProcess:
    '''
    Sms sync process.
    '''

    blogSyncService = IBlogSyncService; wire.entity('blogSyncService')
    # blog sync service used to retrieve blogs set on auto publishing

    sourceService = ISourceService; wire.entity('sourceService')
    # source service used to retrieve source data
    
    postService = IPostService; wire.entity('postService')
    # post service used to insert posts

    blogPostService = IBlogPostService; wire.entity('blogPostService') 
    # blog post service used to insert blog posts

    collaboratorService = ICollaboratorService; wire.entity('collaboratorService')
    # blog post service used to retrieve collaborator

    userService = IUserService; wire.entity('userService')

    syncThreads = {}
    # dictionary of threads that perform synchronization

    sync_interval = 60; wire.config('sync_interval', doc='''
    The number of seconds to perform sync for sms.''')
    
    timeout_inteval = 180#; wire.config('timeout_interval', doc='''
    #The number of seconds after the sync ownership can be taken.''')
    
    user_type_key = 'sms'; wire.config('user_type_key', doc='''
    The user type that is used for the anonymous users of sms posts''')
    
    sms_provider_type = 'smsfeed'; wire.config('sms_provider_type', doc='''
    Key of the source type for SMS providers''') 

    @app.deploy
    def startSmsSyncThread(self):
        '''
        Starts the SMS sync thread.
        '''
        schedule = scheduler(time.time, time.sleep)
        def syncSmss():
            self.syncSmss()
            schedule.enter(self.sync_interval, 1, syncSmss, ())
        schedule.enter(self.sync_interval, 1, syncSmss, ())
        scheduleRunner = Thread(name='sms sync', target=schedule.run)
        scheduleRunner.daemon = True
        scheduleRunner.start()
        log.info('Started the sms automatic synchronization.')

    def syncSmss(self):
        '''
        Read all sms blog sync entries.
        '''
        log.info('Start sms blog synchronization')
        
        for blogSync in self.blogSyncService.getBySourceType(self.sms_provider_type):
            assert isinstance(blogSync, BlogSync)
            key = (blogSync.Blog, blogSync.Source)
            thread = self.syncThreads.get(key)
            if thread:
                assert isinstance(thread, Thread), 'Invalid thread %s' % thread
                if thread.is_alive(): continue

            if not self.blogSyncService.checkTimeout(blogSync.Id, self.timeout_inteval): continue         

            self.syncThreads[key] = Thread(name='sms %d sync' % blogSync.Blog,
                                           target=self._syncSms, args=(blogSync,))
            self.syncThreads[key].daemon = True
            self.syncThreads[key].start()
            log.info('Sms thread started for blog id %d and source id %d', blogSync.Blog, blogSync.Source)
        log.info('End sms blog synchronization')    

    def _syncSms(self, blogSync):
        '''
        Synchronize the sms for the given sync entry.

        @param smsSync: SmsSync
            The sms sync entry declaring the blog and source from which the blog
            has to be updated.
        '''
        assert isinstance(blogSync, BlogSync), 'Invalid blog sync %s' % blogSync
        source = self.sourceService.getById(blogSync.Source)
        assert isinstance(source, Source)

        providerId = self.sourceService.getOriginalSource(source.Id)
        
        log.info("sync sms for sourceId=%i, providerId=%i, blogId=%i, lastId=%i" %(blogSync.Source, providerId, blogSync.Blog, blogSync.CId))

        q=QPost()
        q.cId.since = str(blogSync.CId) 
        
        posts = self.postService.getAllBySource(providerId, q=q)

        for post in posts:
            try:
                
                log.info("post: Id=%i, content=%s, sourceId=%i" %(post.Id, post.Content, blogSync.Source))
                
                smsPost = Post()
                smsPost.Type = post.Type
                smsPost.Uuid = post.Uuid
                smsPost.Creator = post.Creator
                smsPost.Feed = source.Id
                smsPost.Meta = post.Meta
                smsPost.ContentPlain = post.ContentPlain
                smsPost.Content = post.Content
                smsPost.CreatedOn = current_timestamp()   
                
                # make the collaborator
                sql = self.collaboratorService.session().query(CollaboratorMapped.Id)
                sql = sql.filter(CollaboratorMapped.Source == blogSync.Source)
                sql = sql.filter(CollaboratorMapped.User == post.Creator)
                try:
                    collaboratorId, = sql.one()
                except NoResultFound:
                    collaborator = Collaborator()
                    collaborator.Source = blogSync.Source
                    collaborator.User = post.Creator
                    collaboratorId = self.collaboratorService.insert(collaborator)   
                    
                smsPost.Author = collaboratorId            
                
                # prepare the sms sync model to update the change identifier
                blogSync.CId = post.Id if post.Id > blogSync.CId else blogSync.CId

                # insert post from remote source
                self.blogPostService.insert(blogSync.Blog, smsPost)
                
                # update blog sync entry
                blogSync.LastActivity = datetime.datetime.now().replace(microsecond=0) 
                self.blogSyncService.update(blogSync)
                                
            except Exception as e:
                log.error('Error in source %s post: %s' % (source.URI, e))

        blogSync.LastActivity = None 
        self.blogSyncService.update(blogSync)       