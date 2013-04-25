from __plugin__.gui_core.gui_core import publishGui, publish

@publish
def publishJS():
    publishGui('superdesk-desk')
