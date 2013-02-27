
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
from superdesk.article.meta.article import ArticleMapped
from superdesk.person.api.person import QPerson
from superdesk.collaborator.api.collaborator import ICollaboratorService, Collaborator
import hashlib
from livedesk.api.blog_type import IBlogTypeService, BlogType, QBlogType
from livedesk.api.blog_type_post import IBlogTypePostService
from ally.api.extension import IterPart
from sqlalchemy.sql.functions import current_timestamp
from superdesk.article.meta.article_ctx import ArticleCtxMapped
from superdesk.article.impl.article import ArticleServiceAlchemy
from superdesk.article.api.article import IArticleService
from superdesk.article.api.article_ctx import IArticleCtxService
from superdesk.article.impl.article_ctx import ArticleCtxServiceAlchemy
from ally.exception import InputError


DATA = { 'article': 'Ganz besonders, diese Elsässer',
         'article_content': '<article>            <div class="article-head">\
<p class="article-section">DAS ELSASS</p>\
<p class="article-date">4. Mai 2012</p>\
</div>\
<div class="article-title">\
<h1 contenteditable="true" class="editable">Ganz besonders, diese Elsässer</h1>\
<h3 contenteditable="true" class="editable">Das Elass aus unseren Träumen gibt es nicht mehr. Ein Blick auf eine entschlummernde Region.</h3>\
<h4>Von Alain Claude Sulzer (Text) und Mark Niedermann (Fotos)</h4>\
</div>\
<div class="article-images">\
  <figure>\
<div>\
  <a href="#" class="zoom">Zoom</a>\
<img alt="" src="pictures/article-pic-tablet.jpg">\
</div>\
<p>Besorgte «Glaibasler» stören die Tattoo-Harmonie. Foto: Keystone</p>\
<figurecaption>Elsässer Kontraste: Farbige Hausfassaden und schnelle Vehikel in verschlafenen Dörfern.</figurecaption>\
  </figure>\
  <ul>\
  <li><a href="#"><img src="pictures/article-small-1.jpg" alt=""></a></li>\
  <li><a href="#"><img src="pictures/article-small-2.jpg" alt=""></a></li>\
  <li><a href="#"><img src="pictures/article-small-3.jpg" alt=""></a></li>\
  <li><a href="#"><img src="pictures/article-small-4.jpg" alt=""></a></li>\
  </ul>\
</div>\
  <div class="article-text">\
<p contenteditable="true" class="editable">Freunde aus Zürich, Bern oder einem anderen Gebiet jenseits des Juras kann man immer wieder verblüffen, indem man sich mit ihnen ins 10er-Tramm setzt. Richtung Rodersdorf. Man steigt in Leymen aus und sagt beiläufig, das sei Frankreich &ndash; sofern dies die Freunde nicht schon selbst erkannt haben. Das Erstaunen ist jeweils gross: mit dem Tram ins Ausland! Naja, bitte sehr &ndash; wir sind hier in der Region Basel, wir denken über die Grenzen hinaus, unser Flughafen liegt ja auch im Ausland, man ist weltoffen.<br>\
Denkste! Auf den Flughafen bei Blotzheim fährt man hinter hohen Grenzzäunen, und wo sich die mehr oder weniger grüne Grenze vom Bachgraben in Basel bis nach Rodersdorf erstreckt, wachsen virtuelle Mauern. Irgendwie wird uns das Gebiet hinter der Grenze &ndash; der Sundgau und das ganze Elsass &ndash; immer fremder, unbekannter als auch schon.<br>\
Dem hin und wieder Durchreisenden, Durchwandernden und Durchradelnden gefällt die Landschaft, und er kehrt gern in den immer seltener werdenden Restaurants ein. Aber irgendwie scheint das Leben in den Elsässer Dörfern zu erstarren, Beizen verschwinden, Läden sowieso, Leute sieht man kaum auf den Dorfstrassen und Gassen. Und auch in der Schweiz begegnet man Elsässern seltener. Je stärker die deutsche </p>\
<p contenteditable="true" class="editable">Als wir Mitte der 70er-Jahre ein Haus im Elsass (richtiger: im Sundgau) bezogen, war der Krieg, der mehr als zwei Jahrzehnte zurücklag, noch gegenwärtig. Jene Einheimischen, die über 40 waren, hatten Erfahrungen damit gemacht, die den Menschen jenseits der Grenze, hinter der ich geboren war, erspart geblieben waren: als Evakuierte im unbesetzten Frankreich; als Zwangsarbeiter, die in den Osten umgesiedelt worden waren; als Soldaten in Russland oder als Eltern oder Geschwister von Söhnen und Brüdern, die nicht von dort zurückgekehrt waren; von den Juden, die deportiert worden waren, gar nicht zu reden (über die redete man auch nicht).</p>\
<h3 contenteditable="true" class="editable">Die liebenswürdige Rückständigkeit</h3>\
<p contenteditable="true" class="editable">Als wir Mitte der 70er-Jahre ein Haus im Elsass (richtiger: im Sundgau) bezogen, war der Krieg, der mehr als zwei Jahrzehnte zurücklag, noch gegenwärtig. Jene Einheimischen, die über 40 waren, hatten Erfahrungen damit gemacht, die den Menschen jenseits der Grenze, hinter der ich geboren war, erspart geblieben waren: als Evakuierte im unbesetzten Frankreich; als Zwangsarbeiter, die in den Osten umgesiedelt worden waren; als Soldaten in Russland oder als Eltern oder Geschwister von Söhnen und Brüdern, die nicht von dort zurückgekehrt waren; von den Juden, die deportiert worden waren, gar nicht zu reden (über die redete man auch nicht).</p>\
  </div>\
</article>'
}

def createArticles():

    artService = entityFor(IArticleService)
    slug = 'article-demo'
    #assert isinstance(artService, ArticleServiceAlchemy)
    
    try:
        artService.getBySlug(slug)
        return 
    #    session.query(ArticleMapped.Id).filter(ArticleMapped.Id == '1').one()[0]
    except (NoResultFound, InputError):
        theArticle = ArticleMapped()
        theArticle.CreatedOn = current_timestamp()
        theArticle.Slug = slug
        artService.insert(theArticle)
    
    artCtxService = entityFor(IArticleCtxService)

    assert isinstance(artCtxService, ArticleCtxServiceAlchemy)
    
    for typ in [1,2,3,4]:
        ctx = ArticleCtxMapped()
        ctx.Type = typ
        ctx.Content = DATA['article_content']
        ctx.Article = theArticle.Id
        artCtxService.insert(ctx)
        

    

@ioc.after(createTables)
def populate():
    createArticles()
