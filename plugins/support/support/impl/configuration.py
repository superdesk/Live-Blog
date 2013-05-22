'''
Created on May 22, 2013

@package: support
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for the configuration API.
'''

from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.util import aliased
from sqlalchemy.sql import functions as fn
from sqlalchemy.sql.expression import func, or_
from sqlalchemy.sql.operators import desc_op

# --------------------------------------------------------------------

def createConfigurationImpl(service, mapped):
    return type('%sAlchemy' % service.__name__[1:], (ConfigurationServiceAlchemy, service), {'ConfigurationMapped': mapped})
    

@injected
@setup(IConfigurationService, name='configurationService')
class ConfigurationServiceAlchemy(SessionSupport, IConfigurationService):
    '''
    Implementation for @see: IConfigurationService
    '''
    
    ConfigurationMapped = ConfigurationDescription
    # 

    def __init__(self, Configuration, ConfigurationMapped, QConfiguration=None):
        '''
        Construct the configuration service.
        '''
        self.Configuration = Configuration
        self.ConfigurationMapped = ConfigurationMapped
        self.QConfiguration = QConfiguration
        #self.ConfigurationMapped.parent

    def getByName(self, parentId, name):
        '''
        @see: IConfigurationService.getByName
        '''
        sql = self.session().query(self.ConfigurationMapped)
        sql = sql.filter(self.ConfigurationMapped.parent == parentId)
        sql = sql.filter(self.ConfigurationMapped.Name == name)
        try:
            return sql.one()
        except NoResultFound: raise InputError(Ref(_('No configuration'),))

    def getAll(self, parentId, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IConfigurationService.getAll
        '''
        sql = self.session().query(self.ConfigurationMapped)
        sql = sql.filter(self.ConfigurationMapped.parent == parentId)

        if q and self.QConfiguration:
            assert isinstance(q, self.QConfiguration), 'Invalid query %s' % q
            sql = buildQuery(sql, q, self.ConfigurationMapped)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def insert(self, parentId, configuration):
        #assert self.modelType.isValid(entity), 'Invalid entity %s, expected %s' % (entity, self.Entity)
        #assert isinstance(entity.Id, int), 'Invalid entity %s, with id %s' % (entity, entity.Id)
        configurationDb = copy(configuration, self.ConfigurationMapped())
        configurationDb.parent = parentId
        try:
            self.session().add(configurationDb)
            self.session().flush((configurationDb,))
        except SQLAlchemyError as e: handle(e, configurationDb)
        return configurationDb.Name

    def update(self, parentId:Entity.Id, configuration:Configuration):
        #assert self.modelType.isValid(entity), 'Invalid entity %s, expected %s' % (entity, self.Entity)
        #assert isinstance(entity.Id, int), 'Invalid entity %s, with id %s' % (entity, entity.Id)
        sql = self.session().query(self.ConfigurationMapped)
        sql = sql.filter(self.ConfigurationMapped.parent == parentId)
        sql = sql.filter(self.ConfigurationMapped.Name == configuration.Name)
        try:
            configurationDb = sql.one()
        except NoResultFound: raise InputError(Ref(_('Unknown configuration'),))
        configurationDb = copy(configuration, configurationDb)
        configurationDb.parent = parentId
        try: self.session().flush((configurationDb,))
        except SQLAlchemyError as e: handle(e, self.ConfigurationMapped)

    def delete(self, parentId:Entity.Id, name:Configuration.Name):
        sql = self.session().query(self.ConfigurationMapped)
        sql = sql.filter(self.ConfigurationMapped.parent == parentId)
        sql = sql.filter(self.ConfigurationMapped.Name == name)
        try:
            return sql.delete() > 0
        except OperationalError:
            raise InputError(Ref(_('Cannot delete the configuration'),))
