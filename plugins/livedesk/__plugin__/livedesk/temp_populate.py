'''
Created on May 3, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Populates sample data for the services.
'''

from ..superdesk.db_superdesk import alchemySessionCreator
from ally.api.extension import IterPart
from ally.container.support import entityFor
from datetime import datetime
from distribution.container import app
from livedesk.api.blog import IBlogService, QBlog, Blog
from livedesk.api.blog_admin import IBlogAdminService
from livedesk.api.blog_collaborator import IBlogCollaboratorService
from livedesk.api.blog_post import IBlogPostService
from livedesk.api.blog_type import IBlogTypeService, BlogType, QBlogType
from livedesk.api.blog_type_post import IBlogTypePostService, \
    BlogTypePostPersist
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from superdesk.collaborator.api.collaborator import ICollaboratorService, \
    Collaborator
from superdesk.language.api.language import ILanguageService, LanguageEntity
from superdesk.post.api.post import Post
from superdesk.post.meta.type import PostTypeMapped
from superdesk.source.api.source import ISourceService, QSource, Source
from superdesk.source.meta.type import SourceTypeMapped
from superdesk.user.api.user import IUserService, QUser, User
import hashlib

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
           'youtube': (False, 'www.youtube.com', 'xml'),
           'instagram': (False, 'www.instagram.com', 'xml'),
           'soundcloud': (False, 'www.soundcloud.com', 'xml'),
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


BLOG_TYPE_POSTS = [
                   ('default', 'normal', 'User1', 'User1', 'Hello', 'Hello world!'),
                   ('default', 'normal', 'User1', 'User1', 'Conclusion', 'To summarise, this is the conclusion...', )
                   ]

def createBlogTypePosts():
    blogTypePostService = entityFor(IBlogTypePostService)
    assert isinstance(blogTypePostService, IBlogTypePostService)
    for data in BLOG_TYPE_POSTS:
        pst = BlogTypePostPersist()
        blogType, pst.Type, creator, author, pst.Name, pst.Content = data
        blogTypeId = getBlogTypesIds()[blogType]
        exists = False
        for post in blogTypePostService.getAll(blogTypeId):
            if post.Content == pst.Content: exists = True; break
        if not exists:
            pst.Creator = getUsersIds()[creator]
            if author: pst.Author = getCollaboratorsIds()[author]
            blogTypePostService.insert(blogTypeId, pst)


BLOG_TYPES = ('default',)

_cache_blog_types = {}
def getBlogTypesIds():
    blogTypeService = entityFor(IBlogTypeService)
    assert isinstance(blogTypeService, IBlogTypeService)
    if not _cache_blog_types:
        blogTypePosts = _cache_blog_types
        for name in BLOG_TYPES:
            blgTypes = blogTypeService.getAll(q=QBlogType(name=name))
            if blgTypes: blogTypePosts[name] = next(iter(blgTypes)).Id
            else:
                blgType = BlogType()
                blgType.Name = name
                blogTypePosts[name] = blogTypeService.insert(blgType)
    return _cache_blog_types


