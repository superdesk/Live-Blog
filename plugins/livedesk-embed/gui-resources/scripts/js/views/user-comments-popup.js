requirejs.config({
    paths: {recaptcha: '//www.google.com/recaptcha/api/js/recaptcha_ajax'}
});

define([
    'jquery',
    'gizmo/superdesk'
], function($, Gizmo) {
    'use strict';

    var Comment = Gizmo.Model.extend({
        save: function(href, options) {
            var adapter = function() {
                return this.syncAdapter.request.apply(this.syncAdapter, arguments);
            };

            return adapter.call(this, href).
                insert(this.data, options);
        }
    });

    return Gizmo.View.extend({
        commentTokenId: 'comment-token',

        events: {
            '#comment-btn': {click: 'togglePopup'},
            '#comment-message-btn': {click: 'showAfterMessage'},
            '.button.cancel': {click: 'cancel'},
            '.button.send': {click: 'send'},
            'form': {submit: 'send'}
        },

        init: function() {
            this.popup = $(this.el).find('.comment-box').hide();
            this.popup_message = $(this.el).find('.comment-box-message').hide();

            this.username = $(this.el).find('#comment-nickname');
            this.text = $(this.el).find('#comment-text');
            this.captcha = $('#' + this.commentTokenId);

            this.resetInput();

            this.loadRecaptcha = true;
            this.href = this.model.data.CommentPost.href.replace('resources/', 'resources/my/'); // needed for captcha

            this.backdropel = $("#backdrop");
        },

        togglePopup: function(e) {
            e.preventDefault();
            this.popup.toggle();
            this.backdropel.toggle();
            //this.popup.slideToggle();
            if (this.popup.is(':visible')) {
                this.openPopup();
            } else {
                this.closePopup();
            }
        },

        openPopup: function() {
            this.timeline.pause();
            this.initRecaptcha();
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
            Recaptcha.reload();
        },
        showAfterMessage: function(e) {
            e.preventDefault();
            var view = this;
            this.popup_message.slideDown();
            setTimeout(function(){
                view.popup_message.slideUp();
            }, 5000)
        },
        send: function(e) {
            e.preventDefault();

            if (this.isValid()) {
                var comment = new Comment({
                    UserName: this.username.val(),
                    CommentText: this.text.val()
                });

                var view = this;
                comment.save(this.href, {
                    headers: {
                        'X-CAPTCHA-Challenge': Recaptcha.get_challenge(),
                        'X-CAPTCHA-Response': Recaptcha.get_response()
                    },
                    success: function() {
                        view.cancel(e);
                        view.showAfterMessage(e);
                    },
                    error: function() {
                        view.captcha.next('.error').show();
                    }
                });
            }
        },

        initRecaptcha: function() {
            if (this.loadRecaptcha) {
                this.loadRecaptcha = false;
                var view = this;
                require(['recaptcha'], function() {
                    Recaptcha.create(view.captcha.attr('data-public-key'), view.captcha.attr('id'), {
                        theme: 'clean'
                    });
                });
            }
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
