'''
Created on Sep 29, 2011

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides an XML digester used for parsing XML files by using a SAX parser.
'''

from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from xml.sax.xmlreader import InputSource
from xml.sax._exceptions import SAXParseException
from xml.sax.saxutils import XMLGenerator
from collections import deque

# --------------------------------------------------------------------

class DigesterError(Exception):
    '''
    Error raised whenever there is a xml digester problem.
    '''

# --------------------------------------------------------------------

class Digester(ContentHandler):
    '''
    Provides a digester for XML.
    '''

    def __init__(self, root, acceptAttributes=True, acceptUnknownTags=True):
        '''
        @param root: Node
            The root node.
        @param acceptAttributes: boolean
            If True will allow attributes on the tags if False will throw exception when encountering an
            attribute.
        @ivar stack: list
            The stack that contains the values in the digester.
        @ivar errors: list
            The generated errors from parsing.
        '''
        assert isinstance(root, Node), 'Invalid root node %s' % root
        assert isinstance(acceptAttributes, bool), 'Invalid accept attributes flag %s' % acceptAttributes
        assert isinstance(acceptUnknownTags, bool), 'Invalid accept unknown tags flag %s' % acceptUnknownTags
        self.root = root
        self.acceptAttributes = acceptAttributes
        self.acceptUnknownTags = acceptUnknownTags

        self.stack = []
        self.errors = []
        self._parser = make_parser()
        self._parser.setContentHandler(self)

    def parse(self, charSet, file):
        '''
        Parses the provided content.
        
        @param charSet: string
            The character set of the content.
        @param file: byte file
            The bytes file object providing the content.
        @return: object
            The object obtained from parsing.
        '''
        inpsrc = InputSource()
        inpsrc.setByteStream(file)
        inpsrc.setEncoding(charSet)
        return self.parseInputSource(inpsrc)

    def parseInputSource(self, source):
        '''
        Parses the provided input source.
        
        @param source: InputSource
            The input source providing the content.
        @return: object
            The object obtained from parsing.
        '''
        assert isinstance(source, InputSource), 'Invalid input source %s' % source
        del self.errors[:]
        self._nodes = [self.root]
        try:
            self._parser.parse(source)
        except SAXParseException as e:
            assert isinstance(e, SAXParseException)
            raise DigesterError('Bad XML content at line %s and column %s' % (e.getLineNumber(), e.getColumnNumber()))
        if not self.stack: raise DigesterError('Invalid XML content provided, cannot find root tag')
        return self.stack[0]

    def currentName(self):
        '''
        Provides the current processing name of the digester.
        '''
        node = self._currentNode()
        return node.name if node else None

    def currentPath(self):
        '''
        Provides the current processing path of the digester.
        '''
        elements = deque()
        for i in range(1, len(self._nodes)):
            node = self._nodes[i]
            if isinstance(node, Node): elements.append(node.name)
            else: elements.append(node)
        return '/'.join(elements)

    def startElement(self, name, attributes):
        '''
        @see: ContentHandler.startElement
        '''
        if not self.acceptAttributes and len(attributes) > 0:
            raise DigesterError('No attributes accepted for path %r at line %s and column %s' % 
                                (self.currentPath(), self.getLineNumber(), self.getColumnNumber()))
        node = self._pushName(name)
        if not self.acceptUnknownTags and not node:
            raise DigesterError('Unknown path element %r in %r at line %s and column %s' % 
                                (name, self.currentPath(), self.getLineNumber(), self.getColumnNumber()))

        self._processBegin(node, name, attributes)

    def characters(self, content):
        '''
        @see: ContentHandler.characters
        '''
        self._processContent(self._currentNode(), content)

    def endElement(self, name):
        '''
        @see: ContentHandler.endElement
        '''
        self._processEnd(self._popNodes(name), name)

    def getLineNumber(self):
        return self._parser.getLineNumber()

    def getColumnNumber(self):
        return self._parser.getColumnNumber()

    def _pushName(self, name):
        '''
        Called to push a tag name in the node stack and also to provide the node for the path.
        
        @param name: string
            The name to push.
        @return: Node|None
            The node corresponding to the path that has been pushed or None if there is no Node.
        '''
        node = self._nodes[-1]
        if isinstance(node, Node):
            child = node.childrens.get(name)
            if child:
                self._nodes.append(child)
                return child
        self._nodes.append(name)

    def _currentNode(self):
        '''
        Provides the current Node.
        
        @return: Node|None
            The current Node or None if there is no current Node.
        '''
        node = self._nodes[-1]
        if isinstance(node, Node):
            return node

    def _popNodes(self, name):
        '''
        Pops all the nodes until the provided path is encountered.
        
        @param name: string
            The name to which to pop all nodes.
        @return: list[Node]
            A list with all the nodes poped.
        '''
        for k, node in enumerate(reversed(self._nodes)):
            found = False
            if isinstance(node, Node):
                assert isinstance(node, Node)
                found = node.name == name
            else: found = node == name
            if found:
                nodes = self._nodes[-(k + 1):]
                del self._nodes[-(k + 1):]
                break
        else:
            raise DigesterError('Unexpected end element %r at line %s and column %s' % 
                                (name, self.getLineNumber(), self.getColumnNumber()))

        return [node for node in reversed(nodes) if isinstance(node, Node)]

    def _processBegin(self, node, name, attributes):
        '''
        Process the begin for the provided node.
        
        @param node: Node|None
            The node that is to be processed.
        @param path: string
            The path that is started.
        @param attributes: dictionary
            The attributes of the element.
        @return: boolean
            True if there has been any processing (meaning that at least a rule has been invoked), False otherwise.
        '''
        processed = False
        if node:
            assert isinstance(node, Node)
            for rule in node.rules:
                assert isinstance(rule, Rule)
                rule.begin(self, **attributes)
                processed |= True
        return processed

    def _processContent(self, node, content):
        '''
        Process the content for the provided node.
        
        @param node: Node|None
            The node that is to be processed.
        @param path: string
            The path that is ended.
        @return: boolean
            True if there has been any processing (meaning that at least a rule has been invoked), False otherwise.
        '''
        processed = False
        if node:
            assert isinstance(node, Node)
            for rule in node.rules:
                assert isinstance(rule, Rule)
                rule.content(self, content)
                processed |= True
        return processed

    def _processEnd(self, nodes, name):
        '''
        Process the end for the provided nodes.
        
        @param node: list[Node]
            A list with the nodes to be processed.
        @param name: string
            The name to be processed.
        @return: boolean
            True if there has been any processing (meaning that at least a rule has been invoked), False otherwise.
        '''
        processed = False
        if nodes:
            for node in nodes:
                assert isinstance(node, Node)
                for rule in reversed(node.rules):
                    assert isinstance(rule, Rule)
                    rule.end(node, self)
                    processed |= True
        return processed

