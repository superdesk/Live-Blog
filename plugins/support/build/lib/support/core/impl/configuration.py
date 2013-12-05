'''
Created on May 22, 2013

@package: support
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for the configuration API.
'''

from sql_alchemy.support.util_service import SessionSupport, buildQuery, \
    iterateCollection, insertModel, updateModel
from support.meta.configuration import WithConfiguration
from support.api.configuration import QConfiguration, Configuration

# --------------------------------------------------------------------

class ConfigurationServiceAlchemy(SessionSupport):
    '''
    Provides support for handling configurations. By CATEGORY object is meant the object that has been configured to
    have the actions mapping on it.
    '''

    Configuration = WithConfiguration

    def __init__(self, Configuration):
        '''
        Construct the configuration service alchemy.

        @param ConfigurationMapped: Base class
            The configuration mapped class.
        '''
        assert issubclass(Configuration, WithConfiguration), 'Invalid mapped class %s' % Configuration

        self.Configuration = Configuration

    def getByName(self, targetId, name):
        '''
        @see: IConfigurationService.getByName
        '''
        sql = self.session().query(self.Configuration)
        sql = sql.filter(self.Configuration.targetId == targetId)
        sql = sql.filter(self.Configuration.Name == name)
        return sql.one()

    def getAll(self, targetId, q=None, **options):
        '''
        @see: IConfigurationService.getAll
        '''
        sql = self.session().query(self.Configuration.targetId)
        sql = sql.filter(self.Configuration.targetId == targetId)
        if q:
            assert isinstance(q, QConfiguration), 'Invalid query %s' % q
            sql = buildQuery(sql, q, self.Configuration)
        return iterateCollection(sql, **options)

    def insert(self, targetId, configuration):
        '''
        @see: IConfigurationService.insert
        '''
        assert isinstance(configuration, Configuration), 'Invalid configuration'
        return insertModel(self.Configuration, configuration, targetId=targetId).Name

    def update(self, targetId, configuration):
        '''
        @see: IConfigurationService.update
        '''
        assert isinstance(configuration, Configuration), 'Invalid configuration'
        updateModel(self.Configuration, configuration, targetId=targetId)

    def delete(self, targetId, name):
        '''
        @see: IConfigurationService.delete
        '''
        assert isinstance(name, str), 'Invalid configuration name %s' % name

        sql = self.session().query(self.Configuration)
        sql = sql.filter(self.Configuration.targetId == targetId)
        sql = sql.filter(self.Configuration.Name == name)
        return sql.delete() > 0
