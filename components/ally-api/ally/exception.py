'''
Created on May 31, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the exceptions that are used in communicating issues in the API.
The internal errors (the ones that are made by the implementation and not data) are AssertionError.
'''

from .api.operator import Model, Property
from .api.type import typeFor, TypeProperty, TypeModel

# --------------------------------------------------------------------

class DevelException(Exception):
    '''
    Wraps exceptions that are related to wrong development usage from the client.
    '''
    
    def __init__(self, message):
        assert isinstance(message, str), 'Invalid string message %s' % message
        self.message = message
        Exception.__init__(self, message)

# --------------------------------------------------------------------

class InputException(Exception):
    '''
    Wraps exceptions that are related to input data.
    '''
    
    def __init__(self, *message):
        '''
        Initializes the exception based on the message(s) which will be used as a key.
        
        @param message: arguments(String|Ref|InputException)
            The message(s) that compose this input exception.
        '''
        assert message, 'Expected at least one message'
        self.message = []
        for msg in message:
            if isinstance(msg, InputException):
                self.message.extend(msg.message)
            else:
                if isinstance(msg, Ref): self.message.append(msg)
                else:
                    assert isinstance(msg, str), 'Invalid message %s' % msg
                    self.message.append(Ref(msg))
        meses = []
        for msg in self.message:
            mes = '('
            if msg.model:
                mes += msg.model
                if msg.property: mes += '.' + msg.property
                mes += '='
            mes += '\'' + msg.message + '\')'
            meses.append(mes)
        Exception.__init__(self, ', '.join(meses))

# --------------------------------------------------------------------

class Ref:
    '''
    Maps a reference for an exception message.
    '''
    
    def __init__(self, message, model=None, property=None, ref=None):
        '''
        Provides a wrapping of the message which will be used as a key.
        
        @param message: string
            A message to be referenced.
        @param model: string|None 
            The model associated with the message.
        @param property: string|None 
            The property associated with the message.
        @param ref: TypeProperty|TypeModel|None 
            The property type associated with the message.
        '''
        assert isinstance(message, str), 'Invalid message %s' % message
        assert not model or isinstance(model, Model), 'Invalid model %s' % model
        assert not property or isinstance(property, Property), 'Invalid property %s' % property
        if ref:
            typ = typeFor(ref)
            if isinstance(typ, TypeProperty):
                model = typ.model
                property = typ.property
            elif isinstance(typ, TypeModel):
                model = typ.model
            else:
                raise AssertionError('Invalid reference %s, cannot extract any type' % ref)
        self.message = message
        self.model = model.name if model is not None else None
        self.property = property.name if property is not None else None
