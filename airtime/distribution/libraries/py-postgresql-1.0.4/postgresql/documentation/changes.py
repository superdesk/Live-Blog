##
# .documentation.changes
##
from .. import project
# It's a bit lame, but let's not get too fancy.
bid = '.'.join(project.version_info[0:1])
__doc__ = open(__file__[:__file__.rfind('.')] + '-v' + bid + '.txt').read()
__docformat__ = 'reStructuredText'
if __name__ == '__main__':
	help(__name__)
