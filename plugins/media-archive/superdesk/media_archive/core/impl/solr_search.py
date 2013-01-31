'''
Created on Jan 10, 2013

@package: superdesk media archive solr based search
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

The implementation for Solr based search API.
'''

from ally.container.ioc import injected
from sunburnt import SolrInterface
from superdesk.media_archive.core.impl.query_service_creator import QMetaDataInfo, \
     ISearchProvider
from superdesk.media_archive.api.criteria import AsLikeExpression
from superdesk.media_archive.meta.meta_data import MetaDataMapped
from superdesk.media_archive.meta.meta_info import MetaInfoMapped
from ally.container import wire
from itertools import chain
from ally.api.criteria import AsBoolean, AsLike, AsEqual, AsDate, AsDateTime, \
    AsRange, AsTime, AsOrdered
from ally.support.api.util_service import namesForQuery
from ally.api.extension import IterPart

@injected
class SolrSearchProvider(ISearchProvider):
    '''
    Implementation  @see: ISearchProvider
    '''

    solr_server_url = 'localhost:8983/solr/'; wire.config('solr_server_url', doc='''The Solr server address
    ''')


    def __init__(self):
        assert isinstance(self.solr_server_url, str), 'Invalid solr server url %s' % self.solr_server_url

    # ----------------------------------------------------------------

    def update(self, metaInfo, metaData):
        '''
        @see: ISearchProvider.update()
        '''

        si = SolrInterface('http://%s%s' % (self.solr_server_url, metaData.Type))

        document = dict()

        document["MetaInfoId"] = metaInfo.Id
        document["MetaDataId"] = metaData.Id
        document["languageId"] = metaInfo.Language

        # custom processing on some fields
        field = 'CreationDate'
        if hasattr(metaInfo, field) and getattr(metaInfo, field):
            document['CreationData_Year'] = getattr(metaInfo, field).year

        for field in si.schema.fields:
            if hasattr(metaInfo, field) and getattr(metaInfo, field):
                document[field] = getattr(metaInfo, field)
            elif hasattr(metaData, field) and getattr(metaData, field):
                document[field] = getattr(metaData, field)

        si.add(document)
        si.commit()

    # ----------------------------------------------------------------

    def delete(self, idMetaInfo, idMetaData):
        '''
        @see: ISearchProvider.delete()
        '''
        print('MetaDataServiceAlchemy - delete idMetaInfo=%d, idMetaData=%d', idMetaInfo, idMetaData)

    # ----------------------------------------------------------------

    def processQuery(self, session, scheme, qa=None, qi=None, qd=None):
        '''
        Creates the solr query based on received REST queries
        '''

        si = SolrInterface('http://%sother' % self.solr_server_url)
        types = [self.queryIndexer.typesByMetaData[key] for key in self.queryIndexer.typesByMetaData.keys()]

        solrQuery = None
        orClauses = []

        if qa is not None:
            assert isinstance(qa, QMetaDataInfo), 'Invalid query %s' % qa
            solrQuery = buildSolrQuery(si, solrQuery, qa, orClauses)
            if QMetaDataInfo.type in qa: types = qa.type.values

        if qi is not None:
            solrQuery = buildSolrQuery(si, solrQuery, qi, orClauses)

        if qd is not None:
            solrQuery = buildSolrQuery(si, solrQuery, qd, orClauses)

        if orClauses:
            extend = None
            for clause in orClauses:
                if extend: extend = extend | clause
                else: extend = clause

            if solrQuery is None: solrQuery = si.query(extend)
            else: solrQuery = solrQuery.query(extend)

        if solrQuery is None: solrQuery = si.query()
        solrQuery = buildShards(solrQuery, self.solr_server_url, types)

        return solrQuery

    # ----------------------------------------------------------------

    def buildQuery(self, session, scheme, offset=None, limit=1000, qa=None, qi=None, qd=None):
        '''
        @see: ISearchProvider.buildQuery()

        Creates the solr query, executes the query against Solr server. Then build a SQL query that will return
        the Solr founded data.
        '''

        solrQuery = self.processQuery(session, scheme, qa, qi, qd)
        solrQuery = buildLimits(solrQuery, offset, limit)

        response = solrQuery.execute()
        if response.status != 0:
            return None

        count = response.result.numFound
        sql = session.query(MetaDataMapped, MetaInfoMapped)
        sql = sql.join(MetaInfoMapped, MetaDataMapped.Id == MetaInfoMapped.MetaData)

        idList = []
        for metaDataInfo in response:
            print(metaDataInfo)
            idList.append(metaDataInfo["MetaDataId"])

        if idList:
            sql = sql.filter(MetaInfoMapped.Id.in_(idList))

        # TODO: test
        self.buildFacetsQuery(session, scheme, qa=None, qi=None, qd=None)

        return (sql, count)


