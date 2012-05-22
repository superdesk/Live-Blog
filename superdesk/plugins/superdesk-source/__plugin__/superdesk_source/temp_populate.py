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
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from superdesk.source.meta.type import SourceTypeMapped
from ally.container.support import entityFor
from superdesk.source.api.source import ISourceService, QSource, Source

# --------------------------------------------------------------------

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

# --------------------------------------------------------------------

@ioc.after(createTables)
def populate():
    getSourcesIds()
