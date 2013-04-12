'''
Created on Apr 24, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Provides the x-www-form-urlencoded decoding 
'''

from urllib.parse import unquote
from re import compile

# --------------------------------------------------------------------

PARSE_RGEXES = (
                compile('\+'),
                compile('''(?<=\[)[^]]*(?=\])'''),
                compile(r'''^([^[]+)''')
                )

# --------------------------------------------------------------------

def parseStr(theString):
    '''
    php parse_str function port to python
    @see: http://php.net/parse_str
    @author: Mihai Balaceanu
    '''
    replace, keyFindNested, keyFind = PARSE_RGEXES

    paramPairArray, ret = theString.split('&'), {}
    for paramPair in paramPairArray:
        # split keys from values
        try:
            [key, value] = paramPair.split('=')
        except:
            [key, value] = [paramPair, None]

        value = unquote(replace.sub(' ', value)) if value is not None else value # also replace the + with space
        key = unquote(key).strip()

        # look for string end mark
        keyEnd = key.find('\0')
        if keyEnd != -1: key = key[:keyEnd]
        if not key: continue

        # match nested keys in parameter
        keys = keyFindNested.findall(key)
        keys[:0] = keyFind.findall(key)

        curRet = ret
        keysLen = len(keys)
        for k in range(keysLen): #loop found keys in pairs to look for nested objects
            if keys[k].strip() == '': # matched at [] - means list entry
                if not isinstance(curRet, list): # previous is not already a list
                    curRet[keys[k - 1]] = [] # lookbehind
                    curRet = curRet[keys[k - 1]]
                if keysLen - 1 == k: # if last key in this iteration append value to list
                    curRet.append(value)
            else: # for parsing as dict 
                if not keys[k] in curRet: # init new key
                    if isinstance(curRet, list): # previous is list
                        curRet.append({ keys[k]: value if keysLen - 1 == k else {}})
                        curRet = curRet[-1]
                    else: # append value to current dict
                        if keysLen - 1 == k:
                            curRet[keys[k]] = value
                        elif keys[k + 1].strip() == '': # lookahead - next is a list [], init accordingly 
                            curRet[keys[k]] = []
                        else:
                            curRet[keys[k]] = {}
                        curRet = curRet[keys[k]]
                else:
                    curRet = curRet[keys[k]] # put pointer at the next key in tree
    return ret
