
'''
Created on Oct 1, 2013
 
@package: distribution_manager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Cristian Domsa
 
Auto-generated setup configuration for components/plugins needed for pypi.
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(packages=find_packages('.'),
      platforms=['all'],
      zip_safe=True,
      license='GPL v3',
      url='http://www.sourcefabric.org/en/superdesk/', # project home page
           author='Mihai Nistor',
     description='This plugin provides the embed scripts for Livedesk.',
     keywords=['Ally', 'REST', 'Superdesk', 'plugin', 'livedesk', 'embed'],
     author_email='mihai.nistor@sourcefabric.org',
     name='livedesk-embed',
     long_description='Implementation of the Livedesk embed plugin',
     package_data={'': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html']},
     version='1.0',
     install_requires=['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'gui-action >= 1.0', 'gui-core >= 1.0', 'internationalization >= 1.0', 'superdesk-collaborator >= 1.0', 'superdesk-language >= 1.0', 'superdesk-person >= 1.0', 'superdesk-post >= 1.0', 'superdesk-source >= 1.0', 'superdesk-user >= 1.0', 'livedesk >= 1.0'],

     )