'''
Created on Jan 26, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the text encoding for xml.
'''

from xml.sax.saxutils import XMLGenerator
from numbers import Number
from ally.exception import DevelException
from ally.container.ioc import injected

# --------------------------------------------------------------------

@injected
class XMLEncoder:
    '''
    The XML encoder.
    '''
    
    namePath = 'href'
    # The name to use as the attribute in rendering the hyper link.
    nameList = '%sList'
    # The name to use for rendering lists.
    
    def __init__(self):
        assert isinstance(self.namePath, str), 'Invalid name path %s' % self.namePath
        assert isinstance(self.nameList, str), 'Invalid name list %s' % self.nameList
        self._noAttrs = {}
        self._writers = [self.writeValue, self.writeReference, self.writeObject, self.writeList]
    
    def encode(self, obj, fwrite, charSet):
        '''
        Encode the provided text object into XML and write the XML to the fwrite.
        
        @param obj: dictionary{string, ...}
            The text object to convert to XML.
        @param fwrite: file write object
            The file write object to dump the XML to.
        @param charSet: string
            The character set to use in encoding.
        '''
        assert isinstance(obj, dict), 'Invalid text object %s' % obj
        assert fwrite is not None, 'A file write object is required'
        assert isinstance(charSet, str), 'Invalid character set %s' % charSet
        xml = XMLGenerator(fwrite, charSet, short_empty_elements=True)
        xml.startDocument()
        self.write(obj, xml)
        xml.endDocument()
        
    def write(self, obj, xml, name=None, nameList=None):
        '''
        Write any object to the XML generator.
        
        @param obj: object
            The text object to write.
        @param xml: XMLGenerator
            The XML to write to.
        @param name: string|None
            The name of the value object.
        @param nameList: string|None
            The name of the value object within a list, practically a lesser priority name.
        '''
        for writer in self._writers:
            if writer(obj, xml, name, nameList): break
        else:
            raise DevelException('Cannot encode object %s to XML' % obj)
        
    def writeObject(self, obj, xml, name=None, nameList=None):
        '''
        Write the object to the XML generator.
        
        @param obj: object
            The text object to write.
        @param xml: XMLGenerator
            The XML to write to.
        @param name: string|None
            The name of the value object.
        @param nameList: string|None
            The name of the value object within a list, practically a lesser priority name.
        @return: boolean
            True if the provided object was an object and was written, False|None otherwise.
        '''
        assert isinstance(xml, XMLGenerator), 'Invalid XML %s' % xml
        assert not name or isinstance(name, str), 'Invalid name %s' % name
        assert not nameList or isinstance(nameList, str), 'Invalid name list %s' % nameList
        if isinstance(obj, dict):
            if not name and nameList and len(obj) > 1: name = nameList
            if name: xml.startElement(name, {})
            for entryName, entryValue in obj.items(): self.write(entryValue, xml, entryName)
            if name: xml.endElement(name)
            return True
        
    def writeList(self, obj, xml, name=None, *args):
        '''
        Write the list to the XML generator.
        
        @param obj: object
            The text object to write.
        @param xml: XMLGenerator
            The XML to write to.
        @param name: string|None
            The name of the value object.
        @return: boolean
            True if the provided object was a list object and was written, False|None otherwise.
        '''
        if isinstance(obj, list):
            assert isinstance(name, str), 'Expected a name for the list %s' % obj
            nameList = self.nameList % name
            xml.startElement(nameList, {})
            for value in obj:
                self.write(value, xml, nameList=name)
            xml.endElement(nameList)
            return True
    
    def writeValue(self, obj, xml, name=None, nameList=None):
        '''
        Write a value object.
        
        @param obj: string|Number
            The text object of the value.
        @param xml: XMLGenerator
            The XML to write to.
        @param name: string|None
            The name of the value object.
        @param nameList: string|None
            The name of the value object within a list, practically a lesser priority name.
        @return: boolean
            True if the provided object was a value object and was written, False|None otherwise.
        '''
        assert isinstance(xml, XMLGenerator), 'Invalid XML %s' % xml
        assert not name or isinstance(name, str), 'Invalid name %s' % name
        assert not nameList or isinstance(nameList, str), 'Invalid name list %s' % nameList
        if isinstance(obj, (str, Number)):
            if not name and nameList: name = nameList
            if name: xml.startElement(name, {})
            xml.characters(obj)
            if name: xml.endElement(name)
            return True
        
    def writeReference(self, obj, xml, name=None, nameList=None):
        '''
        Write a reference object.
        
        @param obj: dictionary{string, ...}
            The text object of the reference.
        @param xml: XMLGenerator
            The XML to write to.
        @param name: string|None
            The name of the reference object.
        @param nameList: string|None
            The name of the value object within a list, practically a lesser priority name.
        @return: boolean
            True if the provided object was a reference object and was written, False|None otherwise.
        '''
        assert isinstance(xml, XMLGenerator), 'Invalid XML %s' % xml
        assert not name or isinstance(name, str), 'Invalid name %s' % name
        assert not nameList or isinstance(nameList, str), 'Invalid name list %s' % nameList
        if not isinstance(obj, dict): return False
        
        href = obj.get(self.namePath)
        if href:
            if len(obj) == 1:
                if not name and nameList: name = nameList
                if name: xml.startElement(name, {self.namePath:href})
                else:
                    name = self.namePath
                    xml.startElement(name, {})
                    xml.characters(href)
                xml.endElement(name)
            elif len(obj) == 2:
                items = iter(obj.items())
                nameEntry, valueEntry = next(items)
                if nameEntry == self.namePath: nameEntry, valueEntry = next(items)
                # We try to get the other name from the dictionary, so if is not the first entry key it will be 
                # the second
                if not name: name = nameEntry
                xml.startElement(name, {self.namePath:href})
                self.write(valueEntry, xml)
                xml.endElement(name)
            else:
                if not name and nameList: name = nameList
                if not name: raise DevelException('Expected a name for referenced object %s' % obj)
                xml.startElement(name, {self.namePath:href})
                for nameEntry, valueEntry in obj.items():
                    if nameEntry != self.namePath: self.write(valueEntry, xml, nameEntry)
                xml.endElement(name)
            return True
