define([
	'angular',
    'lib/livedesk/scripts/js/manage-feeds/manage-feeds',
    'lib/livedesk/scripts/js/manage-feeds/services/providers-blogs-data',
    'lib/livedesk/scripts/js/manage-feeds/services/all-blog-sources'
	],function(ngular, feeds){
		feeds.factory('chainedBlogsData', ['$http', '$q','providersBlogsData','allBlogSources',  function($http, $q, providersBlogsData, allBlogSources){
            return {
                getData: function(providersUrl, sourcesUrl) {
                    var deffered = $q.defer();
                    providersBlogsData.getData(providersUrl).then(function(chains){
                        allBlogSources.getData(sourcesUrl).then(function(sources){
                            for ( var i = 0; i < chains.length; i++ ) {
                                for ( var j = 0; j < chains[i].blogList.length; j++ ) {
                                    var chained = false;
                                    var sourceId = -1;
                                    for ( var k = 0; k < sources.length; k ++ ) {
                                        var sourceUri = sources[k].URI.href.replace(/^https?:/,'');
                                        var chainUri = chains[i].blogList[j].href.replace(/^https?:/,'');
                                        if ( sourceUri == chainUri ) {
                                            chained = true;
                                            sourceId = sources[k].Id
                                            break;
                                        }
                                    }
                                    chains[i].blogList[j].chained = chained;
                                    chains[i].blogList[j].sourceId = sourceId;
                                }
                            }
                            deffered.resolve(chains);
                        });
                    });
                    return deffered.promise;
                }
            }
        }]);
});