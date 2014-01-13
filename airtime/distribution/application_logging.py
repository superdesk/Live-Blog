'''
Created on Jan 16, 2012

@package: Superdesk
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the application logging setup.
'''

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s (%(threadName)s %(module)s.%(funcName)s %(lineno)d): %(message)s')
logging.basicConfig(format='%(module)s.%(funcName)s %(lineno)d: %(message)s')

logging.getLogger('ally').setLevel(logging.WARN)
logging.getLogger('ally.core.http.server').setLevel(logging.INFO)

logging.getLogger('cherrypy').setLevel(logging.WARN)
