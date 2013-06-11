define([
    'angular',
    'jquery',
    'https://github.com/enyo/dropzone/raw/master/downloads/dropzone-amd-module.js',
    'jqueryui/datepicker',
    'jqueryui/sortable',
    'jqueryui/droppable',
    'jqueryui/draggable',
    'bootstrap/tab'
], function(angular, $, Dropzone) {
    'use strict';

    var module = angular.module('directives', ['resources']);

    module.directive('sdDatepicker', function() {
        return {
            restrict: 'A',
            requires: 'ngModel',
            link: function(scope, element, attrs) {
                element.datepicker({
                    dateFormat: 'yy-mm-dd 12:00:00',
                    onClose: function(dateText) {
                        scope.$apply(function() {
                            element.controller('ngModel').$setViewValue(dateText);
                        });
                    }
                });
                element.addClass('hide');
                element.siblings('[data-toggle="datepicker"]').click(function() {
                    element.datepicker('show');
                });
            }
        };
    });

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

    module.directive('sdSortable', function(CardService) {
        return {
            restrict: 'A',
            require: 'ngModel',
            link: function(scope, element, attrs, ngModel) {
                var startIndex = null;
                $(element[0]).sortable({
                    delay: 150,
                    start: function(e, ui) {
                        startIndex = $(ui.item).index();
                    },
                    stop: function(e, ui) {
                        var diff = $(ui.item).index() - startIndex;
                        var model = ngModel.$viewValue[$(ui.item).attr('data-index')];
                        scope.$apply(function() {
                            CardService.moveCard(model, diff);
                        });
                    }
                });
            }
        };
    });

    module.directive('sdDraggable', function($rootScope) {
        return {
            restrict: 'A',
            require: 'ngModel',
            link: function(scope, element, attrs, ngModel) {
                var $el = $(element[0]);
                $el.draggable({
                    appendTo: 'body',
                    revert: 'invalid',
                    cursor : 'move',
                    helper: 'clone',
                    zIndex: 1000,
                    start: function(e, ui) {
                        $rootScope.draggable = ngModel;
                        $(ui.helper).width($el.width());
                        $(ui.helper).height($el.height());
                    },
                    stop: function(e, ui) {
                        $rootScope.draggable = null;
                    }
                });
            }
        };
    });

    module.directive('sdDroppable', function($rootScope, TaskService) {
        return {
            restrict: 'A',
            require: 'ngModel',
            link: function(scope, element, attrs, ngModel) {
                var $el = $(element[0]);
                var statusBox = $el.closest('.board-statuses');
                $el.droppable({
                    hoverClass: 'drop-hover-status',
                    drop: function(e, ui) {
                        scope.$apply(function() {
                            var task = $rootScope.draggable.$viewValue;
                            task.Status.Key = ngModel.$viewValue.Key;
                            TaskService.saveTaskStatus(task);
                            $rootScope.draggable.$setViewValue(task);
                        });
                    },
                    activate: function(e, ui) {
                        statusBox.show();
                    },
                    deactivate: function(e, ui) {
                        statusBox.hide();
                    }
                });
            }
        };
    });

    module.directive('sdDateTime', function($filter) {
        return {
            scope: {datetime: '=sdDateTime'},
            link: function(scope, element, attrs) {
                scope.$watch('datetime', function(datetime) {
                    var date = new Date(datetime);
                    if (date.valueOf()) {
                        element.text($filter('date')(date, 'd.M.yy HH:mm'));
                    } else {
                        element.text(datetime);
                    }
                });
            }
        };
    });

    // implements modal stack
    module.directive('sdModal', function() {
        var modals = [];
        return {
            restrict: 'A',
            scope: true,
            link: function(scope, element, attrs) {
                element.hide().addClass('modal').addClass('fade');
                var modal = $(element).modal({show: false});

                // hide previously opened modal on show
                modal.on('show', function() {
                    if (modals.length) {
                        var last = modals.pop();
                        $(last).modal('hide');
                        modals.push(last);
                    }

                    modals.push(this);
                });

                // display previously opened modal on hide
                modal.on('hide', function() {
                    modals.pop();
                    if (modals.length) {
                        var last = modals.pop();
                        $(last).modal('show');
                        modals.push(last);
                    }
                });

                if ('modalOpen' in attrs) {
                    modal.on('show', function() {
                        scope.$apply(attrs.modalOpen);
                    });
                }
            }
        };
    });

    module.directive('sdTab', function() {
        return {
            link: function(scope, element, attrs) {
                $(element).tab();
            }
        };
    });

    module.directive('sdUpload', function(uploadUrl) {
        return {
            restrict: 'A',
            scope: false,
            link: function(scope, element, attrs) {
                element.addClass('dropzone-previews');

                var dropzone = new Dropzone(element[0], {
                    url: uploadUrl,
                    paramName: 'upload_file',
                    previewsContainer: element[0],
                    clickable: element.children()[0]
                });

                dropzone.on('success', function(file, response) {
                    scope.$apply(function() {
                        scope.files.push(response);
                    });
                });

                scope.$on('files:reset', function() {
                    dropzone.removeAllFiles();
                });
            }
        };
    });
});
