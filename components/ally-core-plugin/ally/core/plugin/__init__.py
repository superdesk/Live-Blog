'''
Created on Jul 15, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

This package contains specifications, implementations and server basic configuration *server_config* that are specific
for HTTP protocol and REST architecture.
'''

# This is required in order to allow the extension of this package.
try: from __main__ import deployExtendPackage
except ImportError: pass
else: deployExtendPackage()