BLOGS = {
         'GEN Live Desk Master Class': ('default', 'User1', 'en', 'An in-depth demonstration'
                                        ' of the current state of development of the GEN'
                                        ' Live Desk tool for live online news coverage.',
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
                blogType, usrName, langCode, blg.Description, blg.CreatedOn, blg.LiveOn = BLOGS[name]
                blg.Type = getBlogTypesIds()[blogType]
                blg.Creator = getUsersIds()[usrName]
                blg.Language = getLanguagesIds()[langCode]
                blogs[name] = blogService.insert(blg)
    return _cache_blogs


USERS = {
         'User1': ('User1', None, ''),
         'User2': ('User2', None, ''),
         'User3': ('User3', None, ''),
         'User4': ('User4', None, ''),
         'User5': ('User5', None, ''),
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
                usr.Password = hashlib.sha512(b'a').hexdigest()
                usr.FirstName, usr.LastName, usr.EMail = USERS[name]
                users[name] = userService.insert(user=usr)
    return _cache_users


COLLABORATORS = {
                 'User1': 'internal',
                 'User2': 'internal',
                 'User3': 'internal',
                 'User4': 'internal',
                 'User5': 'internal',

                 'advertisement': 'advertisement',
                 'internal': 'internal',
                 'google': 'google',
                 'twitter': 'twitter',
                 'flickr': 'flickr',
                 'youtube': 'youtube',
                 'instagram': 'instagram',
                 'soundcloud': 'soundcloud'
                 }

_cache_collaborators = {}
def getCollaboratorsIds():
    collaboratorService = entityFor(ICollaboratorService)
    assert isinstance(collaboratorService, ICollaboratorService)
    if not _cache_collaborators:
        collaborators = _cache_collaborators
        for uname, source in COLLABORATORS.items():
            try: user = getUsersIds()[uname]
            except KeyError:
                user = None
                colls, index = collaboratorService.getAll(qs=QSource(name=source)), source
            else:
                colls, index = collaboratorService.getAll(qu=QUser(name=USERS[uname][0])), uname
            if colls: collaborators[index] = colls[0].Id
            else:
                coll = Collaborator()
                coll.User = user
                coll.Source = getSourcesIds()[source]
                collaborators[index] = collaboratorService.insert(coll)
    return _cache_collaborators


BLOG_COLLABORATORS = {
                      'User1': 'GEN Live Desk Master Class',
                      'User2': 'GEN Live Desk Master Class',
                      'User3': 'GEN Live Desk Master Class',
                      'User4': 'GEN Live Desk Master Class',
                      'User5': 'GEN Live Desk Master Class',
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
               'User1': 'GEN Live Desk Master Class',
               'User2': 'GEN Live Desk Master Class',
               'User3': 'GEN Live Desk Master Class',
               'User4': 'GEN Live Desk Master Class',
               'User5': 'GEN Live Desk Master Class',
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
		 ('GEN Live Desk Master Class', 'normal', 'User1', 'User1', 'Hello world!'),
         ('GEN Live Desk Master Class', 'quote', 'User2', 'User2', 'GEN Live Desk is a next-generation '
          'open source web tool for both individuals and teams to report live breaking news from anywhere.'),
         ('GEN Live Desk Master Class', 'normal', 'User3', 'User3', 'GEN Live Desk is free to download, '
          'easily implemented into your website and alongside existing newsroom tools. It enhances rather '
          'than replaces. Helps convince an IT department!'),
         ('GEN Live Desk Master Class', 'normal', 'User1', 'User1', 'With GEN Live Desk, you can '
          'drive traffic with engaging content and (if relevant) use sponsorship, contextual adverts or '
          'paid subscriptions to increase revenue.'),
         ('GEN Live Desk Master Class', 'wrapup', 'User2', 'User2', 'That is all for today folks. Join us '
          'at GEN News World Media Summit to see Douglas Arellanes demoing the tool live.'),
         ('GEN Live Desk Master Class', 'advertisement', 'User4', 'advertisement', '<a href="http://genlivedesk.org" target="_blank">GEN Live Desk is a new open source '
          'live-blogging tool for newsrooms and journalists. Sign up now to receive a private invite and '
          'be one of the first to test it!</a>')
         ]

def createBlogPosts():
    blogPostService = entityFor(IBlogPostService)
    assert isinstance(blogPostService, IBlogPostService)
    for _blogName, blogId in _cache_blogs.items():
        published = blogPostService.getPublished(blogId, detailed=True, limit=0)
        assert isinstance(published, IterPart), 'Invalid part %s' % published
        if published.total > 0: return
    for data in POSTS:
        pst = Post()
        blog, pst.Type, creator, author, pst.Content = data
        pst.Creator = getUsersIds()[creator]
        if author: pst.Author = getCollaboratorsIds()[author]

        createPostType(pst.Type)
        if pst.Type == 'advertisement':
            blogPostService.insert(getBlogsIds()[blog], pst)
            pst.Id = None
        blogPostService.insertAndPublish(getBlogsIds()[blog], pst)

# --------------------------------------------------------------------

@app.populate
def populate():
    getSourcesIds()
    createPostType('normal')
    createPostType('wrapup')
    createPostType('link')
    createPostType('image')
    createPostType('quote')
    createPostType('advertisement')
    getBlogsIds()
    createBlogCollaborators()
    createBlogAdmins()
    createBlogPosts()
    createBlogTypePosts()
