define([
    'angular',
    'jquery'
], function(angular, $) {
    'use strict';

    var module = angular.module('users.directives', ['users.resources']);

    module.directive('sdUserImage', function(UserService) {
        return {
            restrict: 'A',
            template: '<img ng-src="{{ src }}" width="{{ width }}" height="{{ height }}" alt="{{ alt }}" />',
            scope: {user: '=sdUser'},
            link: function(scope, element, attrs) {
                scope.width = attrs.width;
                scope.height = attrs.height;
                scope.$watch('user', function(user) {
                    if (user) {
                        scope.alt = user.Name;
                        UserService.getImage(user).then(function(image) {
                            scope.src = image.Thumbnail.href;
                        }, function() {
                            scope.src = '/content/lib/core/images/avatar_default_collaborator.png';
                        });
                    } else {
                        scope.alt = null;
                        scope.src = null;
                    }
                });
            }
        };
    });
});
