'''
Created on Feb 21, 2013

@package: gateway
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Processor that adds default Gateway objects.
'''

from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.design.processor.attribute import defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed, Handler
from collections import Iterable
from gateway.api.gateway import Gateway
from itertools import chain

# --------------------------------------------------------------------

class Reply(Context):
    '''
    The reply context.
    '''
    # ---------------------------------------------------------------- Defined
    gateways = defines(Iterable, doc='''
    @rtype: Iterable(Gateway)
    The default gateways.
    ''')

# --------------------------------------------------------------------

@injected
@setup(Handler, name='registerDefaultGateways')
class RegisterDefaultGateways(HandlerProcessorProceed):
    '''
    Provides the handler that populates default gateways.
    '''
    
    default_gateways = []; wire.config('default_gateways', doc='''
    The default gateways that are available for any unauthorized access. This is a list of dictionaries that are allowed
    the following keys:
        Pattern -   a string value:
                    contains the regex that needs to match with the requested URI. The pattern needs to produce, if is the
                    case, capturing groups that can be used by the Filters or Navigate.
        Headers -   a list of strings:
                    the headers to be filtered in order to validate the navigation. Even though this might look specific for
                    http they actually can be used for any meta data that accompanies a request, it depends mostly on the
                    gateway interpretation. The headers are provided as regexes that need to be matched. In case of headers
                    that are paired as name and value the regex will receive the matching string as 'Name:Value', the name
                    is not allowed to contain ':'. At least one header needs to match to consider the navigation valid.
        Methods -   a list of strings:
                    the list of allowed methods for the request, if no method is provided then all methods are considered
                    valid. At least one method needs to match to consider the navigation valid.
        Filters -   a list of strings:
                    contains a list of URIs that need to be called in order to allow the gateway Navigate. The filters are
                    allowed to have place holders of form '{1}' or '{2}' ... '{n}' where n is the number of groups obtained
                    from the Pattern, the place holders will be replaced with their respective group value. All filters
                    need to return a True value in order to allow the gateway Navigate.
        Errors -    a list of integers:
                    the list of errors codes that are considered to be handled by this Gateway entry, if no error is provided
                    then it means the entry is not solving any error navigation. At least one error needs to match in order
                    to consider the navigation valid.
        Host -      a string value:
                    the host where the request needs to be resolved, if not provided the request will be delegated to the
                    default host.
        Protocol -  a string value:
                    the protocol to be used in the communication with the server that handles the request, if not provided
                    the request will be delegated using the default protocol.
        Navigate -  a string value:
                    a pattern like string of forms like '*', 'resources/*' or 'redirect/Model/{1}'. The pattern is allowed to
                    have place holders and also the '*' which stands for the actual called URI, also parameters are allowed
                    for navigate URI, the parameters will override the actual parameters.
        PutHeaders -The headers to be put on the forwarded requests. The values are provided as 'Name:Value', the name is
                    not allowed to contain ':'.
    ''')
    
    def __init__(self):
        '''
        Construct the default gateways register.
        '''
        assert isinstance(self.default_gateways, list), 'Invalid default gateways %s' % self.default_gateways
        super().__init__()
        
        self._gateways = []
        for config in self.default_gateways: self._gateways.append(gatewayFrom(config))
    
    def process(self, reply:Reply, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Adds the default gateways.
        '''
        assert isinstance(reply, Reply), 'Invalid reply %s' % reply

        if reply.gateways is not None: reply.gateways = chain(self._gateways, reply.gateways)
        else: reply.gateways = self._gateways

# --------------------------------------------------------------------

def gatewayFrom(config):
    '''
    Constructs a gateway from the provided configuration dictionary.
    
    @param config: dictionary{string, ...}
        The configurations dictionary to construct the gateway based on.
    @return: Gateway
        The constructed gateway.
    '''
    assert isinstance(config, dict), 'Invalid gateway configuration %s' % config
    if __debug__: keys = set()
    gateway = Gateway()
    for key in ('Pattern', 'Headers', 'Methods', 'Filters', 'Errors', 'Host', 'Protocol', 'Navigate'):
        value = config.get(key)
        if value is not None:
            if __debug__:
                if key == 'Pattern': assert isinstance(value, str), 'Invalid Pattern %s' % value
                elif key == 'Headers':
                    assert isinstance(value, list), 'Invalid Headers %s' % value
                    for item in value: assert isinstance(item, str), 'Invalid Headers value %s' % item
                elif key == 'Methods':
                    assert isinstance(value, list), 'Invalid Methods %s' % value
                    for item in value: assert isinstance(item, str), 'Invalid Methods value %s' % item
                elif key == 'Filters':
                    assert isinstance(value, list), 'Invalid Filters %s' % value
                    for item in value: assert isinstance(item, str), 'Invalid Filters value %s' % item
                elif key == 'Errors':
                    assert isinstance(value, list), 'Invalid Errors %s' % value
                    for item in value: assert isinstance(item, int), 'Invalid Errors value %s' % item
                elif key == 'Host': assert isinstance(value, str), 'Invalid Host %s' % value
                elif key == 'Protocol': assert isinstance(value, str), 'Invalid Protocol %s' % value
                elif key == 'Navigate': assert isinstance(value, str), 'Invalid Navigate %s' % value
                elif key == 'PutHeaders':
                    assert isinstance(value, list), 'Invalid PutHeaders %s' % value
                    for item in value: assert isinstance(item, str), 'Invalid PutHeaders value %s' % item
                    
            setattr(gateway, key, value)
            assert keys.add(key) or True
            
    assert len(keys) == len(config), 'Invalid gateway configuration names: %s' % (', '.join(keys.difference(config)))
    return gateway
