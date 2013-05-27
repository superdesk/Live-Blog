'''
Created on May 24, 2013

@package: content newsml
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for the newsml content export.
'''

from ..api.export import IItemNewsMLService
from ally.cdm.spec import ICDM
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from content.packager.api.item import IItemService, Item
from io import BytesIO
from superdesk.user.api.user import IUserService, User
from content.packager.api.item_content import IItemContentService, ItemContent

# --------------------------------------------------------------------

@injected
@setup(IItemNewsMLService, name='itemNewsMLService')
class ItemNewsMLService(IItemNewsMLService):
    '''
    Implementation for @see: IItemNewsMLService
    '''
    
    itemService = IItemService; wire.entity('itemService')
    itemContentService = IItemContentService;  wire.entity('itemContentService')
    userService = IUserService; wire.entity('userService')
    cdmNewsML = ICDM; wire.entity('cdmNewsML')
    
    copy_right = 'Sourcefabric o.p.s.'; wire.config('copy_right', doc='''
    The copyright holder for the export.
    ''')
    provider = 'Sourcefabric'; wire.config('provider', doc='''
    The provider for the export.
    ''')
    time_zone = '+02:30'; wire.config('time_zone', doc='''
    The time zone to be added for date time exports.
    ''')
    
    def __init__(self):
        assert isinstance(self.itemService, IItemService), 'Invalid item service %s' % self.itemService
        assert isinstance(self.cdmNewsML, ICDM), 'Invalid NewsML CDM %s' % self.cdmNewsML
    
    def getNewsML(self, guid, scheme):
        '''
        @see: IItemNewsMLService.getNewsML
        '''
        item = self.itemService.getById(guid)
        newsMl = BytesIO(b''.join(data.encode() for data in self.createNewsML(item)))
        self.cdmNewsML.publishFromFile('%s.xml' % guid, newsMl)
        return self.cdmNewsML.getURI('%s.xml' % guid, scheme)
        
    def createNewsML(self, item):
        '''
        Creates the NewsML content.
        '''
        assert isinstance(item, Item), 'Invalid item %s' % item
        versionCreated = '%s%s' % ((item.VersionCreated or item.FirstCreated).strftime('%Y-%m-%dT%H:%M:%S'), self.time_zone)
        contentCreated = (item.VersionCreated or item.FirstCreated).strftime('%Y-%m-%d')
        creator = self.userService.getById(item.Creator)
        assert isinstance(creator, User)
        creatorName = creator.FullName or creator.Name
        
        lead, content = [], []
        for itemContent in self.itemContentService.getAll():
            assert isinstance(itemContent, ItemContent)
            if itemContent.Item != item.GUId: continue
            if itemContent.ResidRef == 'Lead': lead.append(itemContent.Content)
            else: content.append(itemContent.Content)
        lead.extend(content)
        content = ''.join(lead)
        content = content.replace('<br>', '')
        return (
'''<?xml version="1.0" encoding="UTF-8" ?>
<newsItem guid="''', item.GUId, '''"
    version="''', str(item.Version), '''" xmlns="http://iptc.org/std/nar/2006-10-01/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://iptc.org/std/nar/2006-10-01/
    ../XSD/NewsML-G2/2.7/specification/NewsML-G2_2.7-spec-NewsItem-Core.xsd" standard="NewsML-G2" standardversion="2.7" xml:lang="en-US">
    
    <catalogRef href="http://www.iptc.org/std/catalog/catalog.IPTC-G2-Standards_13.xml" />
    
    <rightsInfo>
        <copyrightHolder literal="''', self.copy_right, '''" />
    </rightsInfo>
    
    <itemMeta>
        <itemClass qcode="icls:text" />
        <provider literal="''', self.provider, '''" />
        <versionCreated>''', versionCreated , '''</versionCreated>
    </itemMeta>
    
    <contentMeta>
        <contentCreated>''', contentCreated, '''</contentCreated>
        ''',
        '''
        <creator>
            <name>''', creatorName, '''</name>
        </creator>
        <language tag="en-US" />
        ''',
        '''
        <slugline>''' + item.SlugLine + '''</slugline>
        ''' if item.SlugLine is not None else '',
        '''
        <headline>''' + item.HeadLine + '''</headline>
        ''' if item.HeadLine is not None else '',
        '''
    </contentMeta>
    
    <contentSet>
        <inlineXML contenttype="application/nitf+xml">
            <nitf xmlns="http://iptc.org/std/NITF/2006-10-18/">
                <body>
                    <body.head>''',
                    '''
                        <hedline><hl1>''' + item.HeadLine + '''</hl1></hedline>
                    ''' if item.HeadLine is not None else '',
                    '''
                        <byline>
                            <byttl>By ''', creatorName, '''</byttl>
                        </byline>
                    </body.head>
                    <body.content>''',
                    content,
                    '''
                    </body.content>
                </body>
            </nitf>
        </inlineXML>
    </contentSet>

</newsItem>
''')
