'''
Created on Aug 10, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods for parameters handling.
'''
from urllib.parse import unquote
from re import compile

# --------------------------------------------------------------------

def containsParam(params, name):
    '''
    Checks if the parameters contain an entry with the provided name.
    
    @param params: list[tuple(string, string)]
        The list of parameters.
    @param name: string 
        The name of the parameter to check.
    @return: boolean
        True if name appears in the parameters, False otherwise.
    '''
    for param in params:
        if param[0] == name:
            return True
    return False

def extractParams(params, *names):
    '''
    Extracts all parameters with the provided names. Attention the provided params list will be updated by removing
    the extracted parameters.
    
    @param params: list[tuple(string, string)]
        The list of parameters.
    @param names: *arguments
        The names of the parameter to extract.
    @return: list[tuple(string, string)]
        The extracted parameters for the specified names.
    '''
    extracted = []
    k = 0
    while k < len(params):
        if params[k][0] in names:
            extracted.append(params[k])
            del params[k]
            k -= 1
        k += 1
    return extracted

def extractParamValues(params, name, splitComma=False):
    '''
    Extracts all parameter values with the provided name. Attention the provided params list will be updated by 
    removing the extracted parameters.
    
    @param params: list[tuple(string, string)]
        The list of parameters.
    @param name: string
        The name for which to extract the values.
    @param splitComma: boolean
        If true and the value contains a comma it will generate multiple entries of the parameter with the values
        split.
    @return: list[string]
        The extracted values for the specified name.
    '''
    values = []
    k = 0
    while k < len(params):
        pName, pValue = params[k]
        if pName == name:
            if splitComma:
                values.extend(pValue.split(','))
            else:
                values.append(pValue)
            del params[k]
            k -= 1
        k += 1
    return values

def parseStr(theString):
    '''
    php parse_str function port to python
    @see: http://php.net/parse_str
    @author: Mihai Balaceanu
    '''
    paramPairArray = theString.split('&')
    ret = {}
    
    for paramPair in paramPairArray:
        # split keys from values
        try:
            [key, value] = paramPair.split('=')
        except:
            [key, value] = [paramPair, None]
        value = unquote(value) if value is not None else value
        key = unquote(key).strip()
        
        # look for string end mark
        keyEnd = key.find('\0')
        if keyEnd != -1: key = key[:keyEnd]
        if not key: continue

        # match nested keys in parameter
        keys = compile(r'''(?<=\[)[^]]*(?=\])''').findall(key)
        keys[:0] = compile(r'''^([^[]+)''').findall(key)
        
        curRet = ret 
        keysLen = len(keys)
        for k in range(keysLen): #loop found keys in pairs to look for nested objects
            if keys[k].strip() == '': # matched at [] - means list entry
                if not isinstance(curRet, list): # previous is not already a list
                    curRet[keys[k-1]] = []
                    curRet = curRet[keys[k-1]]
                if keysLen-1 == k: # if last key in this iteration append value to list
                    curRet.append(value)
            else: # for dict 
                if not keys[k] in curRet: # init new key
                    if isinstance(curRet, list): # previous is list
                        curRet.append({ keys[k]: value if keysLen-1 == k else {}})
                        curRet = curRet[-1]
                    else: # append value to current dict
                        if keysLen-1 == k:
                            curRet[keys[k]] = value
                        elif keys[k+1].strip() == '': # next is a list [] - init accordingly 
                            curRet[keys[k]] = []
                        else:
                            curRet[keys[k]] = {} 
                        curRet = curRet[keys[k]]
                else:
                    curRet = curRet[keys[k]] # put pointer at the next key in tree
    return ret
