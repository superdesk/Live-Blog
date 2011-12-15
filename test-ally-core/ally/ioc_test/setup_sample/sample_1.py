'''
Created on Nov 25, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Test IoC setup sample.
'''

from ally.ioc_test.setup_sample.sample_2 import otherConfig

# --------------------------------------------------------------------

def person(config={
                   'name': 'Gabriel'
                   }):
    b = {config['name']}; yield b
    b['age'] = 29
    
def otherPerson():
    b = {otherConfig['name']}; yield b
    b['age'] = 31

def job(person):
    b = {'person':person}; yield b
    b['job'] = 'Developer'
