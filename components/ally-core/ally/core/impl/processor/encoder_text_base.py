'''
Created on Jan 25, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the text base encoder processor handler.
'''

from ally.container.ioc import injected
from ally.core.spec.resources import Converter
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain, \
    EncoderPath
from io import TextIOWrapper
from numbers import Number
import abc
import codecs
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class EncodingTextBaseHandler(Processor):
    '''
    Provides the text base encoding.
    
    Provides on request: NA
    Provides on response: the content response
    
    Requires on request: NA
    Requires on response: contentType, encoderPath, contentConverter, obj, [objMeta]
    '''
    
    charSetDefault = str
    # The default character set to be used if none provided for the content.
    contentTypes = dict
    # The dictionary{string:string} containing as a key the content types specific for this encoder and as a value
    # the content type to set on the response, if None will use the key for the content type response. 
    encodingError = str
    # The encoding error resolving.

    def __init__(self):
        assert isinstance(self.charSetDefault, str), 'Invalid default character set %s' % self.charSetDefault
        assert isinstance(self.contentTypes, dict), 'Invalid content types %s' % self.contentTypes
        assert isinstance(self.encodingError, str), 'Invalid string %s' % self.encodingError
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        # Check if the response is for this encoder
        if rsp.contentType not in self.contentTypes:
            assert log.debug('The content type %r is not for this %s encoder', rsp.contentType, self) or True
        elif not rsp.contentConverter:
            assert log.debug('The response has no content converter, not for this %s encoder', self) or True
        elif not rsp.encoderPath:
            assert log.debug('There is no path encoder on the response, not for this %s encoder', self) or True
        else:
            contentType = self.contentTypes[rsp.contentType]
            if contentType:
                assert log.debug('Normalized content type %r to %r', rsp.contentType, contentType) or True
                rsp.contentType = contentType
            
            # Handling the encoder and converter
            assert isinstance(rsp.contentConverter, Converter), 'Invalid content converter %s' % rsp.contentConverter
            assert isinstance(rsp.encoderPath, EncoderPath), 'Invalid encoder path %s' % rsp.encoderPath
            
            # Resolving the character set
            if rsp.charSet:
                try: codecs.lookup(rsp.charSet)
                except LookupError: rsp.charSet = None
            if not rsp.charSet:
                for charSet in req.accCharSets:
                    try: codecs.lookup(charSet)
                    except LookupError: continue
                    rsp.charSet = charSet
                    break
                else: rsp.charSet = self.charSetDefault
            
            def openTextWriter(): return TextIOWrapper(rsp.dispatch(), rsp.charSet, self.encodingError)
            
            if not rsp.objMeta:
                if rsp.obj is None:
                    assert log.debug('Nothing to encode') or True
                    return
                elif isinstance(rsp.obj, dict):
                    # Expected a plain dictionary dictionary or list for rendering
                    assert isValid(rsp.obj), 'Invalid object for encoding %s' % rsp.obj
                    
                    self.encodeObject(openTextWriter, rsp.charSet, rsp.obj)
                    return
                else:
                    assert log.debug('There is no meta object or valid object on the response, not for this %s encoder',
                                     self) or True
            else:
                self.encodeMeta(openTextWriter, rsp.charSet, rsp.obj, rsp.objMeta, rsp.contentConverter.asString,
                                rsp.encoderPath.encode)
                return
        
        chain.proceed()
    
    # ----------------------------------------------------------------
    
    @abc.abstractclassmethod
    def encodeMeta(self, openTextWriter, charSet, value, meta, asString, pathEncode):
        '''
        Encodes the provided value to a text object based on the  meta data.
        
        @param openTextWriter: Callable
            A callable function that will open the writer for the encoded text.
        @param charSet: string
            A character set encoding.
        @param value: object
            The value object to be encoded.
        @param meta: object meta
            The data meta of the object to encoded.
        @param asString: Callable
            The call used converting values to string values.
        @param pathEncode: Callable
            The call used for encoding the path.
        '''
        
    @abc.abstractclassmethod
    def encodeObject(self, openTextWriter, charSet, obj):
        '''
        Encodes the provided object to a text object based on the  meta data.
        
        @param openTextWriter: Callable
            A callable function that will open the writer for the encoded text.
        @param charSet: string
            A character set encoding.
        @param object: dictionary{string, ...}
            The object to be encoded.
        '''
        
# --------------------------------------------------------------------

def isValid(obj):
    '''
    Checks if the provided object is valid as a text object.
    
    @param obj: dictionary(string, string|list[string]|dictionary{string, ...}}
        The object to be checked.
    @return: boolean
        true if the object is valid, False otherwise.
    '''
    if not isinstance(obj, dict): return False
    for key, value in obj.items():
        if not isinstance(key, (str, Number)): return False
        if isinstance(value, list):
            for ele in value:
                if not isinstance(ele, (str, Number)) and not isValid(ele): return False
        elif not isinstance(value, (str, Number)) and not isValid(value) :return False
    return True

