'''
Created on April 26, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API implementation of liveblog sync.
'''

import socket
import json
import logging
import time
import codecs
from sched import scheduler
from threading import Thread
from urllib.request import urlopen, Request
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from http.client import HTTPResponse
from livedesk.api.blog_sync import IBlogSyncService, QBlogSync, BlogSync
from superdesk.source.api.source import ISourceService, Source
from livedesk.api.blog_post import BlogPost, IBlogPostService
from sqlalchemy.sql.functions import current_timestamp
from superdesk.collaborator.api.collaborator import ICollaboratorService, Collaborator
from ally.container import wire, app
from ally.container.ioc import injected
from ally.container.support import setup
from io import BytesIO

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(name='blogSynchronizer')
class BlogSyncProcess:
    '''
    Blog sync process.
    '''

    blogSyncService = IBlogSyncService; wire.entity('blogSyncService')
    # blog sync service used to retrieve blogs set on auto publishing

    sourceService = ISourceService; wire.entity('sourceService')
    # source service used to retrieve source data

    blogPostService = IBlogPostService; wire.entity('blogPostService')
    # blog post service used to insert blog posts

    collaboratorService = ICollaboratorService; wire.entity('collaboratorService')
    # blog post service used to retrive collaborator

    sync_interval = 10; wire.config('sync_interval', doc='''
    The number of seconds to perform sync for blogs.''')
    date_time_format = '%Y-%m-%d %H:%M:%S'; wire.config('date_time_format', doc='''
    The date time format used in REST requests.''')
    accept_header = 'Accept'; wire.config('accept_header', doc='''
    The header used to specify accepted data format.''')

    nameAcceptCharset = 'Accept-Charset'
    # The name for the accept character sets header

    @app.deploy
    def startSyncThread(self):
        '''
        Starts the sync thread.
        '''
        log.info('Starting the blog automatic sync thread.')
        schedule = scheduler(time.time, time.sleep)
        def syncBlogs():
            self.syncBlogs()
#            schedule.enter(self.sync_interval, 1, syncBlogs, ())
        schedule.enter(self.sync_interval, 1, syncBlogs, ())
        scheduleRunner = Thread(name='blog sync', target=schedule.run)
        scheduleRunner.daemon = True
        scheduleRunner.start()

    def syncBlogs(self):
        '''
        '''
        q = QBlogSync()
        q.auto = True
        syncBlogs = self.blogSyncService.getAll(q=q)
        for blog in syncBlogs:
            self._syncBlog(blog)

    def _syncBlog(self, blogSync):
        assert isinstance(blogSync, BlogSync), 'Invalid blog sync %s' % blogSync
        source = self.sourceService.getById(blogSync.Source)
        assert isinstance(source, Source)
        (scheme, netloc, path, params, query, fragment) = urlparse(source.URI)

        q = parse_qsl(query, keep_blank_values=True)
        q.append(('X-Filter', '*'))
        q.append(('asc', 'cId'))
        q.append(('cId.since', blogSync.CId if blogSync.CId is not None else 0))
        if blogSync.SyncStart is not None:
            q.append(('updatedOn.since', blogSync.SyncStart.strftime(self.date_time_format)))
        url = urlunparse((scheme, netloc, path + '/Post/Published', params, urlencode(q), fragment))
        # TODO: remove
        print(url)
        req = Request(url, headers={self.accept_header : 'JSON', self.nameAcceptCharset : 'UTF-8'})
        try:
            resp = urlopen(req)
            assert isinstance(resp, HTTPResponse)
        except socket.error as e:
            if e.errno == 111: log.error('Connection refused by %s' % source.URI)
            else: log.error('Error connecting to %s: %s' % (source.URI, e.strerror))
            return

        collab = self.collaboratorService.getAll(None, source.Id, limit=1)
        if collab: collabId = collab[0].Id
        else:
            collab = Collaborator()
#            collab.User = blogSync.Creator
            collab.Source = source.Id
            collabId = self.collaboratorService.insert(collab)

        msg = json.load(codecs.getreader('UTF-8')(resp))
        try: blogSync.CId = msg['lastCId']
        except KeyError as e:
            log.error('Missing change identifier from source %s' % source.URI)
            return
        for post in msg['PostList']:
            try:
                dbPost = BlogPost()
                dbPost.Type = post['Type']['Key']
                dbPost.Creator = blogSync.Creator
                dbPost.Author = collabId
                dbPost.Meta = post['Meta'] if 'Meta' in post else None
                dbPost.ContentPlain = post['ContentPlain'] if 'ContentPlain' in post else None
                dbPost.Content = post['Content'] if 'Content' in post else None
                dbPost.CreatedOn = dbPost.PublishedOn = current_timestamp()
                self.blogPostService.insert(blogSync.Blog, dbPost)
            except KeyError as e:
                log.error('Source %s post error: %s' % (source.URI, e))

        self.blogSyncService.update(blogSync)
