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
            '.button.cancel': {click: 'togglePopup'},
            '.button.send': {click: 'send'},
            'form': {submit: 'send'}
        },
        messageDisplayTime: 5000,
        init: function() {
            this.popup = $(this.el).find('.comment-box').hide();
            this.popup_message = $(this.el).find('.comment-box-message').hide();

            this.username = $(this.el).find('#comment-nickname');
            this.text = $(this.el).find('#comment-text');
            this.captcha = $('#' + this.commentTokenId);

            this.resetInput();

            this.loadRecaptcha = true;
            this.href = this.model.data.CommentPost.href.replace('resources/', 'resources/my/'); // needed for captcha

            this.backdropel = $("#backdrop").data('show-status',0);

            this.lbpostlist = this.backdropel.parent();
        },

        togglePopup: function(e) {
            var view = this,
                showStatus = view.backdropel.data('show-status');
            e.preventDefault();
            switch(showStatus) {
                case 0:
                    view.popup.show();
                    view.backdropel.data('show-status',1).show(); 
                    view.lbpostlist.addClass('comment-active');
                    view.timeline.pause();
                    break;
                case 1:
                    view.backdropel.data('show-status',0).hide();
                case 2:
                    view.popup_message.hide();
                    view.resetInput();
                    view.lbpostlist.removeClass('comment-active');
                    view.popup.hide();
                    view.timeline.sync();
                    break;
            }

        },

        resetInput: function() {
            this.username.val('');
            this.text.val('');
            $(this.el).find('.error').hide();
        },

        showAfterMessage: function(e) {
            var view = this;
            view.backdropel.data('show-status',2).show();
            view.popup.toggle();
            view.backdropel.data('show-status',1);
            this.popup_message.show();
            setTimeout(function(){
                view.popup_message.hide({ duration: 0, done: function(){
                    view.backdropel.data('show-status',0);
                    view.backdropel.hide();
                }});
            }, view.messageDisplayTime);
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
                    // headers: {
                    //     'X-CAPTCHA-Challenge': Recaptcha.get_challenge(),
                    //     'X-CAPTCHA-Response': Recaptcha.get_response()
                    // },
                    success: function() {
                        view.showAfterMessage(e);
                    },
                    error: function(response) {
                        view.showAfterMessage(e);
                        /*
                        if (response.status === 401) {
                            Recaptcha.reload();
                        }

                        view.captcha.next('.error').show();
                        */
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

            /*
            if (!Recaptcha.get_response()) {
                this.captcha.next('.error').show();
            } else {
                this.captcha.next('.error').hide();
            }
            */
            return $(this.el).find('.error:visible').length === 0;
        }
    });
});
