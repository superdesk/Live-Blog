// TODO: Set a different jshint config for tests and remove the next lines
/*global describe, it, before, beforeEach, after, afterEach, expect */
/*jshint unused: false, -W030, -W024 */
'use strict';

define(['views/base-view'], function(BaseView) {
    describe('Base view', function() {
        describe('clientEvents', function() {
            it('adds events to the view', function() {
                var view = new BaseView(),
                    events = {
                        e1: 'event1',
                        e2: 'event2'
                    };
                view.clientEvents(events);
                expect(view.events.e1).to.equal('event1');
                expect(view.events.e2).to.equal('event2');
            });
        });
    });
});
