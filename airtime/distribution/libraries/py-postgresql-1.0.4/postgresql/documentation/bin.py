##
# .documentation.bin
##
__doc__ = open(__file__[:__file__.rfind('.')] + '.txt').read()
__docformat__ = 'reStructuredText'
if __name__ == '__main__':
	help(__name__)
