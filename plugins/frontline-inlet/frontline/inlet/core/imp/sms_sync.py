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
from sched import scheduler
from threading import Thread
from superdesk.source.api.source import ISourceService, Source
from livedesk.api.blog_post import IBlogPostService
from sqlalchemy.sql.functions import current_timestamp
from superdesk.collaborator.api.collaborator import ICollaboratorService
from ally.container import wire, app
from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.user.api.user import IUserService
from superdesk.post.api.post import Post, QWithCId, IPostService, QPost
from frontline.inlet.api.sms_sync import ISmsSyncService, SmsSync
from ally.api.criteria import AsRangeOrdered, AsRange

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(name='smsSynchronizer')
class SmsSyncProcess:
    '''
    Sms sync process.
    '''

    smsSyncService = ISmsSyncService; wire.entity('smsSyncService')
    # sms sync service used to retrieve sms sync data

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

    sync_interval = 10; wire.config('sync_interval', doc='''
    The number of seconds to perform sync for sms.''')
    
    user_type_key = 'sms'; wire.config('user_type_key', doc='''
    The user type that is used for the anonymous users of sms posts''')

    @app.deploy
    def startSyncThread(self):
        '''
        Starts the sync thread.
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
        Read all sms sync entries.
        '''
        
        for smsSync in self.smsSyncService.getAll(): 
            assert isinstance(smsSync, SmsSync)
            key = (smsSync.Blog, smsSync.Source)
            thread = self.syncThreads.get(key)
            if thread:
                assert isinstance(thread, Thread), 'Invalid thread %s' % thread
                if thread.is_alive(): continue

            self.syncThreads[key] = Thread(name='sms %d sync' % smsSync.Blog,
                                           target=self._syncSms, args=(smsSync,))
            self.syncThreads[key].daemon = True
            self.syncThreads[key].start()
            log.info('Thread started for blog id %d and source id %d', smsSync.Blog, smsSync.Source)


    def _syncSms(self, smsSync):
        '''
        Synchronize the sms for the given sync entry.

        @param smsSync: SmsSync
            The sms sync entry declaring the blog and source from which the blog
            has to be updated.
        '''
        assert isinstance(smsSync, SmsSync), 'Invalid sms sync %s' % smsSync
        source = self.sourceService.getById(smsSync.Source)
        assert isinstance(source, Source)

        feedId = self.sourceService.getOriginalSource(source.Id)

        q=QPost()
        q.cId.since = str(smsSync.LastId) 
        
        posts = self.postService.getAllBySource(feedId, q=q)

        for post in posts:
            try:
                smsPost = Post()
                smsPost.Type = post.Type
                smsPost.Creator = post.Creator
                smsPost.Author = post.Author
                smsPost.Meta = post.Meta
                smsPost.ContentPlain = post.ContentPlain
                smsPost.Content = post.Content
                smsPost.CreatedOn = current_timestamp()              
                
                # prepare the sms sync model to update the change identifier
                smsSync.LastId = post.Id if post.Id > smsSync.LastId else smsSync.LastId

                # insert post from remote source
                self.blogPostService.insert(smsSync.Blog, smsPost)
                
                # update blog sync entry
                self.smsSyncService.update(smsSync)

            except Exception as e:
                log.error('Error in source %s post: %s' % (source.URI, e))

