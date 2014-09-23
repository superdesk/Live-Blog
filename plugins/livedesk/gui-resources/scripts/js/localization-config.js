define([
	'jquery',
	'angular',
	'gizmo/superdesk',
	config.guiJs('livedesk', 'authorization'),
    'interceptor'
	], function($, angular, Gizmo, auth, interceptor){

		function getGizmoUrl(path) {
	        var url = new Gizmo.Url(path);
	        return url.get();
	    };
	    

	    var locConf = angular.module('localizationConf',[]);
	    locConf.config(['$interpolateProvider', function($interpolateProvider) {
			$interpolateProvider.startSymbol('{{ ');
			$interpolateProvider.endSymbol(' }}');
		}]);
	    locConf.factory('locService', function($rootScope, $q, $http){
	    	var lc = {};
	    	lc.getLanguages = function() {
	    		var deffered = $q.defer();
	    		var langLocation = getGizmoUrl('Localization/Language/?X-Filter=*');
	    		$http.get(langLocation).success(function(data){
	    			deffered.resolve(data.LanguageList);
	    		});
	    		return deffered.promise;
	    	};
	    	lc.incrementRevision = function(param) {
	    		var deffered = $q.defer();
	    		var langLocation = getGizmoUrl('incrementRevision');
	    		$http.put(langLocation).success(function(data){
	    			deffered.resolve(data);
	    		});
	    		return deffered.promise;
	    	};
	    	lc.createIntlCache = function(param) {
	    		var deffered = $q.defer();
	    		var langLocation = getGizmoUrl('Admin/Plugin/livedesk_embed/JSONLocale/' + param);
	    		$http.get(langLocation).success(function(data){
	    			deffered.resolve(data);
	    		});
	    		return deffered.promise;
	    	};
	    	lc.getDownloadLink = function(po) {
	    		return getGizmoUrl('Admin/Plugin/livedesk_embed/PO/'+po);
	    	}
	    	lc.getVersion = function() {
	    		var versionLocation = getGizmoUrl('content/lib/embed/scripts/js/version.js');
	    		versionLocation = versionLocation.replace('resources/','');
	    		var rand = Math.floor((Math.random() * 10000) + 1);
	    		window.liveblog = {};
				liveblog.callbackVersion = function(data) {
					this.versionObject = data;
				};
	    		return $http.jsonp(versionLocation + '?version=' + rand);
	    	}
	    	return lc;
	    });
	    locConf.controller('localizationCtrl', function($rootScope, $scope, locService) {
	    	$scope.switchUploadText = false;
	    	$scope.switchActionText = false;
	    	$scope.uploadText = "";
	    	$scope.actionText = "";
	    	locService.getLanguages().then(function(data){
	    		if(data.length) {
	    			$scope.myLang = data[0].Code;
	    		}
	    		$scope.languages = data;
	    	});
	    	$scope.$watch('myLang', function(){
	    		$scope.downloadLink = locService.getDownloadLink($scope.myLang);
	    		$scope.uploadLink = $scope.downloadLink + '?X-HTTP-Method-Override=PUT';
	    	});
	    	$scope.fileUploaded = function(){
	        	uploadText = _('Upload Complete');
	        	$scope.uploadText = uploadText.toString();
	        	$scope.runActions();
	        	$scope.$apply();
	        }
	        $scope.uploadProgress = function(evt){
	        	progress = Math.round(evt.loaded * 100 / evt.total);
		        $scope.uploadText = progress.toString() + '/100';
		        $scope.$apply();
	        }
	    	$scope.uploadPo = function() {
	    		var uploadText = "";
	    		$scope.switchUploadText = true;
	    		if (typeof($scope.poFile) == "undefined") {
	    			uploadText = _('Please select a valid po file');
	        		$scope.uploadText = uploadText.toString();
	        		return;
	    		}
	    		var fd = new FormData();
	    		fd.append("source", $scope.poFile);
	    		var xhr = new XMLHttpRequest();
	    		xhr.upload.addEventListener("progress", $scope.uploadProgress, false);
		        xhr.addEventListener("load", $scope.fileUploaded, false);
		        xhr.addEventListener("error", function(){
		        	uploadText = _('Upload Failed');
		        	uploadText = uploadText.toString()
		        	alert(uploadText);
		        }, false);
	    		xhr.open("POST", $scope.uploadLink);
	    		xhr.send(fd);
	    		uploadText = _('Uploading');
	        	$scope.uploadText = uploadText.toString();
	    	};
	    	$scope.runActions = function() {
	    		var actionText = "";
	    		$scope.switchActionText = true;
	    		actionText = _('Checking version');
	    		$scope.actionText = actionText.toString();
	    		locService.getVersion().finally(function(data){
	    			var versionObject = liveblog.versionObject;
	    			var intlParam = $scope.myLang + '?version=' + versionObject.major + '.' + versionObject.minor + '.' + versionObject.revision
	    			actionText = _('Creating internationalization cache');
	    			$scope.actionText = actionText.toString();
	    			locService.createIntlCache(intlParam).then(function(data){
	    				actionText = _('Incrementing Revision');
	    				$scope.actionText = actionText.toString();
	    				locService.incrementRevision().then(function(data){
	    					actionText = _('Done');
	    					$scope.actionText = actionText.toString();
	    				});
	    			});

	    		});
	    	}
	    });
	    locConf.directive("fileread", [function () {
		    return {
		        scope: {
		            fileread: "="
		        },
		        link: function (scope, element, attributes) {
		            element.bind("change", function (changeEvent) {
		                scope.$apply(function () {
		                    scope.fileread = changeEvent.target.files[0];
		                });
		            });
		        }
		    }
		}]);
	    return locConf;
	});