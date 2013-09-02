define([
	'angular',
    'angular-resource',
    'lib/livedesk/scripts/js/manage-feeds/manage-feeds'
	],function(ngular, ngularRsrc, feeds){
		feeds.factory('chainedBlogsData', function($http, $q){
            return {
                getData: function(providersUrl) {
                    var deffered = $q.defer();
                    var myData = {};
                    $http({method: 'GET', url: providersUrl}).
                    success(function(data, status, headers, config) {
                        var sourceList = data.SourceList;
                        var sourceListCount = sourceList.length;
                        for ( var i = 0; i < sourceList.length; i++ ) {
                            var source = sourceList[i];
                            var infoUri = source.URI.href + '?X-Filter=Title,Description';
                            $http({method: 'GET', url: infoUri, 'data': {index: i}}).
                            success(function(data, status, headers, config) {
                                var index = config.data.index;
                                sourceList[index].blogList = data.BlogList;
                                sourceListCount --;
                                if ( sourceListCount == 0) {
                                    deffered.resolve(sourceList);
                                }
                            });
                        }
                    });
                    return deffered.promise;
                }
            }
        });
});