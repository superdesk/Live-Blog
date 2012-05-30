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
           'internal': (False, '', ''),
           'advertisement': (False, '', ''),
           'google': (False, 'www.google.com', 'xml'),
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
         'GEN Live Desk Master Class': ('Doug', 'en', 'An in-depth demonstration of the '
                                        'current state of development of the GEN Live Desk '
                                        'tool for live online news coverage.',
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
         'Adam': ('Adam', 'Thomas', 'adam.thomas@sourcefabric.org'),
         'Antoine': ('Antoine', 'Laurent', 'alaurent@globaleditorsnetwork.org'),
         'Bertrand': ('Bertrand', 'Pecquerie', 'bpecquerie@globaleditorsnetwork.org'),
		 'Billy': ('Mihai', 'Balaceanu', 'mihai.balaceanu@sourcefabric.org'),
         'David': ('David', 'Bauer', 'david.bauer@tageswoche.ch'),
         'Doug': ('Douglas', 'Arellanes', 'douglas.arellanes@sourcefabric.org'),
         'Gabriel': ('Gabriel', 'Nistor', 'gabriel.nistor@sourcefabric.org'),
         'Gideon': ('Gideon', 'Lehmann', 'gideon.lehmann@sourcefabric.org'),
         'Guest': ('Guest', None, ''),
         'John': ('John', 'Burke', 'jburke@globaleditorsnetwork.org'),
         'Mihail': ('Mihail', 'Nistor', 'mihai.nistor@sourcefabric.org'),
         'Mugur': ('Mugur', 'Rus', 'mugur.rus@sourcefabric.org'),
         'Sava': ('Sava', 'Tatic', 'sava.tatic@sourcefabric.org'),
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
                 'Adam': 'internal',
                 'Antoine': 'internal',
                 'Bertrand': 'internal',
                 'Billy': 'internal',
                 'David': 'internal',
                 'Doug': 'internal',
                 'Gabriel': 'internal',
                 'Gideon': 'internal',
                 'Guest': 'internal',
                 'John': 'internal',
                 'Mihail': 'internal',
                 'Mugur': 'internal',
                 'Sava': 'internal',

                 'advertisement': 'advertisement',
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
        for uname, source in COLLABORATORS.items():
            try: person = getUsersIds()[uname]
            except KeyError:
                person = None
                colls, index = collaboratorService.getAll(qs=QSource(name=source)), source
            else:
                colls, index = collaboratorService.getAll(qp=QPerson(firstName=USERS[uname][0])), uname
            if colls: collaborators[index] = colls[0].Id
            else:
                coll = Collaborator()
                coll.Person = person
                coll.Source = getSourcesIds()[source]
                collaborators[index] = collaboratorService.insert(coll)
    return _cache_collaborators


BLOG_COLLABORATORS = {
                      'Adam': 'GEN Live Desk Master Class',
                      'Antoine': 'GEN Live Desk Master Class',
                      'David': 'GEN Live Desk Master Class',
                      'Doug': 'GEN Live Desk Master Class',
                      'John': 'GEN Live Desk Master Class',
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
               'Adam': 'GEN Live Desk Master Class',
               'Antoine': 'GEN Live Desk Master Class',
               'Bertrand': 'GEN Live Desk Master Class',
               'Billy': 'GEN Live Desk Master Class',
               'David': 'GEN Live Desk Master Class',
               'Doug': 'GEN Live Desk Master Class',
               'Gabriel': 'GEN Live Desk Master Class',
               'Gideon': 'GEN Live Desk Master Class',
               'Guest': 'GEN Live Desk Master Class',
               'John': 'GEN Live Desk Master Class',
               'Mihail': 'GEN Live Desk Master Class',
               'Mugur': 'GEN Live Desk Master Class',
               'Sava': 'GEN Live Desk Master Class',
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
		 ('GEN Live Desk Master Class', 'normal', 'Adam', 'Adam', 'Hello world!'),
         ('GEN Live Desk Master Class', 'quote', 'David', 'David', 'GEN Live Desk is a next-generation '
          'open source web tool for both individuals and teams to report live breaking news from anywhere.'),
         ('GEN Live Desk Master Class', 'normal', 'Doug', 'Doug', 'GEN Live Desk is free to download, '
          'easily implemented into your website and alongside existing newsroom tools. It enhances rather '
          'than replaces. Helps convince an IT department!'),
         ('GEN Live Desk Master Class', 'normal', 'Antoine', 'Antoine', 'With GEN Live Desk, you can '
          'drive traffic with engaging content and (if relevant) use sponsorship, contextual adverts or '
          'paid subscriptions to increase revenue.'),
         ('GEN Live Desk Master Class', 'wrapup', 'Adam', 'Adam', 'That is all for today folks. Join us '
          'at GEN News World Media Summit to see Douglas Arellanes demoing the tool live.'),
         ('GEN Live Desk Master Class', 'advertisement', 'Mugur', 'advertisement', 'GEN Live Desk is a new open source '
          'live-blogging tool for newsrooms and journalists. Sign up now to receive a private invite and '
          'be one of the first to test it! http://genlivedesk.org')
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
        if pst.Type == 'advertisement':
            blogPostService.insert(getBlogsIds()[blog], pst)
        else:
            blogPostService.insertAndPublish(getBlogsIds()[blog], pst)

# --------------------------------------------------------------------

@ioc.after(createTables)
def populate():
    getSourcesIds()
    createPostType('normal')
    createPostType('wrapup')
    createPostType('quote')
    createPostType('advertisement')
    getBlogsIds()
    createBlogCollaborators()
    createBlogAdmins()
    createBlogPosts()
