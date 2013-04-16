'''
Created on Feb 18, 2013

@package: ally base
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing report implementations.
'''

from .spec import IReport, Resolvers, IResolver

# --------------------------------------------------------------------

class ReportUnused(IReport):
    '''
    Implementation for @see: IReport that reports the unused attributes resolvers.
    '''
    __slots__ = ('_reports', '_resolvers')
    
    def __init__(self):
        '''
        Construct the report.
        '''
        self._reports = {}
        self._resolvers = []
        
    def open(self, name):
        '''
        @see: IReport.open
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        report = self._reports.get(name)
        if not report: report = self._reports[name] = ReportUnused()
        return report
        
    def add(self, resolvers):
        '''
        @see: IReport.add
        '''
        assert isinstance(resolvers, Resolvers), 'Invalid resolvers %s' % resolvers
        self._resolvers.append(resolvers)
        
    def report(self):
        '''
        Creates the report lines.
        
        @return: list[string]
            The list of string lines.
        '''
        st, reported = [], set()
        for resolvers in self._resolvers:
            assert isinstance(resolvers, Resolvers)
            for key, resolver in resolvers.iterate():
                assert isinstance(resolver, IResolver)
                if not resolver.isUsed():
                    if key not in reported:
                        reported.add(key)
                        st.append(('%s.%s for %s' % (key + (resolver,))).strip())
        if st: st.insert(0, 'Unused attributes:')
            
        for name, report in self._reports.items():
            assert isinstance(report, ReportUnused)
            lines = report.report()
            if lines:
                st.append('Report on %s:' % name)
                st.extend('\t%s' % line for line in lines)
        return st
