define([
	'angular',
    'lib/livedesk/scripts/js/manage-feeds/manage-feeds'
	],function(ngular, feeds){
		feeds.factory('allBlogSources', function($http, $q){
            return {
                getData: function(sourcesUrl) {
                    var deffered = $q.defer();
                    var myData = {};
                    $http({method: 'GET', url: sourcesUrl}).
                    success(function(data, status, headers, config) {
                        deffered.resolve(data.SourceList);
                    });
                    return deffered.promise;
                }
            }
        });
});