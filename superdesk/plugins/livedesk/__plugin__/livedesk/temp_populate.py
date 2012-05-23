'''
Created on May 3, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Populates sample data for the services.
'''

from __plugin__.superdesk.db_superdesk import createTables
from __plugin__.superdesk_collaborator.temp_populate import getCollaboratorsIds
from __plugin__.superdesk_post.temp_populate import createPostType
from ally.container import ioc
from ally.container.support import entityFor
from datetime import datetime
from livedesk.api.blog import IBlogService, QBlog, Blog
from livedesk.api.blog_collaborator import IBlogCollaboratorService
from superdesk.language.api.language import ILanguageService, LanguageEntity
from livedesk.api.blog_admin import IBlogAdminService
from livedesk.api.blog_post import IBlogPostService
from superdesk.post.api.post import Post
from superdesk.user.api.user import IUserService, QUser, User

# --------------------------------------------------------------------

LANGUAGES = {'ro', 'en'}

_cache_languages = {}
def getLanguagesIds():
    languageService = entityFor(ILanguageService)
    assert isinstance(languageService, ILanguageService)
    if not _cache_languages:
        languages = _cache_languages
        languages.update({lang.Code: lang.Id for lang in languageService.getAll()})
        for code in LANGUAGES:
            if code not in languages:
                lang = LanguageEntity()
                lang.Code = code
                languages[code] = languageService.insert(lang)
    return _cache_languages

BLOGS = {
         'Demo live blog': ('Doug', 'en', 'This is a Demo for the live blogging tool',
                                            datetime.now(), datetime.now()),
         }

_cache_blogs = {}
def getBlogsIds():
    blogService = entityFor(IBlogService)
    assert isinstance(blogService, IBlogService)
    if not _cache_blogs:
        blogs = _cache_blogs
        for name in BLOGS:
            blgs = blogService.getAll(q=QBlog(title=name))
            if blgs: blogs[name] = next(iter(blgs)).Id
            else:
                blg = Blog()
                blg.Title = name
                usrName, langCode, blg.Description, blg.CreatedOn, blg.LiveOn = BLOGS[name]
                blg.Creator = getUsersIds()[usrName]
                blg.Language = getLanguagesIds()[langCode]
                blogs[name] = blogService.insert(blg)
    return _cache_blogs


USERS = {
         'Doug': (None, None),
         'Bertrand': (None, None),
         'David': (None, None),
         'Adam': (None, None),
         'Antoine': (None, None),
         'Gideon': (None, None),
       }

_cache_users = {}
def getUsersIds():
    userService = entityFor(IUserService)
    assert isinstance(userService, IUserService)
    if not _cache_users:
        users = _cache_users
        for name in USERS:
            usrs = userService.getAll(q=QUser(name=name))
            if usrs: users[name] = next(iter(usrs)).Id
            else:
                usr = User()
                usr.Name = name
                usr.FirstName = name
                usr.LastName, usr.Address = USERS[name]
                users[name] = userService.insert(usr)
    return _cache_users


BLOG_COLLABORATORS = {
                      'Mugur': 'Demo live blog',
                      'Sava': 'Demo live blog',
                      }

def createBlogCollaborators():
    blogCollaboratorService = entityFor(IBlogCollaboratorService)
    assert isinstance(blogCollaboratorService, IBlogCollaboratorService)
    for name, blog in BLOG_COLLABORATORS.items():
        blogId, collId = getBlogsIds()[blog], getCollaboratorsIds()[name]
        blgs = blogCollaboratorService.getAll(blogId)
        for blg in blgs:
            if blg.Id == collId: break
        else:
            blogCollaboratorService.addCollaborator(blogId, collId)

BLOG_ADMINS = {
               'Doug': 'Demo live blog',
               'Bertrand': 'Demo live blog',
               'David': 'Demo live blog',
               'Antoine': 'Demo live blog',
               }

def createBlogAdmins():
    blogAdminService = entityFor(IBlogAdminService)
    assert isinstance(blogAdminService, IBlogAdminService)
    for name, blog in BLOG_ADMINS.items():
        blogId, userId = getBlogsIds()[blog], getUsersIds()[name]
        blgs = blogAdminService.getAll(blogId)
        for blg in blgs:
            if blg.Id == userId: break
        else:
            blogAdminService.addAdmin(blogId, userId)

POSTS = [
         ('Demo live blog', 'normal', 'Doug', None, 'Do we have the blogging live tool'),
         ('Demo live blog', 'normal', 'David', 'Mugur', 'It cannot be done'),
         ('Demo live blog', 'normal', 'David', 'Sava', 'They have some beta one as I heard'),
         ('Demo live blog', 'normal', 'Antoine', 'google', 'Lets see it'),
         ('Demo live blog', 'normal', 'Bertrand', 'Sava', 'Cool, lets test this tool'),
         ('Demo live blog', 'normal', 'Antoine', None, 'Lets go'),
         ]

def createBlogPosts():
    blogPostService = entityFor(IBlogPostService)
    assert isinstance(blogPostService, IBlogPostService)
    for data in POSTS:
        pst = Post()
        blog, pst.Type, creator, author, pst.Content = data
        pst.Creator = getUsersIds()[creator]
        if author: pst.Author = getCollaboratorsIds()[author]

        createPostType(pst.Type)
        blogPostService.insertAndPublish(getBlogsIds()[blog], pst)

# --------------------------------------------------------------------

@ioc.after(createTables)
def populate():
    getBlogsIds()
    createBlogCollaborators()
    createBlogAdmins()
    createBlogPosts()
