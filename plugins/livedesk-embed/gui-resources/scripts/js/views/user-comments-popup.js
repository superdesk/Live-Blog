define([
    'jquery',
    'gizmo/superdesk',
    '//www.google.com/recaptcha/api/js/recaptcha_ajax.js'
], function($, Gizmo) {
    'use strict';

    var Comment = Gizmo.Model.extend({
    });

    var CommentCollection = Gizmo.Collection.extend({
        model: Comment
    });

    return Gizmo.View.extend({
        commentTokenId: 'comment-token',

        events: {
            '#comment-btn': {click: 'togglePopup'},
            '.button.cancel': {click: 'cancel'},
            '.button.send': {click: 'send'},
            'form': {submit: 'send'}
        },

        init: function() {
            this.popup = $(this.el).find('.comment-box').hide();

            this.username = $(this.el).find('#comment-nickname');
            this.text = $(this.el).find('#comment-text');
            this.captcha = $('#' + this.commentTokenId);

            this.resetInput();
            this.initRecaptcha();

            this.storage = new CommentCollection();
            this.storage.setHref(this.model.data.CommentPost.href);
        },

        togglePopup: function(e) {
            e.preventDefault();
            this.popup.toggle();
            if (this.popup.is(':visible')) {
                this.openPopup();
            } else {
                this.closePopup();
            }
        },

        openPopup: function() {
            this.timeline.pause();
            Recaptcha.reload();
        },

        closePopup: function() {
            this.timeline.sync();
        },

        resetInput: function() {
            this.username.val('');
            this.text.val('');
            $(this.el).find('.error').hide();
        },

        cancel: function(e) {
            this.resetInput();
            this.togglePopup(e);
        },

        send: function(e) {
            e.preventDefault();

            if (this.isValid()) {
                this.storage.insert({
                    UserName: this.username.val(),
                    CommentText: this.text.val(),
                    //Challenge: Recaptcha.get_challenge(),
                    //Response: Recaptcha.get_response()
                });
                this.cancel(e);
            }
        },

        initRecaptcha: function() {
            Recaptcha.create(this.captcha.attr('data-public-key'), this.captcha.attr('id'), {
                theme: 'clean'
            });
        },

        isValid: function() {
            if (!this.username.val()) {
                this.username.next('.error').show();
            } else {
                this.username.next('.error').hide();
            }

            if (!this.text.val()) {
                this.text.next('.error').show();
            } else {
                this.text.next('.error').hide();
            }

            if (!Recaptcha.get_response()) {
                this.captcha.next('.error').show();
            } else {
                this.captcha.next('.error').hide();
            }

            return $(this.el).find('.error:visible').length === 0;
        }
    });
});
