'''
Created on Jan 20, 2014

@package: livedesk
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the implementation for version API.
'''

from ally.container.ioc import injected
from ally.container.support import setup
from livedesk.api.version import IVersionService, Version
from ally.container import wire
from ally.support.sqlalchemy.session import SessionSupport
from superdesk.general_setting.api.general_setting import IGeneralSettingService,\
    GeneralSetting, QGeneralSetting
from ally.cdm.spec import ICDM
from io import BytesIO

@injected
@setup(IVersionService, name='versionService')
class VersionService(SessionSupport, IVersionService):
    '''
    Implementation for @see: IVersionService
    '''

    generalSettingService = IGeneralSettingService; wire.entity('generalSettingService')
    versionCDM = ICDM; wire.entity('versionCDM')
    #configuration service used to retrieve configuration data
    version_file = '/lib/livedesk-embed/scripts/js/version.js'; wire.config('version_file', doc='''The file version location embed js files
    ''')
    allypy_version_file = '/lib/core/scripts/js/version.js'; wire.config('allypy_version_file', doc='''The file version location for ally-py js files
    ''')
    embed_version_file = '/lib/embed/scripts/js/version.js'; wire.config('embed_version_file', doc='''The file version location for SEO embed js files
    ''')
    major_key = 'major'
    minor_key = 'minor'
    revision_key = 'revision'
    version_group = 'version'


    def get(self):
        '''
        @see: IVersionService.get
        '''
        version = self.readVersion()
        
        return version

    def incrementRevision(self):
        '''
        @see: IVersionService.incrementRevision
        '''
        
        version = self.readVersion()
        version.Revision = version.Revision + 1
        self.writeVersion(version)
        
    def resetRevision(self):
        '''
        @see: IVersionService.resetRevision
        '''
        
        version = self.readVersion()
        version.Revision = 0
        self.writeVersion(version)
        
    def readVersion(self):
        '''
        Read the version_file and parse it and then create the Version entity
        '''
        
        version = Version()
        version.Major = 0
        version.Minor = 0
        version.Revision = 0
        
        generalSettings = self.generalSettingService.getAll(q=QGeneralSetting(group=self.version_group))
        
        for generalSetting in generalSettings:
            if generalSetting.Key == self.major_key and generalSetting.Value.isdigit(): 
                version.Major = int(generalSetting.Value)
            elif generalSetting.Key == self.minor_key and generalSetting.Value.isdigit():
                version.Minor = int(generalSetting.Value)
            elif generalSetting.Key == self.revision_key and generalSetting.Value.isdigit():
                version.Revision = int(generalSetting.Value)         
        
        return version
        
        
    def writeVersion(self, version):
        '''
        Write the version entity to the version_file
        '''
        
        generalSetting = GeneralSetting()
        generalSetting.Key = self.revision_key
        generalSetting.Group = self.version_group
        generalSetting.Value = str(version.Revision)
        
        self.generalSettingService.update(generalSetting)
        
        
        content = '''liveblog.callbackVersion({
                        major: %s,
                        minor: %s,
                        revision: %s
                    });''' % (str(version.Major), str(version.Minor), str(version.Revision)) 
        
        self.versionCDM.publishContent(self.version_file, BytesIO(content.encode(encoding='utf_8')))         
        
        
        content = '''allyAdmin.callbackVersion({
                        major: %s,
                        minor: %s,
                        revision: %s
                    });''' % (str(version.Major), str(version.Minor), str(version.Revision)) 
        
        self.versionCDM.publishContent(self.allypy_version_file, BytesIO(content.encode(encoding='utf_8'))) 


        content = '''liveblog.callbackVersion({
                        major: %s,
                        minor: %s,
                        revision: %s
                    });''' % (str(version.Major), str(version.Minor), str(version.Revision)) 
        
        self.versionCDM.publishContent(self.embed_version_file, BytesIO(content.encode(encoding='utf_8')))    