class DigesterXMLUpdate(Digester, XMLGenerator):
    '''
    A digester extension to be used in updating the XML files. If there are rules for a certain path than the rule
    has to call the XMLGenerator for rendering that tag, otherwise all elements that do not have a rule will get
    rendered. Attention the digester will not close the provided output.
    '''

    def __init__(self, root, out, encoding='UTF-8', acceptAttributes=True, acceptUnknownTags=True,
                 shortEmptyElements=True):
        '''
        @param out: file object with write
            The file object to write the updated xml, needs to have a 'write' method that accepts text.
            
        @see: Digester.__init__
        @see: XMLGenerator.__init__
        '''
        XMLGenerator.__init__(self, out, encoding, shortEmptyElements)
        Digester.__init__(self, root, acceptAttributes, acceptUnknownTags)

    def parse(self, charSet, file):
        '''
        @see: Digester.parse
        '''
        return Digester.parse(self, charSet, file)

    def _processBegin(self, node, name, attributes):
        '''
        @see: Digester._processBegin
        '''
        if not Digester._processBegin(self, node, name, attributes):
            XMLGenerator.startElement(self, name, attributes)

    def _processContent(self, node, content):
        '''
        @see: Digester._processContent
        '''
        if not Digester._processContent(self, node, content):
            XMLGenerator.characters(self, content)

    def _processEnd(self, nodes, name):
        '''
        @see: Digester._processEnd
        '''
        if not Digester._processEnd(self, nodes, name):
            XMLGenerator.endElement(self, name)

