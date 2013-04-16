'''
Created on Nov 7, 2012

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is used in preparing the application deploy.
'''

from ally.container import ioc
from argparse import ArgumentParser
from inspect import isclass
import application

# --------------------------------------------------------------------

class OptionsCore:
    '''
    The prepared option class.
    '''
    
    def __init__(self):
        super().__init__()
        self._start = True  # Flag indicating that the application should be started
        self._test = False  # Flag indicating that the application unit tests should be executed
        self._repair = False  # Flag indicating that the application should try a repair
        self._writeConfigurations = False  # Indicates that the configurations should be written
        
        self.configurationPath = 'application.properties'
    
    def setStart(self, value):
        '''Setter for the start'''
        self._start = value
        
    def setTest(self, value):
        '''Setter for the test'''
        self._test = value
        self._start = self._start and not value
        
    def setRepair(self, value):
        '''Setter for the repair'''
        self._repair = value
        self._start = self._start and not value
    
    def setWriteConfigurations(self, value):
        '''Setter for the configuration writing'''
        self._writeConfigurations = value
        self._start = self._start and not value
    
    start = property(lambda self: self._start, setStart)
    test = property(lambda self: self._test, setTest)
    repair = property(lambda self: self._repair, setRepair)
    writeConfigurations = property(lambda self: self._writeConfigurations, setWriteConfigurations)

# --------------------------------------------------------------------

@ioc.start
def prepareCoreOptions():
    assert isclass(application.Options), 'Invalid options class %s' % application.Options
    class Options(OptionsCore, application.Options): pass
    application.Options = Options

@ioc.after(prepareCoreOptions)
def prepareCoreActions():
    assert isinstance(application.parser, ArgumentParser), 'Invalid application parser %s' % application.parser
    application.parser.add_argument('-dump', dest='writeConfigurations', action='store_true',
                                    help='Provide this option in order to write all the configuration files and exit')
    application.parser.add_argument('-test', dest='test', action='store_true',
                                    help='Provide this option in order to run the unit tests in the application distribution')
    application.parser.add_argument('-repair', dest='repair', action='store_true',
                                    help='Provide this option in order to run the application distribution repair, this will'
                                    ' trigger all default data and resources to be populated')

@ioc.after(prepareCoreActions)
def prepareCorePreferences():
    assert isinstance(application.parser, ArgumentParser), 'Invalid application parser %s' % application.parser
    application.parser.add_argument('--ccfg', metavar='file', dest='configurationPath', help='The path of the components '
                                    'properties file to be used in deploying the application, by default is used the '
                                    '"application.properties" in the application module folder')
