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
from __plugin__.superdesk_post.temp_populate import getUsersIds, createPostType
from ally.container import ioc
from ally.container.support import entityFor
from datetime import datetime, timedelta
from livedesk.api.blog import IBlogService, QBlog, Blog
from livedesk.api.blog_collaborator import IBlogCollaboratorService
from superdesk.language.api.language import ILanguageService, LanguageEntity
from livedesk.api.blog_admin import IBlogAdminService
from livedesk.api.blog_post import IBlogPostService, BlogPost
from superdesk.post.api.post import QPost

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
         'Active Blog about Starcraft II': ('Gabriel', 'en', 'Lets talk about <b>Stracraft</b>',
                                            datetime(2012, 1, 1, 10, 2, 20, 22), datetime(2012, 1, 1, 10, 3, 1, 22)),
         'InActive Blog about Me': ('God', 'ro', 'Lets talk about <b>Gabriel</b>',
                                            datetime(2012, 1, 1, 10, 1, 20, 22), None),
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

BLOG_COLLABORATORS = {
                      'Billy': 'Active Blog about Starcraft II',
                      'Jey': 'Active Blog about Starcraft II',
                      'Mugurel': 'InActive Blog about Me',
                      }

def createBlogCollaborators():
    blogCollaboratorService = entityFor(IBlogCollaboratorService)
    assert isinstance(blogCollaboratorService, IBlogCollaboratorService)
    for name, blog in BLOG_COLLABORATORS.items():
        blogId, collId = getBlogsIds()[blog], getCollaboratorsIds()[name]
        blgs = blogCollaboratorService.getAll(blogId, collId)
        if not blgs:
            blogCollaboratorService.addCollaborator(blogId, collId)

BLOG_ADMINS = {
               'God': 'Active Blog about Starcraft II',
               'Gabriel': 'InActive Blog about Me',
               }

def createBlogAdmins():
    blogAdminService = entityFor(IBlogAdminService)
    assert isinstance(blogAdminService, IBlogAdminService)
    for name, blog in BLOG_ADMINS.items():
        blogId, userId = getBlogsIds()[blog], getUsersIds()[name]
        blgs = blogAdminService.getAll(blogId, userId)
        if not blgs:
            blogAdminService.addAdmin(blogId, userId)

FROM_TIME = datetime(2012, 1, 2, 10, 13, 20, 22)
D_1 = timedelta(seconds=1)
D_2 = timedelta(seconds=2)
D_3 = timedelta(seconds=10)
POSTS = {}

POSTS[(FROM_TIME, 'Active Blog about Starcraft II')] = \
('normal', 'Gabriel', None, False, 'Wsup from livedesk', FROM_TIME + D_1, FROM_TIME + D_3, None)
FROM_TIME += D_2
POSTS[(FROM_TIME, 'Active Blog about Starcraft II')] = \
('normal', 'God', None, False, 'Wsuppppp', FROM_TIME + D_1, None, None)
FROM_TIME += D_2
POSTS[(FROM_TIME, 'Active Blog about Starcraft II')] = \
('normal', 'God', 'Billy', True, 'I don\'t know starcraft', FROM_TIME + D_1, FROM_TIME + D_3, None)
FROM_TIME += D_2
POSTS[(FROM_TIME, 'Active Blog about Starcraft II')] = \
('wrapup', 'Gabriel', None, False, 'Billy goes out', FROM_TIME + D_1, None, None)
FROM_TIME += D_2
POSTS[(FROM_TIME, 'Active Blog about Starcraft II')] = \
('normal', 'Gabriel', 'google', False, 'Lets try again', FROM_TIME + D_1, None, None)


def createBlogPosts():
    blogPostService = entityFor(IBlogPostService)
    assert isinstance(blogPostService, IBlogPostService)
    for createdOn, blog in POSTS:
        blogId = getBlogsIds()[blog]

        q = QPost()
        q.createdOn.start = q.createdOn.end = createdOn
        psts = blogPostService.getPublished(blogId, q=q)
        try: next(iter(psts))
        except StopIteration:
            pst = BlogPost()
            pst.Blog = blogId
            pst.CreatedOn = createdOn
            pst.Type, creator, author, pst.IsModified, pst.Content, \
            pst.PublishedOn, pst.UpdatedOn, pst.DeletedOn = POSTS[(createdOn, blog)]
            pst.Creator = getUsersIds()[creator]
            if author: pst.Author = getCollaboratorsIds()[author]

            createPostType(pst.Type)
            blogPostService.insert(pst)

# --------------------------------------------------------------------

@ioc.after(createTables)
def populate():
    getBlogsIds()
    createBlogCollaborators()
    createBlogAdmins()
    createBlogPosts()