# --------------------------------------------------------------------

class Node:
    '''
    Defines a node of rules that contain the rule of the node and the childrens.
    '''

    def __init__(self, name):
        '''
        @param name: string
            The element name of the node.
        @ivar rules: list
            Contains the rules of the node.
        @ivar childrens: dictionary
            Contains all the children Nodes, as a key is the path element that describes the node.
        '''
        assert isinstance(name, str), 'Invalid node name %s' % name
        self.name = name
        self.rules = []
        self.childrens = {}

    def addRule(self, rule, *xpaths):
        '''
        Add a rule to this node.
        
        @param rule: Rule
            The rule to be added.
        @param xpaths: tuple
            A tuple of string containing the xpath of the rule.
        @return: Node
            The node of the added rule.
        '''
        assert isinstance(rule, Rule), 'Invalid rule %s' % rule
        paths = deque()
        for path in xpaths:
            assert isinstance(path, str), 'Invalid path element %s' % path
            paths.extend(path.split('/'))
        node = self.obtainNode(paths)
        node.rules.append(rule)
        return node

    def obtainNode(self, xpaths):
        '''
        Obtains the node for the specified xpaths list.
        
        @param xpaths: deque(string)
            The xpaths list to be searched.
        '''
        assert isinstance(xpaths, deque), 'Invalid xpaths %s' % xpaths

        node = self
        while xpaths:
            xpath = xpaths.popleft()
            for path, child in node.childrens.items():
                if path == xpath:
                    node = child
                    break
            else:
                child = node.childrens[xpath] = Node(xpath)
                node = child
        return node

class RuleRoot(Node):
    '''
    Provides a root node.
    '''

    def __init__(self):
        super().__init__('ROOT')

class Rule:
    '''
    Provides the parser rule base.
    '''

    def begin(self, digester, **attributes):
        '''
        Called at element start.
        
        @param digester: Digester
            The processing digester.
        @param attributes: key arguments
            The attributes for the tag if the digester allows them.
        '''

    def content(self, digester, content):
        '''
        Called when the element has character data content.
        
        @param digester: Digester
            The processing digester.
        @param content: string
            The content of the element.
        '''

    def end(self, node, digester):
        '''
        Called at element end.
        
        @param node: Node
            The node containing the rule.
        @param digester: Digester
            The processing digester.
        '''

# --------------------------------------------------------------------

class RuleXMLUpdate(Rule):
    '''
    Rule extension that just delivers the event to the digester XML generator. Used for inheriting whenever you 
    only need to modify like the begin of the rule but the content and end should be propagated.
    '''

    def begin(self, digester, **attributes):
        '''
        @see: Rule.begin
        '''
        assert isinstance(digester, DigesterXMLUpdate), 'Invalid digester %s' % digester
        XMLGenerator.startElement(digester, digester.currentName(), attributes)

    def content(self, digester, content):
        '''
        @see: Rule.content
        '''
        assert isinstance(digester, DigesterXMLUpdate), 'Invalid digester %s' % digester
        XMLGenerator.characters(digester, content)

    def end(self, node, digester):
        '''
        @see: Rule.end
        '''
        assert isinstance(digester, DigesterXMLUpdate), 'Invalid digester %s' % digester
        XMLGenerator.endElement(digester, node.name)

class RuleXMLWrapUpdate(RuleXMLUpdate):
    '''
    Rule extension that just delivers the event to the digester XML generator and also notifies a wrapped rule of the
    triggers.
    '''

    def __init__(self, wrapped):
        '''
        @param wrapped: Rule
            The rule to be wrapped.
        '''
        assert isinstance(wrapped, Rule), 'Invalid wrapping rule %s' % wrapped
        self.wrapped = wrapped

    def begin(self, digester, **attributes):
        '''
        @see: Rule.begin
        '''
        super().begin(digester, **attributes)
        self.wrapped.begin(digester, **attributes)

    def content(self, digester, content):
        '''
        @see: Rule.content
        '''
        super().content(digester, content)
        self.wrapped.content(digester, content)

    def end(self, node, digester):
        '''
        @see: Rule.end
        '''
        super().end(node, digester)
        self.wrapped.end(node, digester)
