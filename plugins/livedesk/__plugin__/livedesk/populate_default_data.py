'''
Created on May 3, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Populates sample data for the services.
'''

from ..superdesk.db_superdesk import alchemySessionCreator
from ..livedesk.populate import populateDefaultUsers
from ally.api.extension import IterPart
from ally.container import ioc, app
from ally.container.support import entityFor
from ally.support.util_io import openURI
from datetime import datetime
from livedesk.api.blog import IBlogService, QBlog, Blog
from livedesk.api.blog_collaborator import IBlogCollaboratorService
from livedesk.api.blog_post import IBlogPostService
from livedesk.api.blog_type import IBlogTypeService, BlogType, QBlogType
from livedesk.api.blog_type_post import IBlogTypePostService, \
    BlogTypePostPersist
from os.path import abspath, dirname, join
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from superdesk.collaborator.api.collaborator import ICollaboratorService, \
    Collaborator
from superdesk.language.api.language import ILanguageService, LanguageEntity
from superdesk.post.api.post import Post
from superdesk.post.meta.type import PostTypeMapped
from superdesk.source.api.source import ISourceService, QSource, Source
from superdesk.source.meta.type import SourceTypeMapped
from superdesk.user.api.user import IUserService, QUser
import csv
from superdesk.user.meta.user_type import UserTypeMapped
from livedesk.meta.blog_media import BlogMediaTypeMapped
from sqlalchemy.sql.expression import exists

# --------------------------------------------------------------------

LANGUAGES = { 'en', 'de', 'fr' }

@ioc.entity
def getLanguagesIds():
    languageService = entityFor(ILanguageService)
    assert isinstance(languageService, ILanguageService)
    languages = { lang.Code: lang.Id for lang in languageService.getAll() }
    for code in LANGUAGES:
        if code not in languages:
            lang = LanguageEntity()
            lang.Code = code
            languages[code] = languageService.insert(lang)
    return languages


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


def createUserType(key):
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    if not session.query(exists().where(UserTypeMapped.Key == key)).scalar():
        userTypeDb = UserTypeMapped()
        userTypeDb.Key = key
        session.add(userTypeDb)

    session.commit()
    session.close()


@app.populate
def createSourceTypes():
    createSourceType('blog provider')
    createSourceType('chained blog')
    createSourceType('comment')

@app.populate
def createLiveBlogUserTypes():
    createUserType('commentator')
    createUserType('sms')
    createUserType('chained blog')

def createBlogMediaType(key):
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    if not session.query(exists().where(BlogMediaTypeMapped.Key == key)).scalar():
        blogMediaTypeDb = BlogMediaTypeMapped()
        blogMediaTypeDb.Key = key
        session.add(blogMediaTypeDb)

    session.commit()
    session.close()

@app.populate
def createBlogMediaTypes():
    createBlogMediaType('top_banner')

SOURCES = {
           'internal': (False, '', '', ''),
           'advertisement': (False, '', '', ''),
           'sms': (False, '', '', ''),
           'comments': (False, '', '', ''),
           'google': (False, 'www.google.com', 'xml', ''),
           'facebook': (False, 'www.facebook.com', 'xml', ''),
           'twitter': (False, 'www.twitter.com', 'xml', '{"ConsumerKey":"uLW0hK2KZosj8Yl4F17uKg","ConsumerSecret":"iRuM0j8pyUTYgbpwPLqAl9wTBn5JzQB4zLJaiUaEdyE"}'),
           'flickr': (False, 'www.flickr.com', 'xml', 'abf46ef4c670460e95d09cf368606b8a'),
           'youtube': (False, 'www.youtube.com', 'xml', ''),
           'instagram': (False, 'www.instagram.com', 'xml', 'daa5f588be7c4ce4b5771ec8653bcf44'),
           'soundcloud': (False, 'www.soundcloud.com', 'xml', 'd98e8886a3f474440649a28ecf79b889'),
           }


@ioc.entity
def getSourcesIds():
    sourcesService = entityFor(ISourceService)
    assert isinstance(sourcesService, ISourceService)
    sources = {}
    for name in SOURCES:
        srcs = sourcesService.getAll(q=QSource(name=name))
        if srcs: sources[name] = next(iter(srcs)).Id
        else:
            src = Source()
            src.Name = name
            src.IsModifiable, src.URI, src.Type, src.Key = SOURCES[name]
            createSourceType(src.Type)
            sources[name] = sourcesService.insert(src)
    return sources


BLOG_TYPES = ('default',)

@ioc.entity
def getBlogTypesIds():
    blogTypeService = entityFor(IBlogTypeService)
    assert isinstance(blogTypeService, IBlogTypeService)
    blogTypes = {}
    for name in BLOG_TYPES:
        blgTypes = blogTypeService.getAll(q=QBlogType(name=name))
        if blgTypes: blogTypes[name] = next(iter(blgTypes)).Id
        else:
            blgType = BlogType()
            blgType.Name = name
            blogTypes[name] = blogTypeService.insert(blgType)
    return blogTypes


@ioc.entity
def getUsersIds():
    userService = entityFor(IUserService)
    assert isinstance(userService, IUserService)
    return { user.Name:user.Id for user in userService.getAll() }


COLLABORATORS = {
                 'advertisement': 'advertisement',
                 'internal': 'internal',
                 'sms': 'sms',
                 'comments': 'comments',
                 'google': 'google',
                 'facebook': 'facebook',
                 'twitter': 'twitter',
                 'flickr': 'flickr',
                 'youtube': 'youtube',
                 'instagram': 'instagram',
                 'soundcloud': 'soundcloud'
                 }

