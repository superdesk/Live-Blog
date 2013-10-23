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
from livedesk.api.blog_sync import IBlogSyncService, BlogSync
from superdesk.source.api.source import ISourceService, Source, QSource
from livedesk.api.blog_post import IBlogPostService
from sqlalchemy.sql.functions import current_timestamp
from superdesk.collaborator.api.collaborator import ICollaboratorService, Collaborator
from ally.container import wire, app
from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.user.api.user import IUserService, User
from ally.exception import InputError
from urllib.error import HTTPError
from superdesk.media_archive.api.meta_data import IMetaDataUploadService
from superdesk.media_archive.api.meta_info import IMetaInfoService
from superdesk.person_icon.api.person_icon import IPersonIconService
from .icon_content import ChainedIconContent
from superdesk.post.api.post import Post
from superdesk.verification.api.verification import PostVerification,\
    IPostVerificationService

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
    
    postVerificationService = IPostVerificationService; wire.entity('postVerificationService')
    # post verification service used to insert post verification

    collaboratorService = ICollaboratorService; wire.entity('collaboratorService')
    # blog post service used to retrive collaborator

    userService = IUserService; wire.entity('userService')

    metaDataService = IMetaDataUploadService; wire.entity('metaDataService')

    metaInfoService = IMetaInfoService; wire.entity('metaInfoService')

    personIconService = IPersonIconService; wire.entity('personIconService')

    syncThreads = {}
    # dictionary of threads that perform synchronization

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
    
    user_type_key = 'chained blog'; wire.config('user_type_key', doc='''
    The user type that is used for the anonymous users of chained blog posts''')

    @app.deploy
    def startSyncThread(self):
        '''
        Starts the sync thread.
        '''
        schedule = scheduler(time.time, time.sleep)
        def syncBlogs():
            self.syncBlogs()
            schedule.enter(self.sync_interval, 1, syncBlogs, ())
        schedule.enter(self.sync_interval, 1, syncBlogs, ())
        scheduleRunner = Thread(name='blogs sync', target=schedule.run)
        scheduleRunner.daemon = True
        scheduleRunner.start()
        log.info('Started the blogs automatic synchronization.')

    def syncBlogs(self):
        '''CollaboratorMapped.Id
        Read all blog sync entries and sync with the corresponding blogs.
        '''
        for blogSync in self.blogSyncService.getAll(): 
            assert isinstance(blogSync, BlogSync)
            key = (blogSync.Blog, blogSync.Source)
            thread = self.syncThreads.get(key)
            if thread:
                assert isinstance(thread, Thread), 'Invalid thread %s' % thread
                if thread.is_alive(): continue

            self.syncThreads[key] = Thread(name='blog %d sync' % blogSync.Blog,
                                           target=self._syncBlog, args=(blogSync,))
            self.syncThreads[key].daemon = True
            self.syncThreads[key].start()
            log.info('Thread started for blog id %d and source id %d', blogSync.Blog, blogSync.Source)


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
        q.append(('asc', 'cId'))
        q.append(('cId.since', blogSync.CId if blogSync.CId is not None else 0))
        if blogSync.SyncStart is not None:
            q.append(('publishedOn.since', blogSync.SyncStart.strftime(self.date_time_format)))
        url = urlunparse((scheme, netloc, path + '/' + self.published_posts_path, params, urlencode(q), fragment))
        req = Request(url, headers={'Accept' : self.acceptType, 'Accept-Charset' : self.encodingType,
                                    'X-Filter' : '*,Creator.*,Author.Source.*,Author.User.*', 'User-Agent' : 'Magic Browser'})
        try: resp = urlopen(req)
        except (HTTPError, socket.error) as e:
            log.error('Read error on %s: %s' % (source.URI, e))
            return
        if str(resp.status) != '200':
            log.error('Read problem on %s, status: %s' % (source.URI, resp.status))
            return

        try: msg = json.load(codecs.getreader(self.encodingType)(resp))
        except ValueError as e:
            log.error('Invalid JSON data %s' % e)
            return

        usersForIcons = {}
        for post in msg['PostList']:
            try:
                if post['IsPublished'] != 'True' or 'DeletedOn' in post: continue

                localPost = Post()
                localPost.Type = post['Type']['Key']
                localPost.Author, localPost.Creator = self._getCollaboratorForAuthor(post['Author'], post['Creator'], source)
                localPost.Meta = post['Meta'] if 'Meta' in post else None
                localPost.ContentPlain = post['ContentPlain'] if 'ContentPlain' in post else None
                localPost.Content = post['Content'] if 'Content' in post else None
                localPost.Order = post['Order'] if 'Order' in post else None
                localPost.CreatedOn = current_timestamp()              
                if blogSync.Auto: localPost.PublishedOn = current_timestamp()
  
                if localPost.Creator and (localPost.Creator not in usersForIcons):
                    try:
                        usersForIcons[localPost.Creator] = post['Author']['User']
                    except KeyError:
                        pass

                # prepare the blog sync model to update the change identifier
                blogSync.CId = int(post['CId']) if blogSync.CId is None or int(post['CId']) > blogSync.CId else blogSync.CId
                blogSync.SyncStart = datetime.strptime(post['PublishedOn'], '%m/%d/%y %I:%M %p')

                # insert post from remote source
                self.blogPostService.insert(blogSync.Blog, localPost)
                
                # update blog sync entry
                self.blogSyncService.update(blogSync)
                
                #create PostVerification
                postVerification = PostVerification()
                postVerification.Id = localPost.Id
                self.postVerificationService.insert(postVerification)
                
            except KeyError as e:
                log.error('Post from source %s is missing attribute %s' % (source.URI, e))
            except Exception as e:
                log.error('Error in source %s post: %s' % (source.URI, e))

        self._updateIcons(usersForIcons)

    def _getCollaboratorForAuthor(self, author, creator, source):
        '''
        Returns a collaborator identifier for the user/source defined in the post.
        If the post was not created by a user (it is twitter, facebook, etc. post) 
        it returns a collaborator for the user that has added the post.

        @param author: dict
            The author data in JSON decoded format
        @param creator: dict
            The creator data in JSON decoded format
        @param source: Source
            The source from which the blog synchronization is done
        @return: integer
            The collaborator identifier.
        '''
        assert isinstance(source, Source)
        
        
        if 'User' in author.keys():
            userJSON = author['User']  
        else:
            userJSON = creator
                                        
        user = User()
        user.Name = sha1((userJSON.get('Name', '') + source.URI).encode(self.encodingType)).hexdigest()
        user.FirstName, user.LastName = userJSON.get('FirstName', ''), userJSON.get('LastName', '')
        user.EMail, user.Password = userJSON.get('EMail', ''), '*'
        user.Type = self.user_type_key
        
        try: userId = self.userService.insert(user)
        except InputError:
            userId = self.userService.getByName(user.Name).Id
            
        collaborator = Collaborator()
        collaborator.User, collaborator.Source = userId, source.Id
        try: collaboratorId = self.collaboratorService.insert(collaborator)
        except InputError:
            collaborators = self.collaboratorService.getAll(userId, source.Id)
            collaboratorId = collaborators[0].Id
        
        if 'User' in author.keys():
            return [collaboratorId, userId]
        else:    
            q = QSource(name=author['Source']['Name'], isModifiable=False)
            sources = self.sourceService.getAll(q=q)
            if not sources: raise Exception('Invalid source %s' % q.name)
            collaborators = self.collaboratorService.getAll(userId=None, sourceId=sources[0].Id)
            if collaborators: return [collaborators[0].Id, userId]
            else:
                collaborator = Collaborator()
                collaborator.Source = sources[0].Id
                return [self.collaboratorService.insert(collaborator), userId]

    def _updateIcons(self, usersData):
        '''
        Setting the icon of the user
        '''
        userIcons = {}
        for userId in usersData:
            userJSON = usersData[userId]
            userIcons[userId] = {'created': None, 'url': None, 'name': None}

            try:
                metaDataIconJSON = userJSON['MetaDataIcon']
                metaDataIconURL = metaDataIconJSON.get('href', '')
                if not metaDataIconURL:
                    continue

                req = Request(metaDataIconURL, headers={'Accept' : self.acceptType, 'Accept-Charset' : self.encodingType, 'User-Agent' : 'Magic Browser'})
                try:
                    resp = urlopen(req)
                except (HTTPError, socket.error) as e:
                    continue
                if str(resp.status) != '200':
                    continue

                try:
                    msg = json.load(codecs.getreader(self.encodingType)(resp))
                except ValueError as e:
                    log.error('Invalid JSON data %s' % e)
                    continue

                try:
                    userIcons[userId]['created'] = datetime.strptime(msg.get('CreatedOn', None), '%m/%d/%y %I:%M %p')
                except:
                    userIcons[userId]['created'] = None
                userIcons[userId]['url'] = msg['Content'].get('href', None)

                if userIcons[userId]['url']:
                    iconFileName = userIcons[userId]['url'].split('/')[-1]
                    if iconFileName:
                        iconFileName = '_' + iconFileName
                    userIcons[userId]['name'] = 'icon_' + str(userId) + iconFileName

            except KeyError:
                continue

        for userId in userIcons:
            iconInfo = userIcons[userId]
            self._synchronizeIcon(userId, iconInfo)

    def _synchronizeIcon(self, userId, iconInfo):
        '''
        Synchronizing local icon according to the remote one
        '''
        if not userId:
            return

        shouldRemoveOld = False
        needToUploadNew = False

        try:
            metaDataLocal = self.personIconService.getByPersonId(userId, 'http')
        except InputError:
            metaDataLocal = None

        if metaDataLocal:
            localId = metaDataLocal.Id
            localCreated = metaDataLocal.CreatedOn
        else:
            localId = None
            localCreated = None

        if not localId:
            if iconInfo['url']:
                needToUploadNew = True

        else:
            if iconInfo['url']:
                if (not iconInfo['created']) or (not localCreated) or (localCreated < iconInfo['created']):
                    shouldRemoveOld = True
                    needToUploadNew = True
            else:
                shouldRemoveOld = True

        if shouldRemoveOld:
            try:
                self.personIconService.detachIcon(userId)
                self.metaInfoService.delete(localId)
            except InputError:
                log.error('Can not remove old icon for chained user %s' % userId)

        if needToUploadNew:
            try:
                iconContent = ChainedIconContent(iconInfo['url'], iconInfo['name'])
                imageData = self.metaDataService.insert(userId, iconContent, 'http')
                if (not imageData) or (not imageData.Id):
                    return
                self.personIconService.setIcon(userId, imageData.Id)
            except InputError:
                log.error('Can not upload icon for chained user %s' % userId)
