'''
Created on Nov 7, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is used in deploying the application.
'''
 
from .prepare import OptionsCore
from __setup__.ally_core.logging import format, debug_for, info_for, warning_for
from ally.container import ioc, aop
from ally.container._impl.ioc_setup import Assembly
from ally.container.config import load, save
from ally.container.ioc import SetupError, ConfigError
import os
import sys
import traceback

# --------------------------------------------------------------------

try: import application
except ImportError: raise

# --------------------------------------------------------------------

@ioc.start
def deploy():
    assert isinstance(application.options, OptionsCore), 'Invalid application options %s' % application.options
    if not application.options.start: return
    try:
        if not os.path.isfile(application.options.configurationPath):
            print('The configuration file "%s" doesn\'t exist, create one by running the the application '
                  'with "-dump" option' % application.options.configurationPath, file=sys.stderr)
            sys.exit(1)
        with open(application.options.configurationPath, 'r') as f: config = load(f)

        assembly = application.assembly = ioc.open(aop.modulesIn('__setup__.**'), config=config)
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        
        import logging
        logging.basicConfig(format=format())
        for name in warning_for(): logging.getLogger(name).setLevel(logging.WARN)
        for name in info_for(): logging.getLogger(name).setLevel(logging.INFO)
        for name in debug_for(): logging.getLogger(name).setLevel(logging.DEBUG)
        
        try: assembly.processStart()
        finally: ioc.deactivate()
    except SystemExit: raise
    except (SetupError, ConfigError):
        print('-' * 150, file=sys.stderr)
        print('A setup or configuration error occurred while deploying, try to rebuild the application properties by '
              'running the the application with "configure components" options', file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print('-' * 150, file=sys.stderr)
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while deploying', file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print('-' * 150, file=sys.stderr)
        
@ioc.start
def dump():
    assert isinstance(application.options, OptionsCore), 'Invalid application options %s' % application.options
    if not application.options.writeConfigurations: return
    if not __debug__:
        print('Cannot dump configuration file if python is run with "-O" or "-OO" option', file=sys.stderr)
        sys.exit(1)
    configFile = application.options.configurationPath
    try:
        if os.path.isfile(configFile):
            with open(configFile, 'r') as f: config = load(f)
        else: config = {}
        
        assembly = application.assembly = ioc.open(aop.modulesIn('__setup__.**'), config=config)
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        try:
            if os.path.isfile(configFile): os.rename(configFile, configFile + '.bak')
            for config in assembly.configurations: assembly.processForName(config)
            # Forcing the processing of all configurations
            with open(configFile, 'w') as f: save(assembly.trimmedConfigurations(), f)
            print('Created "%s" configuration file' % configFile)
        finally: ioc.deactivate()
    except SystemExit: raise
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while dumping configurations', file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print('-' * 150, file=sys.stderr)
