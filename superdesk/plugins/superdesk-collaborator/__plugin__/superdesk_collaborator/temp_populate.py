'''
Created on May 3, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Populates sample data for the services.
'''

from __plugin__.superdesk.db_superdesk import createTables
from __plugin__.superdesk_source.temp_populate import getSourcesIds
from ally.container import ioc
from ally.container.support import entityFor
from superdesk.collaborator.api.collaborator import ICollaboratorService, \
    Collaborator
from superdesk.person.api.person import IPersonService, QPerson, Person

# --------------------------------------------------------------------

PERSONS = {
           'Billy': ('Balaceanu', 'Gruia'),
           'Jey': ('Mihai', 'Floresti'),
           'Mugurel': ('Doe', 'Sporilor'),
           }

_cache_persons = {}
def getPersonsIds():
    personService = entityFor(IPersonService)
    assert isinstance(personService, IPersonService)
    if not _cache_persons:
        persons = _cache_persons
        for name in PERSONS:
            prsns = personService.getAll(q=QPerson(firstName=name))
            if prsns: persons[name] = next(iter(prsns)).Id
            else:
                prsn = Person()
                prsn.FirstName = name
                prsn.LastName, prsn.Address = PERSONS[name]
                persons[name] = personService.insert(prsn)
    return _cache_persons

COLLABORATORS = {
                 'Billy': 'google',
                 'Jey': 'google',
                 'Mugurel': 'facebook',
                 'google': 'google',
                 }

_cache_collaborators = {}
def getCollaboratorsIds():
    collaboratorService = entityFor(ICollaboratorService)
    assert isinstance(collaboratorService, ICollaboratorService)
    if not _cache_collaborators:
        collaborators = _cache_collaborators
        for name in COLLABORATORS:
            colls = collaboratorService.getAll(qp=QPerson(firstName=name))
            if colls: collaborators[name] = colls[0].Id
            else:
                coll = Collaborator()
                try: coll.Person = getPersonsIds()[name]
                except KeyError: pass
                coll.Source = getSourcesIds()[COLLABORATORS[name]]
                collaborators[name] = collaboratorService.insert(coll)
    return _cache_collaborators

# --------------------------------------------------------------------

@ioc.after(createTables)
def populate():
    getCollaboratorsIds()
