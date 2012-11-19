'''
Created on Oct 8, 2012

@package: ally-py
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the documentation of the distribution.
'''

from distutils.dir_util import copy_tree
from shutil import rmtree
import os
import sys

# --------------------------------------------------------------------

MARK_PACKAGE = ('__setup__', '__plugin__')
# The root packages that define a component or plugin
REMOVE = ('__setup__', '__plugin__', 'test', 'setup.py')
# The root resources to be removed.

CODE_SOURCES = ('../plugins', )
# Contains the sources folders
CODE_DESTINATION = 'code'
# The destination for the generated html.
DOC_SOURCE = 'sphinx'
# The docuemntation build sources.
HTML_DESTINATION = '../doc/html'
# The destination for the builded HTML.
ARGS_BUILD = ('', CODE_DESTINATION, '--full' , '-o', DOC_SOURCE, '-H', 'ally-py', '-A', 'Gabriel Nistor',
              '-V', '1.0b1')
# The arguments used for building the sphinx resources.
ARGS_HTML = ('', '-b', 'html', '-d', os.path.join(DOC_SOURCE, '_build/doctrees'), '-D', 'latex_paper_size=a4',
             DOC_SOURCE, HTML_DESTINATION)
# The arguments for building the HTML.

findLibraries = lambda folder: (os.path.join(folder, name) for name in os.listdir(folder))
# Finds all the libraries (that have extension .egg) if the provided folder.

# --------------------------------------------------------------------

if __name__ == '__main__':
    # First we need to set the working directory relative to the application deployer just in case the application is
    # started from somewhere else
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    for src in CODE_SOURCES:
        for proj in os.listdir(src):
            path = os.path.join(src, proj)
            if os.path.isdir(path) and any(os.path.exists(os.path.join(path, mark)) for mark in MARK_PACKAGE):
                copy_tree(path, CODE_DESTINATION)
    
    for remove in REMOVE:
        path = os.path.join(CODE_DESTINATION, remove)
        if os.path.exists(path):
            if os.path.isdir(path): rmtree(path)
            else: os.remove(path)

    # Loading the libraries.
    for path in findLibraries('libraries'):
        if path not in sys.path: sys.path.append(path)

    from sphinx import apidoc
    apidoc.main(list(ARGS_BUILD))
    
    # Loading the libraries.
    for path in findLibraries('../distribution/libraries'):
        if path not in sys.path: sys.path.append(path)
    sys.path.append(os.path.abspath(CODE_DESTINATION))

    import sphinx
    sphinx.main(list(ARGS_HTML))
    
    rmtree(CODE_DESTINATION)
    rmtree(DOC_SOURCE)
