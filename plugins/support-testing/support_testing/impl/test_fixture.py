'''
Created on April 1, 2014

@package: support testing - test fixture service
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Test fixture management implementation.
'''

import datetime
import logging

from ally.api.extension import IterPart
from ally.cdm.spec import ICDM
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.session import SessionSupport
from support_testing.api.test_fixture import ITestFixtureService, TestFixture
from support_testing.core.database_tool import DatabaseTool


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected    
@setup(ITestFixtureService, name='testFixture')
class TestFixtureService(ITestFixtureService, SessionSupport):
    '''
    Implementation for @see: ITestFixtureService
    '''
    cdmTestFixtures = ICDM; wire.entity('cdmTestFixtures')
    del_script_path_format = '/%(name)s/%(database)s_del.sql'
    add_script_path_format = '/%(name)s/%(database)s_add.sql'

    def getAll(self, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: ITestFixtureService.getAll
        '''
        
        testFixture = TestFixture()
        testFixture.Name = 'default'
        testFixture.ApplyOnDatabase = True
        testFixture.ApplyOnFiles = False
        
        if detailed: return IterPart([testFixture,], 1, offset, limit)
        return [testFixture,]
        
    def applyTestFixture(self, testFixture):
        '''
        @see: ITestFixtureService.applyTestFixture
        ''' 
        
        start = datetime.datetime.now()
        
        databaseTool = DatabaseTool()
        path = 'tests'       
        del_path = path + self.del_script_path_format % {'name' : testFixture.Name, 'database' : 'mysql'}
        add_path = path + self.add_script_path_format % {'name' : testFixture.Name, 'database' : 'mysql'}
        
        del_path = self.cdmTestFixtures.getURI(del_path, protocol='file')
        add_path = self.cdmTestFixtures.getURI(add_path, protocol='file')
        
        result = databaseTool.runscript(self.session(), del_path) 
        
        log.info('delete: ', datetime.datetime.now() - start)
        
        if result:
            result = databaseTool.runscript(self.session(), add_path)
        
        log.info('populate: ', datetime.datetime.now() - start)
        
        return result
        
    def createTestFixture(self, testFixture):
        '''
        @see: ITestFixtureService.createTestFixture
        ''' 
        
        #TODO - generate the truncate script:
        # SELECT Concat('DELETE FROM ', TABLE_NAME, ';')  
        # FROM INFORMATION_SCHEMA.TABLES where table_schema = 'lb';
        
        # SELECT Concat('ALTER TABLE ', TABLE_NAME, ' AUTO_INCREMENT = 1;')  
        # FROM INFORMATION_SCHEMA.TABLES where table_schema = 'lb';
        
        #TODO - generate the populate script:
        #mysqldump -uroot -proot --no-create-info --compact --add-locks=FALSE lb > mysql_add.sql
        
        log.info('createTestFixture', str(testFixture))        
        
        