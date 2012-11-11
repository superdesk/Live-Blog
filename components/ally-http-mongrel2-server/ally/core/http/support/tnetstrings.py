'''
Created on Nov 23, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for handling bytes for tnetstrings, this is made based on the mongrel2.tnetstrings module.
'''

# Note this implementation is more strict than necessary to demonstrate
# minimum restrictions on types allowed in dictionaries.

def parse(data):
    payload, payload_type, remain = parse_payload(data)

    if payload_type == b'#':
        value = int(payload)
    elif payload_type == b'}':
        value = parse_dict(payload)
    elif payload_type == b']':
        value = parse_list(payload)
    elif payload_type == b'!':
        value = payload == b'true'
    elif payload_type == b'^':
        value = float(payload)
    elif payload_type == b'~':
        assert len(payload) == 0, 'Payload must be 0 length for null.'
        value = None
    elif payload_type == b',':
        value = payload
    else:
        assert False, 'Invalid payload type: %r' % payload_type

    return value, remain

def parse_payload(data):
    assert data, "Invalid data to parse, it's empty."
    length, extra = data.split(b':', 1)
    length = int(length)

    payload, extra = extra[:length], extra[length:]
    assert extra, 'No payload type: %r, %r' % (payload, extra)
    payload_type, remain = extra[:1], extra[1:]

    assert len(payload) == length, 'Data is wrong length %d vs %d' % (length, len(payload))
    return payload, payload_type, remain

def parse_list(data):
    if len(data) == 0: return []

    result = []
    value, extra = parse(data)
    result.append(value)

    while extra:
        value, extra = parse(extra)
        result.append(value)

    return result

def parse_pair(data):
    key, extra = parse(data)
    assert extra, 'Unbalanced dictionary store.'
    value, extra = parse(extra)

    return key, value, extra

def parse_dict(data):
    if len(data) == 0: return {}

    key, value, extra = parse_pair(data)
    assert isinstance(key, (str, bytes)), 'Keys can only be strings.'

    result = {key: value}

    while extra:
        key, value, extra = parse_pair(extra)
        result[key] = value
  
    return result
