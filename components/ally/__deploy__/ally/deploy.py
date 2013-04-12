'''
Created on Nov 7, 2012

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is used in deploying the application.
'''

from .prepare import OptionsCore
from __setup__.ally.logging import format, debug_for, info_for, warning_for, log_file
from ally.container import ioc, aop, context, support, event
from ally.container.error import SetupError, ConfigError
from ally.container.impl.config import load, save
import application
import logging
import os
import sys
import traceback
import unittest
from logging import FileHandler

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def openSetups():
    ''' Open the assembly for setups '''
    if not os.path.isfile(application.options.configurationPath):
        print('The configuration file "%s" doesn\'t exist, create one by running the the application '
              'with "-dump" option' % application.options.configurationPath, file=sys.stderr)
        sys.exit(1)
    with open(application.options.configurationPath, 'r') as f: config = load(f)

    context.open(aop.modulesIn('__setup__.ally.**'), config=config)
    
    logging.basicConfig(format=format())
    for name in warning_for(): logging.getLogger(name).setLevel(logging.WARN)
    for name in info_for(): logging.getLogger(name).setLevel(logging.INFO)
    for name in debug_for(): logging.getLogger(name).setLevel(logging.DEBUG)
    
    context.deactivate()
    
    context.open(aop.modulesIn('__setup__.**'), config=config)
    
# --------------------------------------------------------------------

@ioc.entity
def dumpAssembly():
    assert isinstance(application.options, OptionsCore), 'Invalid application options %s' % application.options
    configFile = application.options.configurationPath

    if os.path.isfile(configFile):
        with open(configFile, 'r') as f: config = load(f)
    else: config = {}

    return context.open(aop.modulesIn('__setup__.**'), config=config, active=False)

# --------------------------------------------------------------------

@ioc.start
def deploy():
    assert isinstance(application.options, OptionsCore), 'Invalid application options %s' % application.options
    if not application.options.start: return
    try:
        openSetups()
        context.processStart()
        if log_file(): logging.getLogger().addHandler(FileHandler(log_file()))

    except SystemExit: raise
    except (SetupError, ConfigError):
        print('-' * 150, file=sys.stderr)
        print('A setup or configuration error occurred while deploying, try to rebuild the application properties by '
              'running the the application with "-dump" option', file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print('-' * 150, file=sys.stderr)
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while deploying', file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print('-' * 150, file=sys.stderr)
    finally: context.deactivate()

@ioc.start
def dump():
    assert isinstance(application.options, OptionsCore), 'Invalid application options %s' % application.options
    if not application.options.writeConfigurations: return
    if not __debug__:
        print('Cannot dump configuration file if python is run with "-O" or "-OO" option', file=sys.stderr)
        sys.exit(1)
    assembly, configFile = dumpAssembly(), application.options.configurationPath
    try:
        context.activate(assembly)
        try:
            if os.path.isfile(configFile): os.rename(configFile, configFile + '.bak')
            for config in assembly.configurations:
                try: assembly.processForName(config)
                except ConfigError as e: print('Failed to fetch a value for configuration \'%s\': %s' % (config, e))
            # Forcing the processing of all configurations
            with open(configFile, 'w') as f: save(assembly.trimmedConfigurations(), f)
            print('Created "%s" configuration file' % configFile)
        finally: context.deactivate()
    except SystemExit: raise
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while dumping configurations', file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print('-' * 150, file=sys.stderr)

@ioc.start
def test():
    assert isinstance(application.options, OptionsCore), 'Invalid application options %s' % application.options
    if not application.options.test: return
    classes = aop.classesIn('__unit_test__.**.*').asList()
    classes = [clazz for clazz in classes if issubclass(clazz, unittest.TestCase)]
    if not classes:
        print('-' * 71, file=sys.stderr)
        print('No unit test available', file=sys.stderr)
        sys.exit(1)
    testLoader, runner, tests = unittest.TestLoader(), unittest.TextTestRunner(stream=sys.stdout), unittest.TestSuite()
    for clazz in classes: tests.addTest(testLoader.loadTestsFromTestCase(clazz))
    runner.run(tests)

@ioc.start
def repair():
    assert isinstance(application.options, OptionsCore), 'Invalid application options %s' % application.options
    if not application.options.repair: return
    try:
        openSetups()
        for call, name, _trigger in support.eventsFor(event.REPAIR):
            log.info('Executing repair event call \'%s\'', name)
            call()
            
    except SystemExit: raise
    except (SetupError, ConfigError):
        print('-' * 150, file=sys.stderr)
        print('A setup or configuration error occurred while deploying, try to rebuild the application properties by '
              'running the the application with "-dump" options', file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print('-' * 150, file=sys.stderr)
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while repairing', file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print('-' * 150, file=sys.stderr)
    finally: context.deactivate()
