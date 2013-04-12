'''
Created on Mar 27, 2012

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the sql alchemy mapper.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

from .samples.api.article import IArticleService, Article
from .samples.api.article_type import ArticleType, IArticleTypeService, \
    QArticleType
from .samples.impl.article import ArticleServiceAlchemy
from .samples.impl.article_type import ArticleTypeServiceAlchemy
from .samples.meta import meta
from ally.container.binder_op import bindValidations
from ally.container.impl.proxy import createProxy, ProxyWrapper
from ally.exception import InputError
from ally.support.sqlalchemy.mapper import mappingsOf
from ally.support.sqlalchemy.session import bindSession, endSessions, commit, \
    setKeepAlive
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
import unittest

# --------------------------------------------------------------------

class TestMapping(unittest.TestCase):

    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        self.sessionCreate = sessionmaker(bind=engine)
        meta.create_all(engine)

    def test(self):
        articleTypeService = createProxy(IArticleTypeService)(ProxyWrapper(ArticleTypeServiceAlchemy()))
        assert isinstance(articleTypeService, IArticleTypeService)

        bindValidations(articleTypeService, mappingsOf(meta))
        bindSession(articleTypeService, self.sessionCreate)

        setKeepAlive(True)

        at = ArticleType()
        at.Name = 'Test Type 1'
        articleTypeService.insert(at)
        self.assertEqual(at.Id, 1)

        at.Id = 20
        # Validate auto id.
        self.assertRaisesRegex(InputError, "(ArticleType.Id='No value expected')", articleTypeService.insert, at)

        del at.Id
        at.Name = 'Test Type 2'
        articleTypeService.insert(at)
        self.assertEqual(at.Id, 2)

        endSessions(commit)

        at = ArticleType()
        at.Name = 'Test Type 1'
        # Validate unique id.
        self.assertRaisesRegex(InputError, "(ArticleType.Name='Already an entry with this value')",
                               articleTypeService.insert, at)

        at = ArticleType()
        at.Name = 'Test Type 3'
        articleTypeService.insert(at)
        self.assertEqual(at.Id, 3)

        endSessions(commit)

        at = articleTypeService.getById(2)
        at.Name = 'Invalid'
        endSessions(commit)
        at = articleTypeService.getById(2)
        self.assertEqual(at.Name, 'Test Type 2')

        endSessions(commit)

        at = articleTypeService.getById(2)
        at.Name = 'Invalid'
        articleTypeService.update(at)
        endSessions(commit)
        at = articleTypeService.getById(2)
        self.assertEqual(at.Name, 'Invalid')

        articleTypeService.delete(at.Id)
        self.assertRaisesRegex(InputError, "(ArticleType.Id='Unknown id')", articleTypeService.getById, at.Id)

        articleService = createProxy(IArticleService)(ProxyWrapper(ArticleServiceAlchemy()))
        assert isinstance(articleService, IArticleService)

        bindValidations(articleService, mappingsOf(meta))
        bindSession(articleService, self.sessionCreate)

        a = Article()
        a.Name = 'Article 1'
        a.Type = 1
        articleService.insert(a)
        self.assertEqual(a.Id, 1)

        a = Article()
        a.Name = 'Article 2'
        a.Type = 12
        # Invalid foreign key
        self.assertRaisesRegex(InputError, "(Article.Type='Unknown foreign id')", articleService.insert, a)

        endSessions(commit)

        a = articleService.getById(1)
        self.assertEqual(a.Id, 1)
        self.assertEqual(a.Name, 'Article 1')
        self.assertEqual(a.Type, 1)
        at = articleTypeService.getById(a.Type)
        self.assertEqual(at.Id, 1)
        self.assertEqual(at.Name, 'Test Type 1')

        endSessions(commit)

        q = QArticleType()
        q.name.orderDesc()
        self.assertEqual([e.Id for e in articleTypeService.getAll(q=q)], [3, 1])
        q = QArticleType()
        q.name.orderAsc()
        self.assertEqual([e.Id for e in articleTypeService.getAll(q=q)], [1, 3])
        q = QArticleType(name='%1')
        self.assertEqual([e.Id for e in articleTypeService.getAll(q=q)], [1])

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
