# This is required in order to allow the extension of this package.
import __main__
try: extend = getattr(__main__, 'deployExtendPackage')
except AttributeError: import deploy; extend = __main__.deployExtendPackage = deploy.deployExtendPackage

extend()
