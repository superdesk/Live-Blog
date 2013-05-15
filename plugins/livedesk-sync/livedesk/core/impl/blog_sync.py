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
from sched import scheduler
from threading import Thread
from datetime import time, datetime
from urllib.request import urlopen, Request
from urllib.parse import urlparse, ParseResult, parse_qsl, urlencode, urlunparse
from http.client import HTTPResponse

from livedesk.api.blog_sync import IBlogSyncService, QBlogSync, BlogSync
from superdesk.source.api.source import ISourceService, Source
from livedesk.api.blog_post import BlogPost, IBlogPostService
from sqlalchemy.sql.functions import current_timestamp
from superdesk.collaborator.api.collaborator import ICollaboratorService, Collaborator
from livedesk.core.spec import IBlogSync
from ally.container import wire

# --------------------------------------------------------------------

class BlogSync(IBlogSync):
    '''
    Blog sync implementation.
    '''

    blogSyncService = IBlogSyncService; wire.entity('blogSyncService')
    # blog sync service used to retrieve blogs set on auto publishing

    sourceService = ISourceService; wire.entity('sourceService')
    # source service used to retrieve source data

    blogPostService = IBlogPostService; wire.entity('blogPostService')
    # blog post service used to insert blog posts

    collaboratorService = ICollaboratorService; wire.entity('collaboratorService')
    # blog post service used to retrive collaborator

    syncInterval = 1; wire.config('syncInterval', doc='''The number of seconds to perform sync for blogs.''')

    def startSyncThread(self, name):
        '''
        Starts the sync thread.

        @param name: string
            The name for the thread.
        '''
        schedule = scheduler(time.time, time.sleep)
        def syncBlogs():
            self.syncBlogs()
            schedule.enter(self.syncInterval, 1, syncBlogs, ())
        schedule.enter(self.syncInterval, 1, syncBlogs, ())
        scheduleRunner = Thread(name=name, target=schedule.run)
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
        uri = urlparse(source.URI)
        assert isinstance(uri, ParseResult)

        q = parse_qsl(uri.query)
        q.append(('cId', blogSync.CId))
        q.append(('updatedOn.since', datetime.strptime(blogSync.SyncStart, '%Y-%m-%d %H:%M:%S')))
        uri.query = urlencode(q)
        req = Request(urlunparse(uri), headers={'Accept' : 'JSON'})
        try: resp = urlopen(req)
        except socket.error as e:
            print(e.errno)
            if e.errno == 111: print('Connection refused')
            return

        collab = self.collaboratorService.getAll(blogSync.Admin, source.Id, limit=1)
        if collab: collabId = collab[0].Id
        else:
            collab = Collaborator()
            collab.User = blogSync.Creator
            collab.Source = source.Id
            collab.Name = source.Name
            collabId = self.collaboratorService.insert(collab)

        assert isinstance(resp, HTTPResponse)
        msg = json.load(resp)
        blogSync.CId = msg['lastCId']
        for post in msg['PostList']:
            dbPost = BlogPost()
            dbPost.Type = post['Type']['Key']
            dbPost.Creator = blogSync.Creator
            dbPost.Author = collabId
            dbPost.Meta = post['Meta'] if 'Meta' in post else None
            dbPost.ContentPlain = post['ContentPlain'] if 'ContentPlain' in post else None
            dbPost.Content = post['Content'] if 'Content' in post else None
            dbPost.CreatedOn = dbPost.PublishedOn = current_timestamp()
            self.blogPostService.insert(blogSync.Blog, dbPost)

        self.blogSyncService.update(blogSync)