# ----------------------------------------------------------------

    def buildFacetsQuery(self, session, scheme, qa=None, qi=None, qd=None):
        '''
        @see: ISearchProvider.getFacets()

        Creates the solr facets query and then return the list of facets
        '''

        facets = []

        solrQuery = self.processQuery(session, scheme, qa, qi, qd)

        # construct the facets query
        solrQuery = solrQuery.facet_by("Type")
        solrQuery = solrQuery.facet_by("AudioEncoding")
        solrQuery = solrQuery.facet_by("SampleRate")
        solrQuery = solrQuery.facet_by("AudioBitrate")
        solrQuery = solrQuery.facet_by("Genre")
        solrQuery = solrQuery.facet_by("Year")
        solrQuery = solrQuery.facet_by("CameraMake")
        solrQuery = solrQuery.facet_by("VideoEncoding")
        solrQuery = solrQuery.facet_by("VideoBitrate")

        response = solrQuery.execute()
        if response.status != 0:
            return None

        count = response.result.numFound

        # init the list of facets
        print (response.facet_counts.facet_fields)

        return IterPart(facets, count, 0, count)

# ----------------------------------------------------------------


def buildSolrQuery(si, solrQuery, query, orClauses):
    '''
    Builds the Solr query based on a given REST query.

    @param si: SorlInterface
        The current connection to Solr server.
    @param solrQuery: SolrSearch
        The solr query to use.
    @param query: query
        The REST query object to provide querying on.
    @param mapped: List
        The list of OR clauses.
    '''

    ordered, unordered = [], []
    clazz = query.__class__

    for criteria in namesForQuery(clazz):
        if getattr(clazz, criteria) not in query: continue

        if criteria in si.schema.fields:
            field = criteria
        else:
            upperCriteria = criteria[0].upper() + criteria[1:]
            if upperCriteria in si.schema.fields:
                field = upperCriteria
            else: continue

        crt = getattr(query, criteria)

        if isinstance(crt, AsBoolean):
            if AsBoolean.value in crt:
                if solrQuery is None: solrQuery = si.query(**{field : crt.value})
                else: solrQuery = solrQuery.query(**{field : crt.value})
        elif isinstance(crt, AsLike):
            if AsLike.like in crt:
                if solrQuery is None: solrQuery = si.query(**{field : crt.like})
                else: solrQuery = solrQuery.query(**{field : crt.like})
            elif AsLike.ilike in crt:
                if solrQuery is None: solrQuery = si.query(**{field : crt.ilike})
                else: solrQuery = solrQuery.query(**{field : crt.ilike})
        elif isinstance(crt, AsEqual):
            if AsEqual.equal in crt:
                if solrQuery is None: solrQuery = si.query(**{field : crt.equal})
                else: solrQuery = solrQuery.query(**{field : crt.equal})
        elif isinstance(crt, (AsDate, AsTime, AsDateTime, AsRange)):
            if crt.__class__.start in crt:
                if solrQuery is None: solrQuery = si.query(**{field + '__gte' : crt.start})
                else: solrQuery = solrQuery.query(**{field + '__gte' : crt.start})
            elif crt.__class__.until in crt:
                if solrQuery is None: solrQuery = si.query(**{field + '__lt' : crt.until})
                else: solrQuery = solrQuery.query(**{field + '__lt' : crt.until})
            if crt.__class__.end in crt:
                if solrQuery is None: solrQuery = si.query(**{field + '__lte' : crt.end})
                else: solrQuery = solrQuery.query(**{field + '__lte' : crt.end})
            elif crt.__class__.since in crt:
                if solrQuery is None: solrQuery = si.query(**{field + '__gt' : crt.since})
                else: solrQuery = solrQuery.query(**{field + '__gt' : crt.since})
        elif isinstance(crt, AsLikeExpression):
            if AsLikeExpression.inc in crt:
                for value in crt.inc:
                    if solrQuery is None: solrQuery = si.query(**{field : value})
                    else: solrQuery = solrQuery.query(**{field : value})
            if crt and AsLikeExpression.ext in crt:
                for value in crt.ext:
                    orClauses.append(si.Q(**{field : value}))
            if crt and AsLikeExpression.exc in crt:
                for value in crt.exc:
                    if solrQuery is None: solrQuery = si.exclude(**{field : value})
                    else: solrQuery = solrQuery.exclude(**{field : value})


        if isinstance(crt, AsOrdered):
            assert isinstance(crt, AsOrdered)
            if AsOrdered.ascending in crt:
                if AsOrdered.priority in crt and crt.priority:
                    ordered.append((field, crt.ascending, crt.priority))
                else:
                    unordered.append((field, crt.ascending, None))

        ordered.sort(key=lambda pack: pack[2])
        for field, asc, __ in chain(ordered, unordered):
            if asc:
                if solrQuery is None: solrQuery = si.sort_by(field)
                else: solrQuery = solrQuery.sort_by(field)
            else:
                if solrQuery is None: solrQuery = si.sort_by('-' + field)
                else: solrQuery = solrQuery.sort_by('-' + field)

    return solrQuery

# ----------------------------------------------------------------

def buildShards(solrQuery, solrServer, types):
    for type in types:
        solrQuery = solrQuery.add_shard("%s%s" % (solrServer, type))
    return solrQuery

# ----------------------------------------------------------------

def buildLimits(solrQuery, offset, limit):
    if offset and not limit:
        solrQuery = solrQuery.paginate(start=offset)
    elif not offset and limit:
        solrQuery = solrQuery.paginate(start=0, rows=limit)
    elif offset and limit:
        solrQuery = solrQuery.paginate(start=offset, rows=limit)
    return solrQuery


