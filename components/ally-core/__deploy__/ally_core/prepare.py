'''
Created on Nov 7, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is used in preparing the application deploy.
'''

from ally.container import ioc
from argparse import ArgumentParser
from inspect import isclass

# --------------------------------------------------------------------

try: import application
except ImportError: raise

# --------------------------------------------------------------------

class OptionsCore:
    '''
    The prepared option class.
    '''
    
    def __init__(self):
        super().__init__()
        self._start = True  # Flag indicating that the application should be started
        self._writeConfigurations = False  # Indicates that the configurations should be written
        
        self.configurationPath = 'application.properties'
    
    def setStart(self, value):
        '''Setter for the start'''
        self._start = value
        self._writeConfigurations = self._writeConfigurations and not value
    
    def setWriteConfigurations(self, value):
        '''Setter for the configuration writing'''
        self._writeConfigurations = value
        self._start = self._start and not value
    
    start = property(lambda self: self._start, setStart)
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

@ioc.after(prepareCoreActions)
def prepareCorePreferences():
    assert isinstance(application.parser, ArgumentParser), 'Invalid application parser %s' % application.parser
    application.parser.add_argument('--ccfg', metavar='file', dest='configurationPath', help='The path of the components '
                                    'properties file to be used in deploying the application, by default is used the '
                                    '"application.properties" in the application module folder')
