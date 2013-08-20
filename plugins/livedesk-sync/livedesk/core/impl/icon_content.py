'''
Created on August 19, 2013

@package: livedesk-sync
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Content for icons of collaborators of chained blogs.
'''

import socket
import logging
from urllib.request import urlopen
from ally.api.model import Content
from urllib.error import HTTPError
from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.media_archive.api.meta_data import IMetaDataUploadService
from superdesk.media_archive.api.meta_info import IMetaInfoService
from superdesk.person_icon.api.person_icon import IPersonIconService
from ally.container import wire

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(name='chainedIconContent')
class ChainedIconContent(Content):
    '''
    Simple remote icon content taking
    '''

    metaDataService = IMetaDataUploadService; wire.entity('metaDataService')

    metaInfoService = IMetaInfoService; wire.entity('metaInfoService')

    personIconService = IPersonIconService; wire.entity('personIconService')

    inner = {}

    def initialize(self, userId, createdOn, contentURL, fileName):
        '''
        Constructs the content.

        @param contentURL: string
            The URL of the icon to be downloaded.
        @param fileName: string
            The name of file under that the icon should be saved.
        '''
        self.inner['user'] = userId
        self.inner['created'] = createdOn
        self.inner['url'] = contentURL
        self.inner['response'] = None
        self.name = fileName
        self.charSet = 'binary'
        self.type = 'image'
        self.length = 0

    def read(self, nbytes=None):
        '''
        @see: Content.read
        '''
        if not self.inner['response']:
            try: self.inner['response'] = urlopen(self.inner['url'])
            except (HTTPError, socket.error) as e:
                log.error('Can not read icon image data %s' % e)
                return
            if not self.inner['response']:
                log.error('Can not read icon image data %s' % e)
                return

            self.type = self.inner['response'].getheader('Content-Type')
            if not self.type:
                self.type = 'image'
            self.length = self.inner['response'].getheader('Content-Length')
            if not self.length:
                self.length = 0

        if self.inner['response'].closed:
            return ''

        if nbytes:
            return self.inner['response'].read(nbytes)

        return self.inner['response'].read()

    def next(self):
        '''
        @see: Content.next
        '''
        return None

    def synchronizeIcon(self, userId, createdOn, contentURL, fileName):
        '''
        Synchronizing local icon according to the remote one
        '''
        self.initialize(userId, createdOn, contentURL, fileName)

        if not self.inner['user']:
            return

        shouldRemoveOld = False
        needToUploadNew = False

        try:
            metaDataLocal = self.personIconService.getByPersonId(self.inner['user'])
            localId = metaDataLocal.Id
            localCreated = metaDataLocal.CreatedOn
        except:
            localId = None
            localCreated = None

        if not localId:
            if self.inner['url']:
                needToUploadNew = True

        else:
            if self.inner['url']:
                if (not self.inner['created']) or (not localCreated) or (localCreated < self.inner['created']):
                    shouldRemoveOld = True
                    needToUploadNew = True
            else:
                shouldRemoveOld = True

        if shouldRemoveOld:
            try:
                self.personIconService.detachIcon(self.inner['user'])
                self.metaInfoService.delete(localId)
            except: pass

        if needToUploadNew:
            #try:
                imageData = self.metaDataService.insert(self.inner['user'], self, 'http')
                if (not imageData) or (not imageData.Id):
                    return
                self.personIconService.setIcon(self.inner['user'], imageData.Id)
            #except: pass
