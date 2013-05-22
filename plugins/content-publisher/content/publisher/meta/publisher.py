'''
Created on Mar 14, 2013

@package: content publisher
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Petr Jasek

Contains MongoDB meta for content publisher API.
'''

from collections import deque
from mongoengine.document import EmbeddedDocument, Document
from mongoengine.fields import StringField, IntField, EmbeddedDocumentField, \
    ListField, DateTimeField

# ----------------------------------------------------------------

class Ref(EmbeddedDocument):
    '''
    Ref
    '''
    idRef = StringField()
    itemClass = StringField()
    residRef = StringField()
    href = StringField()
    size = IntField()
    rendition = StringField()
    contentType = StringField()
    format = StringField()

# ----------------------------------------------------------------

class Group(EmbeddedDocument):
    '''
    Group
    '''
    id = StringField()
    role = StringField()
    mode = StringField()
    refs = ListField(EmbeddedDocumentField(Ref))

# ----------------------------------------------------------------

class Content(EmbeddedDocument):
    '''
    Content
    '''
    contenttype = StringField()
    content = StringField()
    residRef = StringField()
    href = StringField()
    size = IntField()
    rendition = StringField()
    storage = StringField()

# ----------------------------------------------------------------

class Item(Document):
    '''
    anyItem
    '''
    CLASS_TEXT = 'icls:text'
    CLASS_PACKAGE = 'icls:composite'

    guid = StringField(unique=True)
    version = IntField(required=True)
    itemClass = StringField()
    headline = StringField()
    slugline = StringField()
    byline = StringField()
    creditline = StringField()
    firstCreated = DateTimeField()
    versionCreated = DateTimeField()
    publishedOn = DateTimeField()

    groups = ListField(EmbeddedDocumentField(Group))
    contents = ListField(EmbeddedDocumentField(Content))

    copyrightHolder = StringField()

    meta = {
        'collection': 'items',
        'allow_inheritance': False,
        'indexes': [('itemClass', '-versionCreated')]
        }

    def get_refs(self, role):
        items = []
        queue = deque((role,))
        while len(queue):
            role = queue.popleft()
            refs = []
            for group in self.groups:
                if group.id == role:
                    refs += group.refs
            for ref in refs:
                if ref.idRef:
                    queue.append(ref.idRef)
                else:
                    items.append(ref)
        return items
