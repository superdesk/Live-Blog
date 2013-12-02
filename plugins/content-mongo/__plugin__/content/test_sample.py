'''
Created on Nov 29, 2013

@author: chupy
'''

from ally.container import app
from ..mongo_engine.db_application import database, database_url
from mongoengine.connection import connect, disconnect
from content.base.meta.mengine.item import ItemMapped
from content.resource.meta.mengine.item_resource import ItemResourceMapped
from content.resource.meta.mengine.item_text import ItemTextMapped
    
@app.deploy()
def populate():
    connect(database(), host=database_url())
    ItemMapped.drop_collection()
    
    item = ItemMapped()
    item.GUID = '111'
    item.Type = 'Gabriel'
    item.save()
    
    item = ItemMapped()
    item.GUID = '222'
    item.Type = 'Nistor'
    item.save()
    
    item = ItemMapped()
    item.GUID = '333'
    item.Type = 'Alexandra'
    item.save()
    
    item = ItemMapped()
    item.GUID = '444'
    item.Type = 'Cineva'
    item.save()
    
    item = ItemResourceMapped()
    item.GUID = 'Resc1'
    item.HeadLine = 'Olla from resource 1'
    item.ContentSet = 'http://Somewere'
    item.Class = 'Dummy'
    item.save()
    
    item = ItemTextMapped()
    item.GUID = 'Text1'
    item.HeadLine = 'Olla from text 1'
    item.ContentSet = 'http://Somewere'
    item.save()
    
    disconnect()
