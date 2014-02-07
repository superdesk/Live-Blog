define([
	'angular',
    'lib/livedesk/scripts/js/manage-feeds/manage-feeds'
	],function(ngular, feeds){
		feeds.factory('provider', function($http, $q){
            return {
                addData: function(addProviderUrl, params) {
                    var deffered = $q.defer();
                    $http.post(addProviderUrl, params).
                    success(function(data, status, headers, config) {
                        deffered.resolve(data);
                    }).
                    error(function(data, status, headers, config) {
                    	deffered.reject(data.message);
                    });
                    return deffered.promise;
                },
                createProviderObject: function(source) {
                	var mySource = {};
                    var deffered = $q.defer();
                    var srcUrl = source.href;

                    //hack to add my in the request
                    if ( srcUrl.indexOf( 'my' ) == -1 ) {
                        var indexRes = srcUrl.indexOf('/Data');
                        srcUrl = srcUrl.slice(0, indexRes) + '/my' + srcUrl.slice(indexRes);
                    }

                	$http.get(srcUrl).success(function(data){
                		mySource = {
                			Id: data.Id,
                			Name: data.Name,
                			URI: data.URI,
                			href: source.href
                		}
                		var infoUri = data.URI.href + '?X-Filter=Title,Description';
                		$http({method: 'GET', url: infoUri}).
                        success(function(data, status, headers, config) {
                        	data.BlogList.chained = false;
                        	data.BlogList.sourceId = -1;
                            mySource.blogList = data.BlogList;
                            deffered.resolve(mySource);
                        });
                	}).
                	error(function(data, status, headers, config){
                		deffered.reject(data.message);
                	})
                	return deffered.promise;
                },
                unchainBlogs: function(unchainUrl, blogs) {
                    if ( blogs instanceof Array ) {
                        for ( var i = 0; i < blogs.length; i ++ ) {
                            if ( blogs[i].sourceId > 0 ) {
                                $http({method: 'DELETE', url: unchainUrl + blogs[i].sourceId});
                            }
                        }
                    }
                },
                getBlogs: function(url) {
                    var deffered = $q.defer();
                    var infoUri = url + '?X-Filter=Title,Description';
                    $http({method: 'GET', url: infoUri}).
                    success(function(data, status, headers, config) {
                        deffered.resolve(data.BlogList);
                    }).
                    error(function(){
                        deffered.reject(0);
                    });
                    return deffered.promise;
                },
                editProvider: function(editProviderUrl, params) {
                    var deffered = $q.defer();
                    $http.put(editProviderUrl, params).success(function(data){
                        deffered.resolve(data);
                    }).
                    error(function(){
                        deffered.reject(data);
                    });
                    return deffered.promise;
                }
            }
        });
});