'''
Created on May 3, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Populates sample data for the services.
'''

from __plugin__.superdesk.db_superdesk import alchemySessionCreator, \
    createTables
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from superdesk.post.meta.type import PostTypeMapped
from ally.container.support import entityFor
from superdesk.post.api.post import IPostService, QPost, Post
from datetime import datetime, timedelta
from ally.container import ioc
from superdesk.user.api.user import IUserService, QUser, User
from __plugin__.superdesk_collaborator.temp_populate import getCollaboratorsIds

# --------------------------------------------------------------------

def createPostType(key):
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try: session.query(PostTypeMapped.id).filter(PostTypeMapped.Key == key).one()[0]
    except NoResultFound:
        typ = PostTypeMapped()
        typ.Key = key
        session.add(typ)

    session.commit()
    session.close()

USERS = {
         'Gabriel': ('Mighty', 'Omnipresent'),
         'God': ('Gabriel', 'Near Gabriel'),
         }

def getUsersIds():
    userService = entityFor(IUserService)
    assert isinstance(userService, IUserService)
    users = {}
    for name in USERS:
        usrs = userService.getAll(q=QUser(name=name))
        if usrs: users[name] = next(iter(usrs)).Id
        else:
            usr = User()
            usr.Name = name
            usr.FirstName = name
            usr.LastName, usr.Address = USERS[name]
            users[name] = userService.insert(usr)
    return users

FROM_TIME = datetime(2012, 1, 1, 10, 13, 20, 22)
D_1 = timedelta(seconds=1)
D_2 = timedelta(seconds=2)
POSTS = {
         FROM_TIME: ('normal', 'Gabriel', None, False, 'Heloo world', FROM_TIME + D_1, None, None),
         FROM_TIME + D_2: ('normal', 'God', 'Mugurel', True, 'Heloo master', FROM_TIME + D_2 + D_1, None, None),
         FROM_TIME + 2 * D_2: ('wrapup', 'God', 'Jey', True, 'Heloo everybody', FROM_TIME + 2 * D_2, None, None),
         }

def getPostsIds():
    postService = entityFor(IPostService)
    assert isinstance(postService, IPostService)
    posts = {}
    for createdOn in POSTS:
        q = QPost()
        q.createdOn.start = q.createdOn.end = createdOn
        psts = postService.getAll(q=q)
        if psts: posts[createdOn] = next(iter(psts)).Id
        if not psts:
            pst = Post()
            pst.CreatedOn = createdOn
            pst.Type, creator, author, pst.IsModified, pst.Content, \
            pst.PublishedOn, pst.UpdatedOn, pst.DeletedOn = POSTS[createdOn]
            pst.Creator = getUsersIds()[creator]
            if author: pst.Author = getCollaboratorsIds()[author]

            createPostType(pst.Type)
            posts[createdOn] = postService.insert(pst)
    return posts

# --------------------------------------------------------------------

@ioc.after(createTables)
def populate():
    getPostsIds()
