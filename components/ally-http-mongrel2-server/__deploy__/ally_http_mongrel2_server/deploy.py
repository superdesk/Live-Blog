'''
Created on Nov 7, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is used in deploying the application.
'''
 
from .prepare import OptionsMongrel2
from __setup__.ally_core_http import server_port
from __setup__.ally_http_mongrel2_server.server import send_spec, send_ident, \
    recv_spec, recv_ident
from ally.container import aop, ioc
from ally.container._impl.ioc_setup import Assembly
from ally.container.config import load
from ally.support.util_io import openURI, ReplaceInFile
from ally.support.util_sys import pythonPath
import codecs
import os
import sys
import traceback
from uuid import uuid4

# --------------------------------------------------------------------

try: import application
except ImportError: raise

# --------------------------------------------------------------------

@ioc.start
def config():
    assert isinstance(application.options, OptionsMongrel2), 'Invalid application options %s' % application.options
    if not application.options.configMongrel2: return
    workspace = application.options.configMongrel2
    for name in ('cdm', 'logs', 'run', 'tmp', 'upload'):
        path = os.path.join(workspace, name)
        if not os.path.isdir(path): os.makedirs(path)
    
    try:
        with open(application.options.configurationPath, 'r') as f: config = load(f)
        assembly = application.assembly = ioc.open(aop.modulesIn('__setup__.**'), config=config)
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        
        sendIdent, recvIdent = send_ident(), recv_ident()
        if sendIdent is None: sendIdent = str(uuid4())
        if recvIdent is None: recvIdent = str(uuid4())
        
        replace = {}
        try:
            replace['${send_spec}'] = send_spec()
            replace['${send_ident}'] = sendIdent
            replace['${recv_spec}'] = recv_spec()
            replace['${recv_ident}'] = recvIdent
            replace['${server_port}'] = str(server_port())
        finally: ioc.deactivate()
    except SystemExit: raise
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while configuring Mongrel2', file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print('-' * 150, file=sys.stderr)
    else:
        conf = openURI(os.path.join(pythonPath(), 'ally.conf'))
        conf = codecs.getreader('utf8')(conf)
        conf = ReplaceInFile(conf, replace)
        with open(os.path.join(workspace, 'ally.conf'), 'w') as f: f.write(conf.read())
        
        print('Created "%s" mongrel2 workspace' % workspace)
        
    
