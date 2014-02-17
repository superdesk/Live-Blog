define([
	'angular',
	'gizmo/superdesk'
	], function(angular, Gizmo){
		function getGizmoUrl(path) {
	        var url = new Gizmo.Url(path);
	        return url.get();
	    }
		var seoconf = angular.module('seoConf',[]);
		seoconf.config(['$interpolateProvider', function($interpolateProvider) {
			$interpolateProvider.startSymbol('{{ ');
			$interpolateProvider.endSymbol(' }}');
		}]);
		seoconf.config(function($httpProvider){
			delete $httpProvider.defaults.headers.common['X-Requested-With'];
			$httpProvider.defaults.headers.get = { 'Authorization': localStorage.getItem('superdesk.login.session') }
		});

		seoconf.factory('seoInterfaceData', ['$http', '$q', function($http, $q){
			return {
				getThemes: function(themeUrl) {
					var deffered = $q.defer();
                    var myData = {};
                    $http({method: 'GET', url: themeUrl}).
                    success(function(data, status, headers, config) {
                        deffered.resolve(data.BlogThemeList);
                    });
                    return deffered.promise;
				},
			}
		}]);

		seoconf.controller('seoInterface', function($scope, $http, seoInterfaceData) {
            //initializing some vars
            $scope.chains = 'nebunie';
            seoInterfaceData.getThemes(getGizmoUrl('my/LiveDesk/BlogTheme?X-Filter=Name')).then(function(data) {
            	$scope.seoTheme = "stt";
            	$scope.availableThemes = data;
            });
            //getting the available themes
        });

        return seoconf;
	});