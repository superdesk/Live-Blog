'''
Created on Dec 13, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the mongo engine meta for package item API.
'''

from mongoengine.fields import StringField, ListField, EmbeddedDocumentField
from ally.api.validate import validate, ReadOnly
from content.base.meta.mengine.item import ItemMapped
from content.package.api.item_package import ItemPackage, TYPE_PACKAGE, Ref,\
    Group
from mongoengine.document import EmbeddedDocument

# --------------------------------------------------------------------

class RefMapped(EmbeddedDocument, Ref):
    '''
    Provides the mapping for Ref model.
    '''
    GUID = StringField(max_length=100, primary_key=True)
    ResidRef = StringField(max_length=100, required=True)
    Title = StringField(max_length=1000, required=True)
    Description = StringField(max_length=10000)

class GroupMapped(EmbeddedDocument, Group):
    '''
    Provides the mapping for Group model.
    '''
    GUID = StringField(max_length=100, primary_key=True)
    Id = StringField(max_length=100, required=True)
    Role = StringField(max_length=100, required=True)
    Mode = StringField(max_length=100)
    Title = StringField(max_length=1000)
    Refs = ListField(EmbeddedDocumentField(RefMapped))

@validate(ReadOnly(ItemPackage.Type))
class ItemPackageMapped(ItemMapped, ItemPackage):
    '''
    Provides the mapping for ItemPackage.
    '''
    Root = StringField(max_length=100, required=True)
    Groups = ListField(EmbeddedDocumentField(GroupMapped), required=True)
    
    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.Type = TYPE_PACKAGE
