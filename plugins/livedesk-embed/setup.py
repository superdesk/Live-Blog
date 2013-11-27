
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
           package_data={'': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less', '*.dust', '*.html']},
     description='This plugin provides the embed scripts for Livedesk.',
     author='Mihai Nistor',
     install_requires=['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'gui-action >= 1.0', 'gui-core >= 1.0', 'internationalization >= 1.0', 'superdesk-collaborator >= 1.0', 'language >= 1.0', 'superdesk-person >= 1.0', 'superdesk-post >= 1.0', 'superdesk-source >= 1.0', 'superdesk-user >= 1.0', 'livedesk >= 1.0'],
     author_email='mihai.nistor@sourcefabric.org',
     version='1.0',
     keywords=['Ally', 'REST', 'Superdesk', 'plugin', 'livedesk', 'embed'],
     long_description='Implementation of the Livedesk embed plugin',
     name='livedesk-embed',

     )