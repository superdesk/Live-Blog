'''
Created on Feb 11, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for blog collaborator group API.
'''

from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.internationalization import _
from datetime import timedelta
from livedesk.api.blog_collaborator_group import IBlogCollaboratorGroupService
from livedesk.core.spec import IBlogCollaboratorGroupCleanupService
from livedesk.meta.blog_collaborator import BlogCollaboratorMapped
from livedesk.meta.blog_collaborator_group import BlogCollaboratorGroupMapped, \
    BlogCollaboratorGroupMemberMapped
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.functions import current_timestamp
import logging
from sql_alchemy.support.util_service import SessionSupport
from ally.api.error import InputError
from sql_alchemy.support.mapper import InsertFromSelect, tableFor

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(IBlogCollaboratorGroupService, IBlogCollaboratorGroupCleanupService, name='blogCollaboratorGroupService')
class BlogCollaboratorGroupService(SessionSupport, IBlogCollaboratorGroupService, IBlogCollaboratorGroupCleanupService):
    '''
    Implementation for @see: IBlogCollaboratorGroupService
    '''
    
    group_timeout = 3600; wire.config('group_timeout', doc='''
    The number of seconds after which the blog collaborators group expires.
    ''')
    
    # ----------------------------------------------------------------

    def __init__(self):
        '''
        Construct the blog collaborators group service.
        '''
        assert isinstance(self.group_timeout, int), 'Invalid blog collaborators group timeout %s' % self.group_timeout
        self._group_timeout = timedelta(seconds=self.group_timeout)

    # ----------------------------------------------------------------

    def getById(self, groupId):
        '''
        @see IBlogCollaboratorGroupService.getById
        '''
        sql = self.session().query(BlogCollaboratorGroupMapped)
        sql = sql.filter(BlogCollaboratorGroupMapped.Id == groupId)

        try: 
            group = sql.one()
            return group
        except NoResultFound: raise InputError(_('No collaborator group'), BlogCollaboratorGroupMapped.Id)

    # ----------------------------------------------------------------
            
    def getAllMembers(self, groupId):
        '''
        @see IBlogCollaboratorGroupService.getAllMembers
        '''
        
        sql = self.session().query(BlogCollaboratorGroupMemberMapped).filter(BlogCollaboratorGroupMemberMapped.Group == groupId)
        
        return sql.all()

    # ----------------------------------------------------------------
    
    def insert(self, collaboratorGroup):
        '''
        @see IBlogCollaboratorGroupService.insert
        '''
        
        group = BlogCollaboratorGroupMapped()
        group.Blog = collaboratorGroup.Blog
        group.LastAccessOn = current_timestamp() 
        
        self.session().add(group)
        self.session().flush((group,))
              
        insert = InsertFromSelect(tableFor(BlogCollaboratorGroupMemberMapped), 'fk_group_id, fk_collaborator_id',
                                  select([group.Id, BlogCollaboratorMapped.blogCollaboratorId]).where(BlogCollaboratorMapped.Blog == group.Blog))
        self.session().execute(insert) 
        
        return group.Id  

    # ----------------------------------------------------------------
    
    def delete(self, groupId):
        '''
        @see IBlogCollaboratorGroupService.delete
        '''
        
        self.session().query(BlogCollaboratorGroupMemberMapped).delete(groupId)
        self.session().query(BlogCollaboratorGroupMapped).filter(BlogCollaboratorGroupMapped.Id == groupId).delete()
        
        return True

    # ----------------------------------------------------------------
        
    def addCollaborator(self, groupId, collaboratorId):
        '''
        @see IBlogCollaboratorGroupService.addCollaborator
        '''
        
        updateLastAccessOn(self.session(), groupId) 
        
        sql = self.session().query(BlogCollaboratorGroupMemberMapped)
        sql = sql.filter(BlogCollaboratorGroupMemberMapped.Group == groupId)
        sql = sql.filter(BlogCollaboratorGroupMemberMapped.BlogCollaborator == collaboratorId)
        if sql.count() == 1: return True
        
        member = BlogCollaboratorGroupMemberMapped()
        member.Group = groupId
        member.BlogCollaborator = collaboratorId
        
        self.session().add(member)
        self.session().flush((member,))
        
        return True
            
    # ----------------------------------------------------------------        
    
    def removeCollaborator(self, groupId, collaboratorId):
        '''
        @see IBlogCollaboratorGroupService.removeCollaborator
        '''
        updateLastAccessOn(self.session(), groupId)
        sql = self.session().query(BlogCollaboratorGroupMemberMapped)
        sql = sql.filter(BlogCollaboratorGroupMemberMapped.Group == groupId)
        sql = sql.filter(BlogCollaboratorGroupMemberMapped.BlogCollaborator == collaboratorId)
        sql.delete()
        
        return True
    
    # ----------------------------------------------------------------

    def cleanExpired(self):
        '''
        @see: ICleanupService.cleanExpired
        '''
        olderThan = self.session().query(current_timestamp()).scalar()

        # Cleaning expirated blog collaborators groups
        sqlIn = self.session().query(BlogCollaboratorGroupMapped.Id)
        sqlIn = sqlIn.filter(BlogCollaboratorGroupMapped.LastAccessOn <= olderThan - self._group_timeout)
        
        sql = self.session().query(BlogCollaboratorGroupMemberMapped)
        sql = sql.filter(BlogCollaboratorGroupMemberMapped.Group.in_(sqlIn))
        sql.delete(synchronize_session='fetch')
        
        sql = self.session().query(BlogCollaboratorGroupMapped)
        sql = sql.filter(BlogCollaboratorGroupMapped.LastAccessOn <= olderThan - self._group_timeout)
        deleted = sql.delete(synchronize_session='fetch')
        
        assert log.debug('Cleaned \'%s\' expired authentication requests', deleted) or True

# ----------------------------------------------------------------    

def updateLastAccessOn(session, groupId):
    sql = session.query(BlogCollaboratorGroupMapped)
    sql = sql.filter(BlogCollaboratorGroupMapped.Id == groupId)

    try: group = sql.one()
    except NoResultFound: raise InputError(_('No collaborator group'), BlogCollaboratorGroupMapped.Id)
    
    group.LastAccessOn = current_timestamp()
    session.add(group) 
    session.flush((group,))
