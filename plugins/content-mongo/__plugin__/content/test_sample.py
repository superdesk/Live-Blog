'''
Created on Nov 29, 2013

@author: chupy
'''

from ally.container import app
from ..mongo_engine.db_application import database, mongo_database_url
from mongoengine.connection import connect, disconnect
from content.resource.meta.mengine.item_text import ItemTextMapped
from content.package.meta.mengine.item_package import ItemPackageMapped,\
    RefMapped, GroupMapped

@app.deploy()
def populate():
    connect(database(), host=mongo_database_url())
    ItemTextMapped.drop_collection()
    
    item = ItemTextMapped()
    item.GUID = '111'
    item.Version = 1
    item.Type = 'resource'
    item.ItemClass = 'text'
    item.Provider = 'AAP'
    item.PubStatus = 'usable'
    item.HeadLine = 'good news today'
    item.ContentSet = 'http://some.url.com/resource/id111'
    item.save()

    item = ItemTextMapped()
    item.GUID = '222'
    item.Version = 1
    item.Type = 'resource'
    item.ItemClass = 'text'
    item.Provider = 'AAP'
    item.PubStatus = 'usable'
    item.HeadLine = 'best news tomorrow'
    item.ContentSet = 'http://some.url.com/resource/id222'
    item.save()
    
    ref = RefMapped()
    ref.GUID = '444'
    ref.ResidRef = 'aap:ref1'
    ref.Title = 'best news tomorrow'
    ref.Description = 'description of best news tomorrow'
    
    group = GroupMapped()
    group.GUID = '555'
    group.Id = 'g1'
    group.Role = 'top news'
    group.Refs.append(ref)
    
    item = ItemPackageMapped()
    item.GUID = '333'
    item.Version = 1
    item.Type = 'package'
    item.ItemClass = 'composite'
    item.Provider = 'AAP'
    item.PubStatus = 'usable'
    item.Root = 'g1'
    item.Groups.append(group)
    item.save()
    
    disconnect()
