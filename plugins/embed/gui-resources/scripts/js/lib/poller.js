'use strict';

// Inspired in Backbone poller: https://github.com/uzikilon/backbone-poller
define(['underscore'], function(_) {

    var poller = {

        defaultPollSettings: {
            // pollInterval in milliseconds
            pollInterval: null,

            // The function to use when polling
            poller: null,

            // Options to be passed to the polling function
            pollOptions: {}
        },

        startPolling: function() {
            for (var setting in this.defaultPollSettings) {
                if (!this[setting]) {
                    this[setting] = this.defaultPollSettings[setting];
                }
            }
            this._delayedPoll();
        },

        stopPolling: function() {
            clearInterval(this.timeoutId);
            this.timeoutId = null;
            if (this.xhr && this.xhr.abort) {
                this.xhr.abort();
                this.xhr = null;
            }
        },

        _poll: function() {
            if (!(this.pollInterval && this.poller && typeof this.poller === 'function')) {
                return;
            }

            var self = this;

            var options = _.extend(this.pollOptions, {
                success: function(model, resp, opt) {
                    self._delayedPoll();
                },
                error: function(model, resp, opt) {
                    self.stopPolling();
                }
            });

            this.xhr = this.poller(options);
        },

        _delayedPoll: function() {
            if (!this.pollInterval) { return; }
            var run = _.bind(this._poll, this);
            this.timeoutId = _.delay(run, this.pollInterval);
        }
    };

    return poller;
});
