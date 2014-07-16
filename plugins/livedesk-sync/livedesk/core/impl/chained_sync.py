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
from datetime import datetime
from sched import scheduler
from threading import Thread
from urllib.request import urlopen, Request
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
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
from superdesk.post.api.post import Post, IPostService
from uuid import uuid4
from random import randint

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(name='chainedSynchronizer')
class ChainedSyncProcess:
    '''
    Chained sync process.
    '''

    blogSyncService = IBlogSyncService; wire.entity('blogSyncService')
    # blog sync service used to retrieve blogs set on auto publishing

    sourceService = ISourceService; wire.entity('sourceService')
    # source service used to retrieve source data

    blogPostService = IBlogPostService; wire.entity('blogPostService')
    # blog post service used to insert blog posts
    
    postService = IPostService; wire.entity('postService')
    # post service used to insert/update posts

    collaboratorService = ICollaboratorService; wire.entity('collaboratorService')
    # blog post service used to retrive collaborator

    userService = IUserService; wire.entity('userService')

    metaDataService = IMetaDataUploadService; wire.entity('metaDataService')

    metaInfoService = IMetaInfoService; wire.entity('metaInfoService')

    personIconService = IPersonIconService; wire.entity('personIconService')

    syncThreads = {}
    # dictionary of threads that perform synchronization

    sync_interval = 53; wire.config('sync_interval', doc='''
    The number of seconds to perform sync for blogs.''')
    
    timeout_inteval = 4#; wire.config('timeout_interval', doc='''
    #The number of seconds after the sync ownership can be taken.''')
    
    published_posts_field = 'PostPublished'; wire.config('published_posts_field', doc='''
    The field that contains URI for published posts retrieval''')
    
    user_type_key = 'chained blog'; wire.config('user_type_key', doc='''
    The user type that is used for the anonymous users of chained blog posts''')
    
    blog_provider_type = 'blog provider'; wire.config('blog_provider_type', doc='''
    Key of the source type for blog providers''')

    acceptType = 'text/json'
    # mime type accepted for response from remote blog
    encodingType = 'UTF-8'
    # character encoding type accepted for response from remove blog
    


    @app.deploy
    def startChainSyncThread(self):
        '''
        Starts the chain sync thread.
        '''
        schedule = scheduler(time.time, time.sleep)
        def syncChains():
            self.syncChains()
            schedule.enter(self.sync_interval, 1, syncChains, ())
        schedule.enter(self.sync_interval, 1, syncChains, ())
        scheduleRunner = Thread(name='chained sync', target=schedule.run)
        scheduleRunner.daemon = True
        scheduleRunner.start()
        log.info('Started the chained blogs automatic synchronization.')

    def syncChains(self):
        '''
        Read all chained blog sync entries and sync with the corresponding blogs.
        '''        
        log.info('Start chained blog synchronization')
        
        sleep_time = randint(0, 1000) * 0.001
        time.sleep(sleep_time)
        
        for blogSync in self.blogSyncService.getBySourceType(self.blog_provider_type): 
            assert isinstance(blogSync, BlogSync)
            key = (blogSync.Blog, blogSync.Source)
            thread = self.syncThreads.get(key)
            if thread:
                assert isinstance(thread, Thread), 'Invalid thread %s' % thread
                if thread.is_alive(): 
                    log.info('Chained thread for blog %d is alive', blogSync.Blog)
                    continue


            if not self.blogSyncService.checkTimeout(blogSync.Id, self.timeout_inteval * self.sync_interval): 
                log.info('Chained thread for blog %d is already taken', blogSync.Blog)
                continue
            
            self.syncThreads[key] = Thread(name='blog %d sync' % blogSync.Blog,
                                           target=self._syncChain, args=(blogSync,))
            self.syncThreads[key].daemon = True
            self.syncThreads[key].start()
            log.info('Chained thread started for blog id %d and source id %d', blogSync.Blog, blogSync.Source)
            
        log.info('End chained blog synchronization')

    def _syncChain(self, blogSync):
        '''
        Synchronize the blog for the given sync entry.

        @param blogSync: BlogSync
            The blog sync entry declaring the blog and source from which the blog
            has to be updated.
        '''
        assert isinstance(blogSync, BlogSync), 'Invalid blog sync %s' % blogSync
        source = self.sourceService.getById(blogSync.Source)
        
        log.info('_syncChain blogId=%d, sourceId=%d', blogSync.Blog, blogSync.Source)
        
        assert isinstance(source, Source)
        (scheme, netloc, path, params, query, fragment) = urlparse(source.URI)
        
        if not scheme: scheme  = 'http'

        blogUrl = urlunparse((scheme, netloc, path, params, query, fragment))
        blogPublishedPostsURI = self._readPublishedPostsUrl(blogUrl, self.published_posts_field)
        if not blogPublishedPostsURI:
            log.error('Unable to sync blog: %s' % (source.URI,))
            return

        (scheme, netloc, path, params, query, fragment) = urlparse(blogPublishedPostsURI)
        if not scheme: scheme  = 'http'

        q = parse_qsl(query, keep_blank_values=True)
        q.append(('asc', 'cId'))
        q.append(('cId.since', blogSync.CId if blogSync.CId is not None else 0))

        url = urlunparse((scheme, netloc, path, params, urlencode(q), fragment))
        req = Request(url, headers={'Accept' : self.acceptType, 'Accept-Charset' : self.encodingType,
                                    'X-Filter' : '*,Creator.*,Author.User.*,Author.Source.*', 'User-Agent' : 'Magic Browser'})
        
        try: resp = urlopen(req)
        except (HTTPError, socket.error) as e:
            log.error('Read error on %s: %s' % (source.URI, e))
            blogSync.LastActivity = None 
            self.blogSyncService.update(blogSync)
            return
        
        if str(resp.status) != '200':
            log.error('Read problem on %s, status: %s' % (source.URI, resp.status))
            blogSync.LastActivity = None 
            self.blogSyncService.update(blogSync)
            return

        try: msg = json.load(codecs.getreader(self.encodingType)(resp))
        except ValueError as e:
            log.error('Invalid JSON data %s' % e)
            blogSync.LastActivity = None 
            self.blogSyncService.update(blogSync)
            return

        usersForIcons = {}
        for post in msg['PostList']:
            try:
                if post['IsPublished'] != 'True': continue
                
                insert = False 
                if 'Uuid' in post: 
                    uuid = post['Uuid']
                    localPost = self.postService.getByUuidAndSource(uuid, source.Id) 
                else: 
                    #To support old instances that don't have Uuid attribute
                    uuid = str(uuid4().hex)
                    localPost = None 
                    
                if localPost == None:  
                    if 'DeletedOn' in post: continue    
                    localPost = Post()
                    localPost.Uuid = uuid
                    insert = True
                
                if 'DeletedOn' not in post:       
                    #TODO: workaround, read again the Author because sometimes we get access denied
                    post['Author'] = self._readAuthor(post['Author']['href'])   
                    post['Creator'] = self._readCreator(post['Creator']['href'])
                    
                    #if exists local, update it, otherwise continue the original insert
                    localPost.Type = post['Type']['Key']
                    localPost.Author, localPost.Creator, needUpdate, isAuthor = self._getCollaboratorForAuthor(post['Author'], post['Creator'], source)
                    localPost.Feed = source.Id
                    localPost.Meta = post['Meta'] if 'Meta' in post else None
                    localPost.ContentPlain = post['ContentPlain'] if 'ContentPlain' in post else None
                    localPost.Content = post['Content'] if 'Content' in post else None
                    localPost.Order = post['Order'] if 'Order' in post else None
                    localPost.CreatedOn = current_timestamp()              
                    if blogSync.Auto: 
                        localPost.PublishedOn = current_timestamp()
                        localPost.WasPublished = True
                    
                    log.info("received post: %s", str(localPost))
      
                    if localPost.Creator and (localPost.Creator not in usersForIcons) and needUpdate:
                        try:
                            if isAuthor: usersForIcons[localPost.Creator] = post['Author']['User']
                            else: usersForIcons[localPost.Creator] = post['Creator']
                        except KeyError:
                            pass
                    
                else:
                    localPost.DeletedOn = datetime.strptime(post['DeletedOn'], '%m/%d/%y %I:%M %p')
                            
                # prepare the blog sync model to update the change identifier
                blogSync.CId = int(post['CId']) if blogSync.CId is None or int(post['CId']) > blogSync.CId else blogSync.CId

                if insert: self.blogPostService.insert(blogSync.Blog, localPost)
                else: self.blogPostService.update(blogSync.Blog, localPost)
                
                # update blog sync entry
                blogSync.LastActivity = datetime.now().replace(microsecond=0)
                self.blogSyncService.update(blogSync)
                
            except KeyError as e:
                log.error('Post from source %s is missing attribute %s' % (source.URI, e))
            except Exception as e:
                log.error('Error in source %s post: %s' % (source.URI, e))

        self._updateIcons(usersForIcons)
        
        blogSync.LastActivity = None 
        self.blogSyncService.update(blogSync)
   

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
        
        user = User()
        
        isAuthor = False
        
        if 'User' in author: 
            userJSON = author['User']  
            isAuthor = True
        else: userJSON = creator
                                            
        #To support old instances that don't have Uuid attribute 
        if 'Uuid' in userJSON: user.Uuid = userJSON.get('Uuid', '')
        else: user.Uuid = str(uuid4().hex)
        
        if 'Cid' in userJSON: cid = int(userJSON.get('Cid', ''))
        else: cid = None
        
        user.Name = user.Uuid
        user.FirstName, user.LastName = userJSON.get('FirstName', ''), userJSON.get('LastName', '')
        user.Address, user.PhoneNumber = userJSON.get('Address', ''), userJSON.get('PhoneNumber', '')
        user.EMail, user.Password = userJSON.get('EMail', ''), '~'
        user.Type = self.user_type_key

        
        needUpdate = True
        try: userId = self.userService.insert(user)
        except InputError:
            localUser = self.userService.getByUuid(user.Uuid)
            userId = localUser.Id
            if localUser.Type == self.user_type_key and (cid is None or localUser.Cid < cid): 
                user.Id = localUser.Id
                user.Type = localUser.Type
                user.Cid = cid
                self.userService.update(user)
            else: needUpdate = False    
            
        collaborator = Collaborator()
        collaborator.User, collaborator.Source = userId, source.Id
        try: collaboratorId = self.collaboratorService.insert(collaborator)
        except InputError:
            collaborators = self.collaboratorService.getAll(userId, source.Id)
            collaboratorId = collaborators[0].Id
        
        if isAuthor:
            return [collaboratorId, userId, needUpdate, isAuthor]
        else:    
            q = QSource(name=author['Source']['Name'], isModifiable=False)
            sources = self.sourceService.getAll(q=q)
            if not sources: raise Exception('Invalid source %s' % q.name)
            collaborators = self.collaboratorService.getAll(userId=None, sourceId=sources[0].Id)
            if collaborators: return [collaborators[0].Id, userId, needUpdate, isAuthor]
            else:
                collaborator = Collaborator()
                collaborator.Source = sources[0].Id
                return [self.collaboratorService.insert(collaborator), userId, needUpdate, isAuthor]

    def _updateIcons(self, usersData):
        '''
        Setting the icon of the user
        '''
        userIcons = {}
        for userId in usersData:
            userJSON = usersData[userId]
            userIcons[userId] = {'url': None, 'name': None}

            try:
                metaDataIconJSON = userJSON['MetaDataIcon']
                metaDataIconURL = metaDataIconJSON.get('href', '')
                if not metaDataIconURL:
                    continue
                
                (scheme, netloc, path, params, query, fragment) = urlparse(metaDataIconURL)
                if not scheme: 
                    metaDataIconURL = urlunparse(('http', netloc, path, params, query, fragment))

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
            localName = metaDataLocal.Name
        else:
            localId = None
            localName = None

        if not localId:
            if iconInfo['url']:
                needToUploadNew = True

        else:
            if iconInfo['url']:
                #on changed avatar the name of the file is changed
                if (not iconInfo['name']) or (not localName) or (localName != iconInfo['name']):
                    shouldRemoveOld = True
                    needToUploadNew = True
            else:
                shouldRemoveOld = True

        if shouldRemoveOld:
            try:
                self.personIconService.detachIcon(userId)
                #self.metaInfoService.delete(localId)
            except InputError:
                log.error('Can not remove old icon for chained user %s' % userId)

        if needToUploadNew:
            try:
                iconContent = ChainedIconContent(iconInfo['url'], iconInfo['name'])
                imageData = self.metaDataService.insert(userId, iconContent, 'http')
                if (not imageData) or (not imageData.Id):
                    return
                self.personIconService.setIcon(userId, imageData.Id, False)
            except InputError:
                log.error('Can not upload icon for chained user %s' % userId)
                
                
    def _readAuthor(self, url):
        
        (scheme, netloc, path, params, query, fragment) = urlparse(url)
        if not scheme: 
            url = urlunparse(('http', netloc, path, params, query, fragment))
        
        request = Request(url, headers={'Accept' : self.acceptType, 'Accept-Charset' : self.encodingType, 'User-Agent' : 'Magic Browser', 'X-Filter' : '*,User.*,Source.*'})
        
        try:
            response = urlopen(request)
        except (HTTPError, socket.error) as e:
            return None
        
        if str(response.status) != '200':
            return None
        
        try:
            return json.load(codecs.getreader(self.encodingType)(response))
        except ValueError as e:
            log.error('Invalid JSON data %s' % e)
            return None    
        
    def _readCreator(self, url):
        
        (scheme, netloc, path, params, query, fragment) = urlparse(url)
        if not scheme: 
            url = urlunparse(('http', netloc, path, params, query, fragment))
        
        request = Request(url, headers={'Accept' : self.acceptType, 'Accept-Charset' : self.encodingType, 'User-Agent' : 'Magic Browser', 'X-Filter' : '*'})
        
        try:
            response = urlopen(request)
        except (HTTPError, socket.error) as e:
            return None
        
        if str(response.status) != '200':
            return None
        
        try:
            return json.load(codecs.getreader(self.encodingType)(response))
        except ValueError as e:
            log.error('Invalid JSON data %s' % e)
            return None               

    def _readPublishedPostsUrl(self, url, field):
        request = Request(url, headers={'Accept' : self.acceptType, 'Accept-Charset' : self.encodingType, 'User-Agent' : 'Magic Browser'})

        try:
            response = urlopen(request)
        except (HTTPError, socket.error) as e:
            return None

        if str(response.status) != '200':
            return None

        try:
            blogInfo = json.load(codecs.getreader(self.encodingType)(response))
        except ValueError as e:
            log.error('Invalid JSON data %s' % e)
            return None

        if type(blogInfo) is not dict:
            log.error('Invalid blog info: not a struct')
            return None

        if field not in blogInfo:
            log.error('Invalid blog info: without ' + str(field))
            return None

        if type(blogInfo[field]) is not dict:
            log.error('Invalid blog info: ' + str(field) + ' is not a struct')
            return None

        if ('href' not in blogInfo[field]) or (not blogInfo[field]['href']):
            log.error('Invalid blog info: ' + str(field) + ' not with href part')
            return None

        if type(blogInfo[field]['href']) is not str:
            log.error('Invalid blog info: ' + str(field) + ' href part is not a string')
            return None

        return blogInfo[field]['href']

