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
			$httpProvider.defaults.headers.post = { 'Authorization': localStorage.getItem('superdesk.login.session') }
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
				getSeoConfig: function(seoConfigUrl) {
					var deffered = $q.defer();
                    $http({method: 'GET', url: seoConfigUrl}).
                    success(function(data, status, headers, config) {
                    	var SeoList = data.SeoList;
                    	if ( SeoList.length ) {
                    		//pick the first one for now
                    		varSeoConfigItemLink = SeoList[0].href;
                    		$http({method: 'GET', url: varSeoConfigItemLink}).
		                    success(function(data, status, headers, config) {
		                    	deffered.resolve(data);
		                    });
                    	} else {
                    		deffered.resolve({Id: 0});
                    	}
                        
                    });
                    return deffered.promise;
				},
				newConfig: function(url, data) {
					var deffered = $q.defer();
                    $http({method: 'POST', url: url, data: data, headers: {'Content-Type': 'text/json'}}).
                    success(function(data, status, headers, config) {
                    	$http({method: 'GET', url: data.href}).
	                    success(function(data, status, headers, config) {
	                    	//return the data from the newly created seo config object
	                    	deffered.resolve(data);
	                    });
                        
                    });
                    return deffered.promise;
				},
				editConfig: function(url, data) {
					var deffered = $q.defer();
                    $http({method: 'PUT', url: url, data: data}).
                    success(function(data, status, headers, config) {
                        deffered.resolve(data);
                    });
                    return deffered.promise;
				}
			}
		}]);

		seoconf.controller('seoInterface', function($scope, $http, seoInterfaceData) {
			$scope.boxCounter = 0;
			$scope.updateCheckbox = [];
            //initializing some vars
            $scope.init = function(BlogId) {
            	$scope.BlogId = BlogId;
            	//getting the available themes
	            seoInterfaceData.getThemes(getGizmoUrl('my/LiveDesk/BlogTheme?X-Filter=Name,Id')).then(function(data) {
	            	$scope.availableThemes = data;
	            });
	            seoInterfaceData.getSeoConfig(getGizmoUrl('my/LiveDesk/Blog/' + $scope.BlogId + '/Seo')).then(function(data) {
					
	            	if ( data.Id == 0 ) {
	            		$scope.Id = 0;
	            		$scope.SeoTheme = "1";
	            		$scope.CallbackActive = 'False';
	            		$scope.RefreshActive = 'False';
	            		$scope.CallbackURL = '';
	            		$scope.RefreshInterval = 60;
	            		$scope.MaxPosts = 10;
	            		$scope.HtmlURL = '';
	            		$scope.LastSynk = 0;
	            	} else {
	            		$scope.Id = data.Id;
		            	$scope.SeoTheme = data.BlogTheme.Id;
		            	$scope.CallbackActive = data.CallbackActive;
		            	$scope.CallbackURL = data.CallbackURL;
		            	$scope.RefreshActive = data.RefreshActive;
		            	$scope.RefreshInterval = data.RefreshInterval;
		            	$scope.MaxPosts = data.MaxPosts;
		            	$scope.HtmlURL = data.HtmlURL;
		            	$scope.LastSynk = data.LastSynk;
	            	}

	            	for ( var i = 0; i < $scope.boxCounter; i++ ) {
	            		$scope.updateCheckbox[i]();
	            	}

	            	//on-off switches for data that may or may not be present
	            	$scope.HtmlURLSwitch = false;
	            	$scope.CallbackStatusSwitch = false;

	            	//vars to keep the text info
	            	$scope.HtmlURLText = '';
	            	$scope.CallbackStatusText = '';

	            	//general info on the html created
	            	if ( data.HtmlURL ) {
	            		$scope.HtmlURLSwitch = true;
	            		$scope.HtmlURL = data.HtmlURL;
	            		$scope.HtmlURLText =  _('SEO html');
	            		//add timeinfo to text if it exists
	            		if ( data.LastSynk ) {
	            			var lastSynk = new Date( data.LastSynk );
	            			$scope.HtmlURLText += _(' generated on ');
	            			$scope.HtmlURLText += lastSynk.format('yyyy-mm-dd HH:MM:ss');
	            		}
	            	}
	            	$scope.HtmlURLText = $scope.HtmlURLText.toString();
	            	//info on callback status if it exists
	            	if ( data.CallbackStatus ) {
	            		$scope.CallbackStatusSwitch = true;
	            		$scope.CallbackStatusText = _('Callback URL responded with ');
	            		$scope.CallbackStatusText += data.CallbackStatus;
	            	}	            	
	            });
            };
            $scope.save = function() {
            	var data = {
            		BlogTheme: $scope.SeoTheme.toString(),
	            	CallbackActive: $scope.CallbackActive,
	            	CallbackURL: $scope.CallbackURL,
	            	RefreshActive: $scope.RefreshActive,
	            	RefreshInterval: $scope.RefreshInterval.toString(),
	            	MaxPosts: $scope.MaxPosts.toString()	
            	}
            	if ( $scope.Id == 0 ) {
            		//new request
            		data.Blog = $scope.BlogId.toString();
            		seoInterfaceData.newConfig(getGizmoUrl('my/LiveDesk/Seo'), data).then(function(data) {
            			//set the seo object scope id to the newly created one
            			$scope.Id = data.Id;
            		});
            	} else {
					seoInterfaceData.editConfig(getGizmoUrl('LiveDesk/Seo/' + $scope.Id), data).then(function(data) {
            			//stuff do to after seo config edit
            		});
            	}
            };
        });
	
		seoconf.directive('seoToggler', function() {
			return {
				restrict: 'E',
				template: '<div style="float:none" class="sf-toggle-custom on-off-toggle"><div class="sf-toggle-custom-inner"></div></div>',
				link: function(scope, element, attrs) {
					scope.updateCheckbox[scope.boxCounter] = function() {
						var value = scope[attrs['toggle']];
						if ( value == attrs['trueValue'] ) {
							element.find('.sf-toggle-custom').addClass('sf-checked');
						}
					}
					scope.boxCounter ++;
					element.find('.sf-toggle-custom').on('click', function(){
						$(this).toggleClass('sf-checked');
						if ( $(this).hasClass('sf-checked') ) {
							scope[attrs['toggle']] = attrs['trueValue'];
						} else {
							scope[attrs['toggle']] = attrs['falseValue'];
						}
					})
				}
			}
		})

        return seoconf;
	});