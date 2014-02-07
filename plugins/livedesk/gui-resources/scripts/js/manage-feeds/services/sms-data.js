define([
    'jquery',
    'gizmo/superdesk',
	'angular',
    'lib/livedesk/scripts/js/manage-feeds/manage-feeds'
	], function(jQuery, Gizmo, ngular, feeds){
		feeds.factory('smsData', function($http, $q){
            return {
                getData: function(smsUrl, sourcesUrl) {
                    var deffered = $q.defer();
                    //a bit messy way of getting the sms feeds and the assigned sms feeds

                    $http({method: 'GET', url: smsUrl}).
                    success(function(data, status, headers, config) {
                        var smss = data.SourceList;

                        //go for all feeds
                        $http({method: 'GET', url: sourcesUrl}).
                        success(function(data, status, headers, config) {
                            var allAssigned = data.SourceList;
                            for ( var i = 0; i < smss.length; i ++ ) {
                                smss[i].assigned = false;
                                for ( var j = 0; j < allAssigned.length; j ++ ) {
                                    if ( allAssigned[j].Name == smss[i].Name ) {
                                        smss[i].assigned = true;
                                        smss[i].source = allAssigned[j].Id
                                        break;
                                    }
                                }
                            }
                            deffered.resolve(smss);
                        });
                        //end all feeds
                    });

                    return deffered.promise;
                }
            }
        });
});