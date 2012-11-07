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
import sys

# --------------------------------------------------------------------

try: import application
except ImportError:
    print('No application available to prepare', file=sys.stderr)
    sys.exit(1)
parser = application.parser
assert isinstance(parser, ArgumentParser), 'Invalid parser %s' % parser

# --------------------------------------------------------------------

@ioc.start
def populateCoreActions():
    parser.add_argument('-dump', dest='write_configurations', action='store_true', help='Provide this option in order to '
                        'write all the configuration files and exit')


@ioc.after(populateCoreActions)
def populateCoreOptions():
    parser.add_argument('--ccfg', metavar='file', dest='components_configurations', default='application.properties',
                        help='The path of the components properties file to be used in deploying the application, by default '
                        'is used the "application.properties" in the application module folder')
