'''
Created on Nov 29, 2013

@author: chupy
'''

from ally.container import app
from ..mongo_engine.db_application import database, database_url
from mongoengine.connection import connect, disconnect
from content.resource.meta.mengine.item_text import ItemTextMapped
from content.package.meta.mengine.item_package import ItemPackageMapped

@app.deploy()
def populate():
    connect(database(), host=database_url())
    ItemTextMapped.drop_collection()
    
    item1 = ItemTextMapped()
    item1.GUID = '111'
    item1.Version = 1
    item1.Type = 'resource'
    item1.ContentType = 'text'
    item1.Provider = 'AAP'
    item1.PubStatus = 'usable'
    item1.HeadLine = 'good news today'
    item1.ContentSet = 'http://some.url.com/resource/id111'
    item1.save()

    item2 = ItemTextMapped()
    item2.GUID = '222'
    item2.Version = 1
    item2.Type = 'resource'
    item2.ContentType = 'text'
    item2.Provider = 'AAP'
    item2.PubStatus = 'usable'
    item2.HeadLine = 'best news tomorrow'
    item2.ContentSet = 'http://some.url.com/resource/id222'
    item2.save()

    pack = ItemPackageMapped()
    pack.GUID = '333'
    pack.Version = 1
    pack.Type = 'package'
    pack.Provider = 'AAP'
    pack.PubStatus = 'usable'
    pack.Items.append(item1)
    pack.Items.append(item2)
    pack.save()
    
    disconnect()
