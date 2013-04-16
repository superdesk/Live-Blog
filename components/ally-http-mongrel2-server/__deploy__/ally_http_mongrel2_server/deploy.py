'''
Created on Nov 7, 2012

@package: ally http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is used in deploying the application.
'''
 
from .prepare import OptionsMongrel2
from __setup__.ally_http import server_port, server_type
from __setup__.ally_http_mongrel2_server.server import send_spec, send_ident, \
    recv_spec, recv_ident
from ally.container import aop, ioc, support, context
from ally.container.impl.config import load, save
from ally.support.util_io import openURI, ReplaceInFile, pipe
from ally.support.util_sys import pythonPath
from os import path, makedirs, renames
from uuid import uuid4
import application
import codecs
import sys
import traceback

# --------------------------------------------------------------------

@ioc.start
def config():
    assert isinstance(application.options, OptionsMongrel2), 'Invalid application options %s' % application.options
    if not application.options.configMongrel2: return
    workspace = application.options.configMongrel2
    folders = [path.join('mongrel2', name) for name in ('logs', 'run', 'tmp')]
    folders.append(path.join('shared', 'upload'))

    for name in folders:
        folder = path.join(workspace, name)
        if not path.isdir(folder): makedirs(folder)
    
    configFile = application.options.configurationPath
    if path.isfile(configFile):
        with open(configFile, 'r') as f: config = load(f)
    else:
        print('The configuration file "%s" doesn\'t exist, create one by running the the application '
              'with "-dump" option, also change the application properties "server_type" configuration to "mongrel2" '
              'and also adjust the "recv_spec", "send_spec" and "server_port" accordingly' % configFile, file=sys.stderr)
        sys.exit(1)
        
    try:
        context.open(aop.modulesIn('__setup__.**'), config=config)
    
        updateConfig = False
        if server_type() != 'mongrel2':
            updateConfig = True
            support.persist(server_type, 'mongrel2')
        
        sendIdent = send_ident()
        if sendIdent is None:
            updateConfig = True
            sendIdent = str(uuid4())
            support.persist(send_ident, sendIdent)
        
        replace = {}
        try:
            replace['${send_spec}'] = send_spec()
            replace['${send_ident}'] = sendIdent
            replace['${recv_spec}'] = recv_spec()
            replace['${recv_ident}'] = recv_ident()
            replace['${server_port}'] = str(server_port())
        
            if updateConfig:
                if path.isfile(configFile): renames(configFile, configFile + '.bak')
                with open(configFile, 'w') as f: save(context.configurations(force=True), f)
                print('Updated the "%s" configuration file' % configFile)
        finally: context.deactivate()
    except SystemExit: raise
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while configuring Mongrel2', file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print('-' * 150, file=sys.stderr)
    else:
        conf = openURI(path.join(pythonPath(), 'resources', 'ally.conf'))
        conf = codecs.getreader('utf8')(conf)
        conf = ReplaceInFile(conf, replace)
        with open(path.join(workspace, 'ally.conf'), 'w') as f: pipe(conf, f)
        with open(path.join(workspace, 'README-Mongrel2.txt'), 'wb') as f:
            pipe(openURI(path.join(pythonPath(), 'resources', 'README-Mongrel2.txt')), f)
        
        print('Configured "%s" mongrel2 workspace' % workspace)
    
