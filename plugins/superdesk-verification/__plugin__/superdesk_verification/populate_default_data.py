'''
Created on Oct 8, 2013

@package: superdesk verification
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Populates default data for the services.
'''

from ally.container import app, ioc
from ..superdesk.db_superdesk import alchemySessionCreator
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import exists
from superdesk.verification.meta.status import VerificationStatusMapped

# --------------------------------------------------------------------

def createVerificationStatus(key):
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)

    if not session.query(exists().where(VerificationStatusMapped.Key == key)).scalar():
        verificationStatus = VerificationStatusMapped()
        verificationStatus.Key = key
        session.add(verificationStatus)

    session.commit()
    session.close()

@app.populate(priority=ioc.PRIORITY_FIRST)
def populateVeridicationStatuses():
    createVerificationStatus('verified')
<<<<<<< HEAD
    createVerificationStatus('nostatus')
    createVerificationStatus('onverification')
=======
    createVerificationStatus('on verification')
    createVerificationStatus('no verification info')
>>>>>>> 4d49bcc09513d2bb06041f30e41a8e7ce2d74ffe
    createVerificationStatus('unverified') 
