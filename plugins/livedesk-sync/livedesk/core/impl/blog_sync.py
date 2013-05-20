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
from hashlib import sha1
from sched import scheduler
from threading import Thread
from urllib.request import urlopen, Request
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from datetime import datetime
from livedesk.api.blog_sync import IBlogSyncService, QBlogSync, BlogSync
from superdesk.source.api.source import ISourceService, Source, QSource
from livedesk.api.blog_post import BlogPost, IBlogPostService
from sqlalchemy.sql.functions import current_timestamp
from superdesk.collaborator.api.collaborator import ICollaboratorService, Collaborator
from ally.container import wire, app
from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.user.api.user import IUserService, QUser, User
from ally.exception import InputError
from urllib.error import HTTPError

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

    userService = IUserService; wire.entity('userService')

    sync_interval = 10; wire.config('sync_interval', doc='''
    The number of seconds to perform sync for blogs.''')
    date_time_format = '%Y-%m-%d %H:%M:%S'; wire.config('date_time_format', doc='''
    The date time format used in REST requests.''')
    published_posts_path = 'Post/Published'; wire.config('published_posts_path', doc='''
    The partial path used to construct the URL for published posts retrieval''')

    acceptType = 'text/json'
    # mime type accepted for response from remote blog
    encodingType = 'UTF-8'
    # character encoding type accepted for response from remove blog

    @app.deploy
    def startSyncThread(self):
        '''
        Starts the sync thread.
        '''
        log.info('Starting the blog automatic sync thread.')
        schedule = scheduler(time.time, time.sleep)
        def syncBlogs():
            self.syncBlogs()
            schedule.enter(self.sync_interval, 1, syncBlogs, ())
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
        '''
        Synchronize the blog for the given sync entry.

        @param blogSync: BlogSync
            The blog sync entry declaring the blog and source from which the blog
            has to be updated.
        '''
        assert isinstance(blogSync, BlogSync), 'Invalid blog sync %s' % blogSync
        source = self.sourceService.getById(blogSync.Source)
        assert isinstance(source, Source)
        (scheme, netloc, path, params, query, fragment) = urlparse(source.URI)

        q = parse_qsl(query, keep_blank_values=True)
        q.append(('X-Filter', '*,Author.Source.*,Author.User.*'))
        q.append(('asc', 'cId'))
        q.append(('cId.since', blogSync.CId if blogSync.CId is not None else 0))
        if blogSync.SyncStart is not None:
            q.append(('updatedOn.since', blogSync.SyncStart.strftime(self.date_time_format)))
        url = urlunparse((scheme, netloc, path + '/' + self.published_posts_path, params, urlencode(q), fragment))
        req = Request(url, headers={'Accept' : self.acceptType, 'Accept-Charset' : self.encodingType})
        try: resp = urlopen(req)
        except HTTPError as e:
            log.error('Error connecting to %s: %s' % (source.URI, e))
            return
        except socket.error as e:
            if e.errno == 111: log.error('Connection refused by %s' % source.URI)
            else: log.error('Error connecting to %s: %s' % (source.URI, e.strerror))
            return

        msg = json.load(codecs.getreader(self.encodingType)(resp))
        try: blogSync.CId = msg['lastCId']
        except KeyError as e:
            log.error('Missing change identifier from source %s' % source.URI)
            return
        for post in msg['PostList']:
            try:
                if post['IsPublished'] != 'True': continue
                publishedOn = datetime.strptime(post['PublishedOn'], '%m/%d/%y %I:%M %p')
                if blogSync.SyncStart is None or blogSync.SyncStart < publishedOn:
                    blogSync.SyncStart = publishedOn
                dbPost = BlogPost()
                dbPost.Type = post['Type']['Key']
                dbPost.Creator = blogSync.Creator
                dbPost.Author = self._getCollaboratorForAuthor(post['Author'], source)
                dbPost.Meta = post['Meta'] if 'Meta' in post else None
                dbPost.ContentPlain = post['ContentPlain'] if 'ContentPlain' in post else None
                dbPost.Content = post['Content'] if 'Content' in post else None
                dbPost.CreatedOn = dbPost.PublishedOn = current_timestamp()
                self.blogPostService.insert(blogSync.Blog, dbPost)
            except KeyError as e:
                log.error('Post from source %s is missing attribute %s' % (source.URI, e))
            except Exception as e:
                log.error('Error in source %s post: %s' % (source.URI, e))

        self.blogSyncService.update(blogSync)

    def _getCollaboratorForAuthor(self, author, source):
        '''
        Returns a collaborator identifier for the user/source defined in the post.
        If the post was not created by a user it returns a collaborator for the
        source identified in the post and the default user. The default user should
        be the sync entry creator. If the source from the post does not exist
        locally raises Exception.

        @param author: dict
            The author data in JSON decoded format
        @param source: Source
            The source from which the blog synchronization is done
        @return: integer
            The collaborator identifier.
        '''
        assert isinstance(source, Source)
        try:
            uJSON = author['User']
            u = User()
            u.Name = sha1((uJSON.get('Name', '') + source.URI).encode(self.encodingType)).hexdigest()
            u.FirstName, u.LastName = uJSON.get('FirstName', ''), uJSON.get('LastName', '')
            u.EMail, u.Password = uJSON.get('EMail', ''), '*'
            try: userId = self.userService.insert(u)
            except InputError:
                q = QUser(name=u.Name)
                localUser = self.userService.getAll(q=q)
                userId = localUser[0].Id
            c = Collaborator()
            c.User, c.Source = userId, source.Id
            try: return self.collaboratorService.insert(c)
            except InputError:
                collabs = self.collaboratorService.getAll(userId, source.Id)
                return collabs[0].Id
        except KeyError:
            q = QSource(name=author['Source']['Name'], isModifiable=False)
            sources = self.sourceService.getAll(q=q)
            if not sources: raise Exception('Invalid source %s' % q.name)
            collabs = self.collaboratorService.getAll(userId=None, sourceId=sources[0].Id)
            if collabs: return collabs[0].Id
            else:
                c = Collaborator()
                c.Source = sources[0].Id
                return self.collaboratorService.insert(c)
