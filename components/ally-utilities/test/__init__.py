# Required in order to register the package extender whenever the unit test is run.
try:
    import deploy
    deploy.registerPackageExtender()
except ImportError: pass
