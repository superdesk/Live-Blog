'''
Created on Jan 16, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the application logging setup.
'''

import logging
#logging.basicConfig(format='%(asctime)s %(levelname)s (%(threadName)s %(module)s.%(funcName)s %(lineno)d): %(message)s')
logging.basicConfig(format='%(module)s.%(funcName)s %(lineno)d: %(message)s')

#logging.getLogger('ally.core.impl.assembler').setLevel(logging.DEBUG)
#logging.getLogger('newscoop').setLevel(logging.WARN)

#logging.getLogger('internationalization.scanner').setLevel(logging.DEBUG)
#logging.getLogger('ally.support.sqlalchemy.mapper').setLevel(logging.DEBUG)
#logging.getLogger('__plugin__').setLevel(logging.DEBUG)

#logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
#logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARN)
#logging.getLogger('sqlalchemy.pool').setLevel(logging.WARN)
#logging.getLogger('sqlalchemy.orm').setLevel(logging.DEBUG)

#logging.getLogger('__plugin__').setLevel(logging.WARN)

logging.getLogger('ally').setLevel(logging.WARN)
#logging.getLogger('ally.container').setLevel(logging.INFO)
#logging.getLogger('ally.container._impl.support_setup').setLevel(logging.DEBUG)
#logging.getLogger('ally.support.sqlalchemy.session').setLevel(logging.DEBUG)

#logging.getLogger('print_desk').setLevel(logging.WARN)

#logging.getLogger('ally.core.impl.assembler').setLevel(logging.DEBUG)
#logging.getLogger('ally_deploy_plugin').setLevel(logging.WARN)

logging.getLogger('cherrypy').setLevel(logging.WARN)
