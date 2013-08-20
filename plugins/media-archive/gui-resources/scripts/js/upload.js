define([
    'jquery',
    './adv-upload',
    'jqueryui/texteditor',
    'tmpl!media-archive>texteditor-image-command'
], function($, AdvancedUpload) {
    'use strict';


    return {
        /*!
         * plugin for texteditor
         */
        texteditor: function() {
            var origImageCtrl = $.ui.texteditor.prototype.plugins.controls.image;
            var command = origImageCtrl.apply(this, arguments);
            $.tmpl('media-archive>texteditor-image-command', {}, function(e, output) {
                $(command.dialog).prepend(output);

                $('form#editoruploadform [type=button]', command.dialog).on('click', function() {
                    var upload = new AdvancedUpload({thumbSize: 'medium'});
                    upload.activate().then(function(data) {
                        $('body').css('cursor', 'auto');

                        var valIn = $('[data-option="image-value"]', command.dialog);
                        valIn.parents('.control-group:eq(0)').addClass('success');
                        $('<span class="help-inline">&#10004;</span>').insertAfter(valIn);
                        var content = data[0].data.Content;
                        valIn.val(content.href);

                        var thumbnail = $('<img alt="" />').attr('src', data[0].data.Thumbnail.href);
                        $('.thumbnail-placeholder', command.dialog).empty().append(thumbnail);

                        setTimeout(function() {
                            valIn.parents('.control-group:eq(0)').removeClass('success');
                            valIn.next('.help-inline').remove();
                        }, 5000);
                    });
                });

                $(command.dialog).on('dialogclose', function() {
                    $('.thumbnail-placeholder', command.dialog).empty();
                });
            });

            return command;
        }
    };
});
