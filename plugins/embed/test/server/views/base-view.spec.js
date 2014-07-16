/*global describe, it, before, beforeEach, after, afterEach, expect, requirejs */
/*jshint unused: false, -W030, -W024 */
'use strict';
describe('Base view', function() {
    var view;

    beforeEach(function(done) {
        requirejs(['views/base-view'], function(BaseView) {
            view = new BaseView();
            done();
        });
    });

    describe('clientEvents', function() {
        it('does not add events to the view', function() {
            var events = {
                    e1: 'event1',
                    e2: 'event2'
                };
            view.clientEvents(events);
            expect(view.events.e1).to.be.undefined;
            expect(view.events.e2).to.be.undefined;
        });
    });
});
