'''
Created on August 27, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for blog sms API.
'''

from livedesk.api.sms import IBlogSMSService
from ally.support.sqlalchemy.session import SessionSupport
from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.post.meta.post import PostMapped
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.source.meta.source import SourceMapped
from superdesk.source.meta.type import SourceTypeMapped
from livedesk.api.blog_post import QWithCId
from livedesk.meta.blog_post_tag import BlogPostTagMapped
from superdesk.tag.meta.tag import TagMapped
from superdesk.tag.meta.type import TagTypeMapped
from sqlalchemy.sql.expression import exists, and_
from ally.api.criteria import AsRange, AsBoolean
from ally.exception import InputError
from ally.internationalization import _
from ally.support.sqlalchemy.util_service import buildLimits
from ally.api.extension import IterPart
from sqlalchemy.orm.exc import NoResultFound
from __plugin__.frontline_inlet.populate_default_data import sms_source_types
from __plugin__.livedesk.tag import view_tag_type_key, view_hidden_tag_key

# --------------------------------------------------------------------

@injected
@setup(IBlogSMSService, name='blogSMSService')
class BlogSMSServiceAlchemy(SessionSupport, IBlogSMSService):
    '''
    Implementation for @see: IBlogSMSService
    '''

    def __init__(self):
        '''
        Construct the blog sms service.
        '''
        self.smsTypeKeys = sms_source_types()

        self.tagTypeKeyView = view_tag_type_key()
        self.tagKeyViewHidden = view_hidden_tag_key()

    def getMessages(self, blogId, sourceId=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IBlogSMSService.getMessages
        '''
        sql = self._commonSQL(blogId, sourceId, q)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def getPublishedMessages(self, blogId, sourceId=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IBlogSMSService.getPublishedMessages
        '''
        sql = self._commonSQL(blogId, sourceId, q)
        sql = sql.filter(PostMapped.PublishedOn != None)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def getUnpublishedMessages(self, blogId, sourceId=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IBlogSMSService.getUnpublishedMessages
        '''
        sql = self._commonSQL(blogId, sourceId, q)
        sql = sql.filter(PostMapped.PublishedOn == None)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def _commonSQL(self, blogId, sourceId=None, q=None):
        '''
        shared part of taking the relevant sms posts
        '''
        sql = self.session().query(PostMapped)

        if q:
            assert isinstance(q, QWithCId), 'Invalid query %s' % q
            if (QWithCId.isHidden in q) and (AsBoolean.value in q.isHidden):
                hiddenId = self._takeHiddenId()
                hiddenSQL = exists().where(and_(BlogPostTagMapped.Post == PostMapped.Id, BlogPostTagMapped.Blog == blogId, BlogPostTagMapped.typeId == hiddenId))
                if q.isHidden.value:
                    sql = sql.filter(hiddenSQL)
                else:
                    sql = sql.filter(~hiddenSQL)

            if (QWithCId.cId in q) and q.cId:
                if AsRange.start in q.cId:
                    sql = sql.filter(PostMapped.Id >= q.cId.start)
                if AsRange.since in q.cId:
                    sql = sql.filter(PostMapped.Id > q.cId.since)
                if AsRange.end in q.cId:
                    sql = sql.filter(PostMapped.Id <= q.cId.end)
                if AsRange.until in q.cId:
                    sql = sql.filter(PostMapped.Id < q.cId.until)

            if (QWithCId.search in q) and q.search:
                for searchValue in [q.search.ilike, q.search.like]:
                    if not searchValue:
                        continue
                    if not '%' in searchValue:
                        if not searchValue.endswith('%'):
                            searchValue = searchValue + '%'
                        if not searchValue.startswith('%'):
                            searchValue = '%' + searchValue
                    sql = sql.filter(or_(PostMapped.Content.ilike(all), PostMapped.ContentPlain.ilike(all)))

        sql = sql.join(CollaboratorMapped, CollaboratorMapped.Id == PostMapped.Author)
        sql = sql.join(SourceMapped, SourceMapped.Id == CollaboratorMapped.Source)

        if sourceId:
            if not self._isTypeSMS(sourceId):
                raise InputError(_('Not SMS source type'))
            sql = sql.filter(SourceMapped.Id == sourceId)
        else:
            sql = sql.join(SourceTypeMapped, SourceTypeMapped.Key == self.smsTypeKey)
            sql = sql.filter(SourceTypeMapped.Key._in(self.smsTypeKeys))

    def _takeHiddenId(self):
        '''
        Provides Id of the tag that specifies hidden posts
        '''
        sql = self.session().query(TagMapped.id).filter(TagMapped.Key == self.tagKeyViewHidden)
        sql = sql.join(TagTypeMapped, TagTypeMapped.id == TagMapped.typeId).filter(TagTypeMapped.Key == self.tagTypeKeyView)

        try:
            return sql.one()[0]
        except NoResultFound:
            raise InputError(_('No tag for hidden posts'))

    def _isTypeSMS(self, sourceId):
        '''
        Checks whether the source id is of the sms source type
        '''
        sql = self.session().query(SourceTypeMapped.Key).join(SourceMapped, SourceMapped.typeId == SourceTypeMapped.id)
        sql = sql.filter(SourceMapped.Id == sourceId)

        try:
            if sql.one()[0] in self.smsTypeKeys:
                return True
            else:
                return False
        except NoResultFound:
            raise InputError(_('No sms source with id %s') % sourceId)
