// TODO: Set a different jshint config for tests and remove the next lines
/*global describe, it, before, beforeEach, after, afterEach, expect, sinon */
/*jshint unused: false, -W030, -W024 */
'use strict';

define(['jquery', 'models/base-model'], function($, Model) {
    describe('Base model', function() {
        describe('poller', function() {
            // Use Sinon to replace jQuery's ajax method
            // with a spy.
            beforeEach(function() {
                sinon.stub($, 'ajax').yieldsTo('success', {
                    Id: 1
                });
            });

            // Restore jQuery's ajax method to its
            // original state
            afterEach(function() {
                $.ajax.restore();
            });
            it('should make an ajax call to //localhost:9000', function(done) {
                var model = new Model({Id: 1}),
                    options = {
                    url: '//localhost:9000',
                    crossDomain: true
                };

                model.poller(options);
                expect($.ajax.calledOnce).to.be.true;
                expect($.ajax.getCall(0).args[0].url).to.equal('//localhost:9000');
                expect($.ajax.getCall(0).args[0].crossDomain).to.be.true;
                expect(model.get('Id')).equal(1);
                done(); // let Mocha know we're done async testing
            });

        });
        describe('properties', function() {
            var model = new Model();
            it('should have property idAttribute equall to "Id"', function() {
                expect(model).to.have.property('idAttribute').to.equal('Id');
            });
        });
    });
});
