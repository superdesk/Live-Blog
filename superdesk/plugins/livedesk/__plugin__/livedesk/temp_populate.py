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
from superdesk.source.api.source import ISourceService, QSource, Source
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from superdesk.source.meta.type import SourceTypeMapped
from superdesk.person.api.person import QPerson
from superdesk.collaborator.api.collaborator import ICollaboratorService, Collaborator
from superdesk.post.meta.type import PostTypeMapped

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


def createSourceType(key):
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    try: session.query(SourceTypeMapped.id).filter(SourceTypeMapped.Key == key).one()[0]
    except NoResultFound:
        typ = SourceTypeMapped()
        typ.Key = key
        typ.IsAvailable = True
        session.add(typ)

    session.commit()
    session.close()

SOURCES = {
           'google': (False, 'www.google.com', 'xml'),
           'facebook': (False, 'www.facebook.com', 'rss'),
           'twitter': (False, 'www.twitter.com', 'xml'),
           'flickr': (False, 'www.flickr.com', 'xml'),
           }


_cache_sources = {}
def getSourcesIds():
    sourcesService = entityFor(ISourceService)
    assert isinstance(sourcesService, ISourceService)
    if not _cache_sources:
        sources = _cache_sources
        for name in SOURCES:
            srcs = sourcesService.getAll(q=QSource(name=name))
            if srcs: sources[name] = next(iter(srcs)).Id
            if not srcs:
                src = Source()
                src.Name = name
                src.IsModifiable, src.URI, src.Type = SOURCES[name]
                createSourceType(src.Type)
                sources[name] = sourcesService.insert(src)
    return _cache_sources


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
         'Adam': ('Adam', None, 'adam.thomas@sourcefabric.org'),
         'Antoine': ('Antoine', None, 'alaurent@globaleditorsnetwork.org'),
         'Bertrand': ('Bertrand', None, 'bpecquerie@globaleditorsnetwork.org'),
		 'Billy': ('Mihai', 'Balaceanu', 'mihai.balaceanu@sourcefabric.org'),
         'David': ('David', None, 'david.bauer@tageswoche.ch'),
         'Doug': ('Doug', None, 'douglas.arellanes@sourcefabric.org'),
         'Gabriel': ('Gabriel', None, 'gabriel.nistor@sourcefabric.org'),
         'Gideon': ('Gideon', None, 'gideon.lehmann@sourcefabric.org'),
         'Guest': ('Guest', None, ''),
         'Mihail': ('Mihail', 'Nistor', 'mihai.nistor@sourcefabric.org'),
         'Mugur': ('Mugur', None, 'mugur.rus@sourcefabric.org'),
         'Sava': ('Sava', None, 'sava.tatic@sourcefabric.org'),
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
                usr.FirstName, usr.LastName, usr.EMail = USERS[name]
                users[name] = userService.insert(usr)
    return _cache_users


COLLABORATORS = {
                 'Adam': 'facebook',
                 'Antoine': 'facebook',
                 'Bertrand': 'facebook',
                 'David': 'facebook',
                 'Doug': 'facebook',
                 'Gabriel': 'twitter',
                 'Gideon': 'facebook',
                 'Guest': 'facebook',
                 'Mihail': 'facebook',
                 'Mugur': 'twitter',
                 'Sava': 'facebook',
                 'Billy': 'twitter',

                 'google': 'google',
                 'twitter': 'twitter',
                 'flickr': 'flickr',
                 }

_cache_collaborators = {}
def getCollaboratorsIds():
    collaboratorService = entityFor(ICollaboratorService)
    assert isinstance(collaboratorService, ICollaboratorService)
    if not _cache_collaborators:
        collaborators = _cache_collaborators
        for name in COLLABORATORS:
            colls = collaboratorService.getAll(qp=QPerson(firstName=name))
            if colls: collaborators[name] = colls[0].Id
            else:
                coll = Collaborator()
                try: coll.Person = getUsersIds()[name]
                except KeyError: pass
                coll.Source = getSourcesIds()[COLLABORATORS[name]]
                collaborators[name] = collaboratorService.insert(coll)
    return _cache_collaborators


BLOG_COLLABORATORS = {
                       'Antoine': 'Demo live blog',
                       'Bertrand': 'Demo live blog',
                       'Doug': 'Demo live blog',
                       'Guest': 'Demo live blog',
                       'Mugur': 'Demo live blog',
                       'Sava': 'Demo live blog',
					   'Mihail': 'Demo live blog',
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
               'Adam': 'Demo live blog',
               'Antoine': 'Demo live blog',
               'Bertrand': 'Demo live blog',
               'David': 'Demo live blog',
               'Doug': 'Demo live blog',
               'Gabriel': 'Demo live blog',
               'Gideon': 'Demo live blog',
               'Guest': 'Demo live blog',
               'Mihail': 'Demo live blog',
               'Mugur': 'Demo live blog',
               'Sava': 'Demo live blog',
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


POSTS = [
		 ('Demo live blog', 'normal', 'Mihail', 'Mihail', '<b>START</b> your sourcefabrics!!!'),
         ('Demo live blog', 'normal', 'Sava', 'Sava', 'We want a new live blogging tool!'),
         ('Demo live blog', 'normal', 'Mugur', 'Mugur', 'It cannot be done!'),
         ('Demo live blog', 'normal', 'Doug', 'Doug', 'I heard they have a beta version...'),
         ('Demo live blog', 'normal', 'Guest', 'Guest', 'Lets see it!'),
         ('Demo live blog', 'normal', 'Sava', 'Sava', 'Cool, lets test this tool!'),
         ('Demo live blog', 'normal', 'Mugur', 'Mugur', 'It has bugs...'),
         ('Demo live blog', 'normal', 'Doug', 'Doug', 'Can you fix the bugs?'),
         ('Demo live blog', 'normal', 'Mugur', 'Mugur', 'We need at least two months to fix the bugs.'),
         ('Demo live blog', 'normal', 'Sava', 'Sava', 'I want to see it anyway. Let\'s go!'),
         ('Demo live blog', 'wrapup', 'Sava', 'google', 'Livedesk is the next generation live blogging tool.'),
         ('Demo live blog', 'quote', 'Mihail', 'Mihail', 'Fear leads to anger, anger leads to hate, hate leads to suffering.'),
         ]

def createBlogPosts():
    blogPostService = entityFor(IBlogPostService)
    assert isinstance(blogPostService, IBlogPostService)
    for _blogName, blogId in _cache_blogs.items():
        if blogPostService.getPublishedCount(blogId) > 0: return
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
    getSourcesIds()
    createPostType('normal')
    createPostType('wrapup')
    createPostType('quote')
    getBlogsIds()
    createBlogCollaborators()
    createBlogAdmins()
    createBlogPosts()
