'''
Created on Nov 29, 2013

@author: chupy
'''

from ally.container import app
from ..mongo_engine.db_application import database, database_url

@app.deploy()
def populate():
    from mongoengine.connection import connect, disconnect
    from content.base.meta.item_mongo import ItemMapped
    
    connect(database(), host=database_url())
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
    disconnect()