@ioc.entity
def getCollaboratorsIds():
    collaboratorService = entityFor(ICollaboratorService)
    assert isinstance(collaboratorService, ICollaboratorService)
    collaborators = {}
    for source, id in getSourcesIds().items():
        colls = collaboratorService.getAll(qs=QSource(name=source))
        if colls: collaborators[source] = colls[0].Id
        else:
            coll = Collaborator()
            coll.User = None
            coll.Source = getSourcesIds()[source]
            collaborators[source] = collaboratorService.insert(coll)

    for user, id in getUsersIds().items():
        colls = collaboratorService.getAll(qu=QUser(name=user))
        if colls: collaborators[user] = colls[0].Id
        else:
            coll = Collaborator()
            coll.User = id
            coll.Source = getSourcesIds()['internal']
            collaborators[user] = collaboratorService.insert(coll)
    return collaborators


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


@app.populate
def createPostTypes():
    createPostType('normal')
    createPostType('wrapup')
    createPostType('link')
    createPostType('image')
    createPostType('quote')
    createPostType('advertisement')


BLOG_TYPE_POSTS = [
                   ('default', 'normal', 'admin', 'admin', 'Hello', 'Hello world!'),
                   ('default', 'normal', 'admin', 'admin', 'Conclusion', 'To summarize, this is the conclusion...',)
                   ]

@ioc.after(populateDefaultUsers, createPostTypes)
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


BLOGS_DEFAULTS = ('default', 'en')

def defaultBlogs():
    '''
    Reads blogs data from blogs.csv (CSV) file
    '''
    blogs = {}
    blogsFile = join(dirname(abspath(__file__)), 'blogs.csv')
    with openURI(blogsFile, byteMode=False) as csvfile:
        blogsRead = csv.reader(csvfile, delimiter=',', quotechar='"')
        for blog in blogsRead:
            data = (BLOGS_DEFAULTS[0], blog[1], BLOGS_DEFAULTS[1], blog[2], datetime.now(), datetime.now())
            blogs[blog[0]] = data
    return blogs

@ioc.entity
def getBlogsIds():
    blogService = entityFor(IBlogService)
    assert isinstance(blogService, IBlogService)
    blogs = {}
    for name, data in defaultBlogs().items():
        blgs = blogService.getAll(q=QBlog(title=name))
        if blgs: blogs[name] = next(iter(blgs)).Id
        else:
            blg = Blog()
            blg.Title = name
            blogType, usrName, langCode, blg.Description, blg.CreatedOn, blg.LiveOn = data
            blg.Type = getBlogTypesIds()[blogType]
            blg.Creator = getUsersIds()[usrName]
            blg.Language = getLanguagesIds()[langCode]
            blogs[name] = blogService.insert(blg)
    return blogs


BLOG_COLLABORATORS = {
                      'reporter': 'Election Night 2013',
                      'journalist': 'Election Night 2013',
                     }

@ioc.after(createBlogTypePosts)
def createBlogCollaborators():
    blogCollaboratorService = entityFor(IBlogCollaboratorService)
    assert isinstance(blogCollaboratorService, IBlogCollaboratorService)
    for name, blog in BLOG_COLLABORATORS.items():
        blogId, collId = getBlogsIds()[blog], getCollaboratorsIds()[name]
        blgs = blogCollaboratorService.getAll(blogId)
        for blg in blgs:
            if blg.Id == collId: break
        else:
            blogCollaboratorService.addCollaboratorAsDefault(blogId, collId)


BLOG_ADMINS = {
               'admin': 'Election Night 2013',
               'editor': 'Election Night 2013',
               }

@ioc.after(createBlogTypePosts)
def createBlogAdmins():
    blogCollaboratorService = entityFor(IBlogCollaboratorService)
    assert isinstance(blogCollaboratorService, IBlogCollaboratorService)
    for name, blog in BLOG_ADMINS.items():
        blogId, collId = getBlogsIds()[blog], getCollaboratorsIds()[name]
        blgs = blogCollaboratorService.getAll(blogId)
        for blg in blgs:
            if blg.Id == collId: break
        else:
            blogCollaboratorService.addCollaborator(blogId, collId, 'Administrator')


def defaultPosts():
    '''
    Reads posts data from posts.csv (CSV) file
    '''
    posts = []
    postsFile = join(dirname(abspath(__file__)), 'posts.csv')
    with openURI(postsFile, byteMode=False) as csvfile:
        postsRead = csv.reader(csvfile, delimiter=',', quotechar='"')
        for post in postsRead:
            posts.append(post)
    return posts

@ioc.after(createBlogAdmins, createBlogCollaborators)
def createBlogPosts():
    blogPostService = entityFor(IBlogPostService)
    assert isinstance(blogPostService, IBlogPostService)
    for _blogName, blogId in getBlogsIds().items():
        published = blogPostService.getPublished(blogId, detailed=True, limit=0)
        assert isinstance(published, IterPart), 'Invalid part %s' % published
        if published.total > 0: return
    for data in defaultPosts():
        pst = Post()
        blog, pst.Type, creator, author, pst.Content = data
        pst.Creator = getUsersIds()[creator]
        if author: pst.Author = getCollaboratorsIds()[author]

        createPostType(pst.Type)
        if pst.Type == 'advertisement':
            blogPostService.insert(getBlogsIds()[blog], pst)
            pst.Id = None
            pst.Uuid = None
        blogPostService.insertAndPublish(getBlogsIds()[blog], pst)
