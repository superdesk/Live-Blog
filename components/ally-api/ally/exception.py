'''
Created on May 31, 2011

@package: ally api
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the exceptions that are used in communicating issues in the API.
The internal errors (the ones that are made by the implementation and not data) are Exception.
'''

from .api.operator.container import Model
from .api.operator.type import TypeModelProperty, TypeModel
from .api.type import typeFor

# --------------------------------------------------------------------

class DevelError(Exception):
    '''
    Wraps exceptions that are related to wrong development usage.
    '''

    def __init__(self, message):
        assert isinstance(message, str), 'Invalid string message %s' % message
        self.message = message
        Exception.__init__(self, message)

# --------------------------------------------------------------------

class InputError(Exception):
    '''
    Wraps exceptions that are related to input data.
    '''

    def __init__(self, *message):
        '''
        Initializes the exception based on the message(s) which will be used as a key.
        
        @param message: arguments(String|Ref|InputError)
            The message(s) that compose this input exception.
        '''
        assert message, 'Expected at least one message'
        self.message = []
        for msg in message:
            if isinstance(msg, InputError):
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
        @param model: Model|None 
            The model associated with the message.
        @param property: string|None 
            The property associated with the message.
        @param ref: TypeModelProperty|TypeModel|None 
            The property type associated with the message.
        '''
        assert isinstance(message, str), 'Invalid message %s' % message
        assert not model or isinstance(model, Model), 'Invalid model %s' % model
        assert not property or isinstance(property, str), 'Invalid property %s' % property
        if ref:
            typ = typeFor(ref)
            if isinstance(typ, TypeModelProperty):
                assert isinstance(typ, TypeModelProperty)
                self.model = typ.container.name
                self.property = typ.property
            elif isinstance(typ, TypeModel):
                assert isinstance(typ, TypeModel)
                self.model = typ.container.name
                self.property = None
            else: raise Exception('Invalid reference %s, cannot extract any type' % ref)
        else:
            self.model = model.name if model else None
            self.property = property
        self.message = message
