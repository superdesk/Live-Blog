'''
Created on May 22, 2013

@package: support
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for the configuration API.
'''

from ..api.configuration import Configuration, QConfiguration, IConfigurationService
from ..meta.configuration import ConfigurationDescription
from ally.container.ioc import injected
from ally.container.support import setup
from ally.internationalization import _
from ally.api.extension import IterPart
from ally.support.util_sys import callerGlobals
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm.exc import NoResultFound
from sql_alchemy.support.util_service import SessionSupport, buildQuery, \
    iterateCollection
from ally.api.error import InputError

# --------------------------------------------------------------------

def createConfigurationImpl(service, mapped):
    '''
    Generator of particular configuration implementations

    @param service: class
        The service that implements particular configuration API.
    @param mapped: class
        The mapping of Configuration API into particular configuration table.

    @return: The implementation class for the particular configuration API.
        The created class is from the module that calls the function.
    '''
    assert issubclass(service, IConfigurationService), 'Invalid service. It should extend the IConfigurationService'
    assert issubclass(mapped, ConfigurationDescription), 'Invalid DB mapping. It should extend the ConfigurationDescription mapping'
    assert issubclass(mapped, Configuration), 'Invalid DB mapping. It should extend the Configuration class'

    namespace = {'ConfigurationMapped': mapped, '__module__': callerGlobals()['__name__']}
    return type('%sAlchemy' % service.__name__[1:], (ConfigurationServiceAlchemy, service), namespace)

# --------------------------------------------------------------------

@injected
@setup(IConfigurationService, name='configurationService')
class ConfigurationServiceAlchemy(SessionSupport, IConfigurationService):
    '''
    Implementation for @see: IConfigurationService
    '''
    
    ConfigurationMapped = ConfigurationDescription
    # variable for the DB mapping class to be used

    def getByName(self, parentId, name):
        '''
        @see: IConfigurationService.getByName
        '''
        sql = self.session().query(self.ConfigurationMapped)
        sql = sql.filter(self.ConfigurationMapped.parent == parentId)
        sql = sql.filter(self.ConfigurationMapped.Name == name)
        return sql.one()

    def getAll(self, parentId, q=None, **options):
        '''
        @see: IConfigurationService.getAll
        '''
        sql = self.session().query(self.ConfigurationMapped)
        sql = sql.filter(self.ConfigurationMapped.parent == parentId)

        if q:
            assert isinstance(q, QConfiguration), 'Invalid query'
            sql = buildQuery(sql, q, self.ConfigurationMapped)
        return iterateCollection(sql, **options)

    def insert(self, parentId, configuration):
        '''
        @see: IConfigurationService.insert
        '''
        assert isinstance(parentId, int), 'Invalid parentId'
        assert isinstance(configuration, Configuration), 'Invalid configuration'

        if not configuration.Name:
            raise InputError(Ref(_('No configuration name'),))

        configurationDb = copy(configuration, self.ConfigurationMapped())
        configurationDb.parent = parentId
        try:
            self.session().add(configurationDb)
            self.session().flush((configurationDb,))
        except SQLAlchemyError as e: handle(e, configurationDb)
        return configurationDb.Name

    def update(self, parentId, configuration):
        '''
        @see: IConfigurationService.update
        '''
        assert isinstance(parentId, int), 'Invalid parentId'
        assert isinstance(configuration, Configuration), 'Invalid configuration'

        sql = self.session().query(self.ConfigurationMapped)
        sql = sql.filter(self.ConfigurationMapped.parent == parentId)
        sql = sql.filter(self.ConfigurationMapped.Name == configuration.Name)
        try:
            configurationDb = sql.one()
        except NoResultFound: raise InputError(Ref(_('Unknown configuration'),))

        configurationDb.Value = configuration.Value
        configurationDb.parent = parentId
        try: self.session().flush((configurationDb,))
        except SQLAlchemyError as e: handle(e, self.ConfigurationMapped)

    def delete(self, parentId, name):
        '''
        @see: IConfigurationService.delete
        '''
        assert isinstance(parentId, int), 'Invalid parentId'
        assert isinstance(name, str), 'Invalid configuration name'

        sql = self.session().query(self.ConfigurationMapped)
        sql = sql.filter(self.ConfigurationMapped.parent == parentId)
        sql = sql.filter(self.ConfigurationMapped.Name == name)
        try:
            return sql.delete() > 0
        except OperationalError:
            raise InputError(Ref(_('Cannot delete the configuration'),))
