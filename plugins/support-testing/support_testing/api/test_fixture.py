'''
Created on April 1, 2014

@package: testing_support - test fixture
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API specifications for test fixture.
'''

from ally.api.config import service, call, UPDATE, INSERT, LIMIT_DEFAULT, query
from superdesk.api.domain_superdesk import modelTool
from ally.api.type import Iter
from ally.api.criteria import AsLikeOrdered


@modelTool(id='Name')
class TestFixture:
    '''
    Provides the text fixture model
    '''
    Name = str
    ApplyOnDatabase = bool
    ApplyOnFiles = bool
    

# --------------------------------------------------------------------

@query(TestFixture)
class QTestFixture:
    '''
    Provides the query for test fixture model.
    '''
    name = AsLikeOrdered
    
# --------------------------------------------------------------------   

@service
class ITestFixtureService:
    '''
    Test fixture service API.
    '''
           
    @call
    def getAll(self, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
               q:TestFixture=None) -> Iter(TestFixture):
        '''
        Return the list of all available test fixtures
        '''   
         
    @call(method=UPDATE)
    def applyTestFixture(self, testFixture:TestFixture) -> bool:
        '''
        Apply the test fixture to the current instance
        '''
    
    @call(method=INSERT)
    def createTestFixture(self, testFixture:TestFixture) -> TestFixture.Name:
        '''
        Create a new test fixture from the current state of the instance
        ''' 
# --------------------------------------------------------------------
