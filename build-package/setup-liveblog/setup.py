'''
Created on Sep 25, 2013

@package: Liveblog
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="liveblog",
    version="1.5.0",
    packages=find_packages(),
    install_requires=['ally-py >= 0.1'],
    platforms=['all'],
    zip_safe=True,
    package_data={'': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.js', '*.css', '*.less',
                       '*.dust', '*.html', '*.csv', '*.txt', '*.xsd', '*.exe',
                       '*.ffpreset', '*.so*', '*.a*', '*.dll', '*.dylib', '*.jar',
                       'AUTHORS', 'COPYING*', 'README*']},

    # metadata for upload to PyPI
    author="Sourcefabric",
    author_email="contact@sourcefabric.org",
    description="Liveblog",
    long_description='Live blogging application',
    license="GPL v3",
    keywords="Liveblog",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
    classifiers=[
                 'Development Status :: 5 - Production/Stable',
                 'Environment :: Web Environment',
                 'Intended Audience :: End Users/Desktop',
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: JavaScript',
                 'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
                 ]
)
