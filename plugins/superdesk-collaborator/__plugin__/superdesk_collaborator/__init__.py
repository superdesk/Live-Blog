'''
Created on Apr 19, 2012

@package: superdesk collaborator
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the superdesk collaborator setup files.
'''

# --------------------------------------------------------------------

NAME = 'superdesk collaborator'
GROUP = 'Superdesk'
VERSION = '1.0'
DESCRIPTION = 'Provides the collaborator for content.'
LONG_DESCRIPTION = 'Collaborator functionality (model, service)'
AUTHOR = 'Gabriel Nistor'
AUTHOR_EMAIL = 'gabriel.nistor@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'Superdesk', 'plugin', 'collaborator']
INSTALL_REQUIRES = ['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'superdesk >= 1.0',
                    'superdesk-person >= 1.0', 'superdesk-source >= 1.0']

__extra__  = dict()