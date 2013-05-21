'''
Created on Dec 21, 2012

@author: chupy
'''
# --------------------------------------------------------------------

class A:
    
    def keys(self):
        print('keys')
        return ('1', '2')
    
    def __getitem__(self, key):
        print('__getitem__')
        return None

if __name__ == '__main__':
    print('loasasDsfdksd'.title())
