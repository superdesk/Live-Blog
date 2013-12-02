'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the mongo engine meta for item API.
'''

from datetime import datetime
from mongoengine.fields import StringField, IntField, DateTimeField

from content.base.api.item import Item
from mongo_engine.support.document import Base


# --------------------------------------------------------------------
class ItemMapped(Base, Item):
    '''
    Provides the mapping for Item.
    '''
    GUID = StringField(max_length=1000, primary_key=True)
    Version = IntField(min_value=1, default=1, required=True)
    CreatedOn = DateTimeField(default=datetime.utcnow, required=True)
    Type = StringField(max_length=100, required=True)
