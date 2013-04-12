'''
Created on Nov 7, 2012

@package: ally http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is used in preparing the application deploy.
'''

from ..ally.prepare import OptionsCore, prepareCoreOptions, \
    prepareCoreActions
from ally.container import ioc
from argparse import ArgumentParser
from inspect import isclass
import application

# --------------------------------------------------------------------

class OptionsMongrel2(OptionsCore):
    '''
    The prepared option class.
    '''
    
    def __init__(self):
        super().__init__()
        self._configMongrel2 = False
    
    def setConfigMongrel2(self, value):
        '''Setter for the mongrel2 configure'''
        if value is None: value = 'workspace'
        self._configMongrel2 = value
        self._start = self._start and not value
    
    configMongrel2 = property(lambda self: self._configMongrel2, setConfigMongrel2)

# --------------------------------------------------------------------

@ioc.after(prepareCoreOptions)
def prepareMongrel2Options():
    assert isclass(application.Options), 'Invalid options class %s' % application.Options
    class Options(OptionsMongrel2, application.Options): pass
    application.Options = Options


@ioc.after(prepareCoreActions)
def prepareMongrel2Actions():
    assert isinstance(application.parser, ArgumentParser), 'Invalid parser %s' % application.parser
    application.parser.add_argument('-cfg-mongrel2', metavar='folder', dest='configMongrel2', nargs='?', default=False,
                                    help='Provide this option to create the mongrel2 workspace, by default the mongrel2 '
                                    'workspace will be created by default in "workspace" in the application folder, '
                                    'just provide a new mongrel2 workspace if thats the case, the path can be relative to '
                                    'the application folder or absolute')
