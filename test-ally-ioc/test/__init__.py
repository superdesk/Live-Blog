# This is required in order to allow the extension of this package.
try: from __main__ import deployExtendPackage
except ImportError:
    import __main__
    from . import extender
    __main__.deployExtendPackage = extender.deployExtendPackage
else: deployExtendPackage()