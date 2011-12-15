'''
Created on Aug 10, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods for parameters handling.
'''

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
