'''
Created on Nov 7, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is used in deploying the application.
'''
 
from __setup__.ally_core_plugin.deploy_plugin import configurations_file_path, \
    loadPlugins
from ally.container import ioc, aop
from ally.container._impl.ioc_setup import Assembly
from ally.container.config import load, save
import os
import sys
import traceback
try: import application
except ImportError:
    print('No application available to deploy', file=sys.stderr)
    sys.exit(1)
    
# --------------------------------------------------------------------

@ioc.start
def dump():
    if not application.options.write_configurations: return
    if not __debug__:
        print('Cannot dump configuration file if python is run with "-O" or "-OO" option', file=sys.stderr)
        sys.exit(1)
    try:
        ioc.activate(application.assembly)
        try: 
            loadPlugins()
            configFile = configurations_file_path()
        finally: ioc.deactivate()
        
        if os.path.isfile(configFile):
            with open(configFile, 'r') as f: config = load(f)
        else: config = {}
        
        assembly = ioc.open(aop.modulesIn('__plugin__.**'), config=config)
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        try:
            if os.path.isfile(configFile): os.rename(configFile, configFile + '.bck')
            for config in assembly.configurations: assembly.processForName(config)
            # Forcing the processing of all configurations
            with open(configFile, 'w') as f: save(assembly.trimmedConfigurations(), f)
        finally: ioc.deactivate()
    
    except SystemExit: raise
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while dumping configurations', file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print('-' * 150, file=sys.stderr)
