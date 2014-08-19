define([
	'jquery',
	'angular',
	'gizmo/superdesk',
	config.guiJs('livedesk', 'authorization')
	], function($, angular, Gizmo, auth){
		function getGizmoUrl(path) {
	        var url = new Gizmo.Url(path);
	        return url.get();
	    }
        function relativeToAbsolute(rel) {
            return window.location.protocol + '//' + window.location.host + rel;
        }
	    var angularHeaders = $.extend({}, auth, { 'Content-Type': 'text/json' });
		var seoconf = angular.module('seoConf',[]);
		seoconf.config(['$interpolateProvider', function($interpolateProvider) {
			$interpolateProvider.startSymbol('{{ ');
			$interpolateProvider.endSymbol(' }}');
		}]);
		seoconf.config(function($httpProvider){
			delete $httpProvider.defaults.headers.common['X-Requested-With'];
			$httpProvider.defaults.headers.get = auth;
			$httpProvider.defaults.headers.post = angularHeaders;
			$httpProvider.defaults.headers.put = angularHeaders;
			$httpProvider.defaults.headers.delete = auth;
		});

		seoconf.factory('seoInterfaceData', ['$http', '$q', function($http, $q){
			return {
				getSeoConfigDefaults: function() {
					var deffered = $q.defer();
                    var myData = {};
                    var configUrl = getGizmoUrl('GeneralSetting?group=seo&X-Filter=Value,Key')
                    $http({method: 'GET', url: configUrl}).
                    success(function(data, status, headers, config) {
                        deffered.resolve(data.GeneralSettingList);
                    });
                    return deffered.promise;
				},
				getThemes: function(themeUrl) {
					var deffered = $q.defer();
                    var myData = {};
                    $http({method: 'GET', url: themeUrl}).
                    success(function(data, status, headers, config) {
                        deffered.resolve(data.BlogThemeList);
                    });
                    return deffered.promise;
				},
				getSeoConfigs: function(seoConfigUrl) {
					//get a single seo config's details
					var deffered = $q.defer();
                    $http({method: 'GET', url: seoConfigUrl}).
                    success(function(data, status, headers, config) {
                    	deffered.resolve(data.SeoList);
                    });
                    return deffered.promise;
				},
				getSeoConfig: function(seoConfigUrl) {
					//get all seo configs for this blog
					var deffered = $q.defer();
                    $http({method: 'GET', url: seoConfigUrl}).
                    success(function(data, status, headers, config) {
		                deffered.resolve(data);
                    });
                    return deffered.promise;
				},
				newConfig: function(url, data) {
					var deffered = $q.defer();
                    $http({method: 'POST', url: url, data: data}).
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
				},
				removeConfig: function(Id) {
					var deffered = $q.defer();
                    $http({method: 'DELETE', url: getGizmoUrl('my/LiveDesk/Seo/' + Id)}).
                    success(function(data, status, headers, config) {
                        deffered.resolve(data);
                    });
                    return deffered.promise;
				}
			}
		}]);

		seoconf.controller('seoInterface', function($scope, $http, seoInterfaceData, $q) {
			$scope.cleanConfig = {
        		Id: 0,
        		SeoTheme: '1',
        		CallbackActive: 'True',
        		RefreshActive: 'True',
        		CallbackURL: '',
        		RefreshInterval: 60,
        		MaxPosts: 10,
        		HtmlURL: '',
      	  		LastSync: 0
        	};
        	$scope.defaultConfig = {};
			$scope.boxCounter = 0;
			$scope.updateCheckbox = [];
			$scope.configs = [];
            //initializing some vars
            $scope.addSeoConfig = function() {
            	var config = $scope.completeConfigData($.extend(true,{},$scope.cleanConfig));
            	$scope.RefreshActive = 'True';
            	$scope.configs.push(config);
            };
            $scope.getThemes = function() {
            	seoInterfaceData.getThemes(getGizmoUrl('my/LiveDesk/BlogTheme?X-Filter=Name,Id')).then(function(data) {
	            	$scope.availableThemes = data;
	            });
            };
            $scope.getSeoConfigs = function() {
            	var deffered = $q.defer();
            	seoInterfaceData.getSeoConfigs(getGizmoUrl('my/LiveDesk/Blog/' + $scope.BlogId + '/Seo')).then(function(data) {
	            	//init the configs var
	            	
	            	if (data.length == 0) {
	            		//no seo config for this blog yet
	            		var config = $.extend(true,{},$scope.cleanConfig);
	            		//add this empty new config to the scope
	            		config = $scope.completeConfigData(config);
	            		//add the rest of the data
	            		$scope.configs.push(config);
	            		deffered.resolve(data);
	            	} else {
	            		var dl = data.length;
	            		//done counter
	            		var dc = 0;
	            		for (var i = 0; i < data.length; i ++) {
	            			seoInterfaceData.getSeoConfig(data[i].href).then(function(data){
	            				
	            				//create new config object
	            				var config = {};
	            				config.Id = data.Id;
				            	config.SeoTheme = data.BlogTheme.Id;
				            	config.CallbackActive = data.CallbackActive;
				            	config.CallbackURL = data.CallbackURL;
				            	config.RefreshActive = data.RefreshActive;
				            	config.RefreshInterval = data.RefreshInterval;
				            	config.MaxPosts = data.MaxPosts;
				            	config.HtmlURL = data.HtmlURL;
				            	config.LastSync = data.LastSync;

				            	config = $scope.completeConfigData(config);
				            	//add the rest of the data
	            				$scope.configs.push(config);
	            				dc ++;
	            				if ( dc == dl ) {
	            					//finished loading all the configs
	            					deffered.resolve(data);
	            				}
	            			});
	            		}
	            	}
	            });
	            return deffered.promise;
            };
            $scope.init = function(BlogId) {
            	//variable for the main HTML active button
            	//initialy false until data is read
            	$scope.htmlActive = false;
            	$scope.BlogId = BlogId;
            	//getting the available themes
            	//for new seo configs
            	$scope.getThemes();
            	seoInterfaceData.getSeoConfigDefaults().then(function(data){
            		//create the default config object from db settings
            		for ( var i = 0; i < data.length; i++ ) {
            			$scope.defaultConfig[data[i].Key] = data[i].Value;
            		}
            		$scope.cleanConfig = $.extend(true, $scope.cleanConfig, $scope.defaultConfig);
            		$scope.getSeoConfigs().then(function(){
            			$scope.getMasterHtmlActive();
            		});
            	});
            };
            $scope.getMasterHtmlActive = function() {
            	var startValue = "True";
            	for (var i = 0; i < $scope.configs.length; i ++) {
            		if ( $scope.configs[i].RefreshActive == "False") {
            			startValue = "False";
            			break;
            		}
            	};
            	$scope.htmlActive = startValue;
            };
            $scope.toggleHtmlActive = function() {
            	for (var j = 0; j < $scope.configs.length; j ++) {
            		$scope.configs[j].RefreshActive = $scope.htmlActive;
            	}
            	$scope.saveAllConfigs();
            };
            $scope.showRemove = function(i) {
            	return i ? true : false;
            };
            $scope.showPartition = function(i) {
            	return i ? false : true;
            };
            $scope.toggleExtraInfo = function(i) {
            	$scope.configs[i].showExtra = $scope.configs[i].showExtra === false ? true : false;
            	if ( $scope.configs[i].showExtra ) {
					var extraInfoText = _('Hide advanced settings');
            	} else {
            		var extraInfoText = _('Show advanced settings');
            	}
            	$scope.configs[i].extraInfoText = extraInfoText.toString();
            };
            $scope.completeConfigData = function(config) {
            	config.showExtra = false;
            	var extraInfoText = _('Show advanced settings');
            	config.extraInfoText = extraInfoText.toString();
            	config.HtmlWaitSwitch = false;
            	//on-off switches for data that may or may not be present
            	config.HtmlURLSwitch = true;
            	config.CallbackStatusSwitch = false;
            	//vars to keep the text info
            	config.HtmlURLText = _('URL');
            	config.CallbackStatusText = '';
            	//general info on the html created
            	if (config.Id > 0 && config.HtmlURL && config.LastSync) {
                    config.HtmlWaitSwitch = false;
            		config.HtmlURLSwitch = true;
            		config.HtmlURL = relativeToAbsolute(config.HtmlURL);
            		config.HtmlURLText =  _('URL');
            		//add timeinfo to text if it exists
            		if ( config.Id > 0 && config.LastSync ) {
            			var LastSync = new Date( config.LastSync );
            		}
            	} else {
            		config.HtmlURL = _('Please select a theme and press Generate HTML');
            		config.HtmlURL = config.HtmlURL.toString();
            	}
            	config.HtmlURLText = config.HtmlURLText.toString();
            	//info on callback status if it exists
            	if (config.Id > 0 && config.CallbackStatus ) {
            		config.CallbackStatusSwitch = true;
            		config.CallbackStatusText = config.CallbackStatus;
            	}
            	return config;
            };

            $scope.handleHtmlLink = function(seoUrl, i) {
                $scope.configs[i].HtmlURLSwitch = false;
                $scope.configs[i].CallbackStatusSwitch = false;
                $scope.configs[i].HtmlWaitSwitch = true;
                var waitText = _('Please wait while the HTML is generating...');
                $scope.configs[i].HtmlWaitText = waitText.toString();
                if ($scope.configs[i].RefreshActive == "False") {
                    $scope.configs[i].HtmlWaitSwitch = false;
                    return;
                }
                
                if ($scope.configs[i].htmlInterval) {
                    clearInterval($scope.configs[i].htmlInterval);
                }

                var counter = 0;
                $scope.configs[i].htmlInterval = setInterval(function() {
                    $http({method: 'GET', url: seoUrl, headers: {'X-Format-DateTime': "yyyy-MM-ddTHH:mm:ss'Z'"}}).
                    success(function(data, status, headers, config) {
                        //return the data from the newly created seo config object
                        var changedOn = Date.parse(data.ChangedOn);
                        counter ++;
                        if (counter == 20) {
                            clearInterval($scope.configs[i].htmlInterval);
                            var text = _('The HTML generation process is taking too long, please refresh the page at a later time');
                            $scope.configs[i].HtmlWaitText = text.toString();
                        }
                        if (data.CallbackStatus) {
                            clearInterval($scope.configs[i].htmlInterval);
                            $scope.configs[i].HtmlURLSwitch = false;
                            $scope.configs[i].HtmlWaitSwitch = false;
                            $scope.configs[i].CallbackStatusText = _('Result: ');
                            $scope.configs[i].CallbackStatusText += data.CallbackStatus;
                            $scope.configs[i].CallbackStatusSwitch = true;
                        }
                        if (data.LastSync) {
                            var LastSyncOn = Date.parse(data.LastSync);
                            if ( LastSyncOn >= changedOn) {
                                clearInterval($scope.configs[i].htmlInterval);
                                $scope.configs[i].HtmlURL = relativeToAbsolute(data.HtmlURL);
                                var urlText = _('SEO html');
                                $scope.configs[i].HtmlURLText = urlText.toString();
                                $scope.configs[i].HtmlURLSwitch = true;
                                $scope.configs[i].HtmlWaitSwitch = false;
                            }
                        }
                    });
                }, 10000);
            };
            //loop through all configs and save them one by one
            $scope.removeConfig = function(index) {
            	if ($scope.configs[index].Id) {
                    //clearInterval if it exists
                    if ($scope.configs[index].htmlInterval) {
                        clearInterval($scope.configs[index].htmlInterval);
                    }
					seoInterfaceData.removeConfig($scope.configs[index].Id).then(function(){
	            		$scope.configs.splice(index, 1);
	            	});
            	} else {
            		$scope.configs.splice(index, 1);
            	}
            };
            $scope.isLast = function(i) {
            	return $scope.configs.length - 1 == i;
            }
            $scope.showNewHtml = function() {
            	return $scope.configs.length < 4;
            };
            $scope.saveAllConfigs = function() {
            	for (var i = 0; i < $scope.configs.length; i ++) {
            		$scope.save($scope.configs[i], i);
            	}
            };
            $scope.save = function(config, index) {
            	var data = {
            		BlogTheme: config.SeoTheme.toString(),
	            	CallbackActive: config.CallbackActive,
	            	CallbackURL: config.CallbackURL,
	            	RefreshActive: $scope.htmlActive,
	            	RefreshInterval: config.RefreshInterval.toString(),
	            	MaxPosts: config.MaxPosts.toString()	
            	}
            	if ( config.Id == 0 ) {
            		//new request
            		data.Blog = $scope.BlogId.toString();
            		seoInterfaceData.newConfig(getGizmoUrl('my/LiveDesk/Seo'), data).then(function(data) {
            			//set the seo object scope id to the newly created one
            			config.Id = data.Id;
                        $scope.handleHtmlLink(getGizmoUrl('my/LiveDesk/Seo/' + config.Id), index);
            		});
            	} else {
					seoInterfaceData.editConfig(getGizmoUrl('my/LiveDesk/Seo/' + config.Id), data).then(function(data) {
            			//stuff do to after seo config edit
                        $scope.handleHtmlLink(getGizmoUrl('my/LiveDesk/Seo/' + config.Id), index);
            		});
            	}
            };
            $scope.toggleSave = function(index) {
            	$scope.save($scope.configs[index], index);
            };
        });
	
		seoconf.directive('seoToggler', function() {
			return {
				restrict: 'E',
				scope: {
					toggle: "=",
					action: "&"
				},
				template: '<div style="float:none" class="sf-toggle-custom on-off-toggle"><div class="sf-toggle-custom-inner"></div></div>',
				link: function(scope, element, attrs) {
					if ( scope.toggle == attrs['trueValue'] ) {
						element.find('.sf-toggle-custom').addClass('sf-checked');
					}
					scope.$watch('toggle', function(){
						//console.log('true vlue ',attrs['trueValue']);
						if ( scope.toggle == attrs['trueValue'] ) {
							element.find('.sf-toggle-custom').addClass('sf-checked');
						} else {
							element.find('.sf-toggle-custom').removeClass('sf-checked');
						}
					}, true);
					element.find('.sf-toggle-custom').on('click', function(){
						$(this).toggleClass('sf-checked');
						if ( $(this).hasClass('sf-checked') ) {
							scope.toggle = attrs['trueValue'];
						} else {
							scope.toggle = attrs['falseValue'];
						}
                        scope.$apply();
                        scope.action(attrs['index']);
					})
				}
			}
		})

        return seoconf;
	});