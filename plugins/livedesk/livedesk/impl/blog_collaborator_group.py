'''
Created on Feb 11, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for blog collaborator group API.
'''

from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.session import SessionSupport
from livedesk.meta.blog_collaborator import BlogCollaboratorMapped
from sqlalchemy.orm.exc import NoResultFound
from livedesk.api.blog_collaborator_group import IBlogCollaboratorGroupService
from livedesk.meta.blog_collaborator_group import BlogCollaboratorGroupMapped,\
    BlogCollaboratorGroupMemberMapped
from sqlalchemy.sql.functions import current_timestamp
from ally.support.sqlalchemy.mapper import InsertFromSelect, tableFor
from sqlalchemy.sql.expression import select

# --------------------------------------------------------------------

@injected
@setup(IBlogCollaboratorGroupService, name='blogCollaboratorGroupService')
class BlogCollaboratorGroupService(SessionSupport, IBlogCollaboratorGroupService):
    '''
    Implementation for @see: IBlogCollaboratorGroupService
    '''

    def getById(self, groupId):
        '''
        @see IBlogCollaboratorGroupService.getById
        '''
        sql = self.session().query(BlogCollaboratorGroupMapped)
        sql = sql.filter(BlogCollaboratorGroupMapped.Id == groupId)

        try: 
            group = sql.one()
            return group
        except NoResultFound: raise InputError(Ref(_('No collaborator group'), ref=BlogCollaboratorGroupMapped.Id))
        
    def getAllMembers(self, groupId):
        '''
        @see IBlogCollaboratorGroupService.getAllMembers
        '''
        
        sql = self.session().query(BlogCollaboratorGroupMemberMapped).filter(BlogCollaboratorGroupMemberMapped.Group == groupId)
        
        return sql.all()

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

    def delete(self, groupId):
        '''
        @see IBlogCollaboratorGroupService.delete
        '''
        
        self.session().query(BlogCollaboratorGroupMemberMapped).delete(groupId)
        self.session().query(BlogCollaboratorGroupMapped).filter(BlogCollaboratorGroupMapped.Id == groupId).delete()
        
        return True

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
        self.session().flush((member, ))
        
        return True
            
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
    

def updateLastAccessOn(session, groupId):
    sql = session.query(BlogCollaboratorGroupMapped)
    sql = sql.filter(BlogCollaboratorGroupMapped.Id == groupId)

    try: group = sql.one()
    except NoResultFound: raise InputError(Ref(_('No collaborator group'), ref=BlogCollaboratorGroupMapped.Id))
    
    group.LastAccessOn = current_timestamp()
    session.add(group) 
    session.flush((group, ))