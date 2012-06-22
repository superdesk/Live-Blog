requirejs.config({ paths:{ jquery: '../jquery', gizmo: '../gizmo' }});
define(['jquery', 'qunit', 'gizmo', 'unit/gizmo-data'], function($, q, giz, data)
{
    var run = function()
    {
        module('gizmo.js');
        
        test("should be defined", function() 
        {
            ok(giz, 'gizmo defined');
        });
          
        // models
        var Post = giz.Model.extend({ defaults:{ Author: Collaborator }}),
            Source = giz.Model.extend(),
            Person = giz.Model.extend(),
            Collaborator = giz.Model.extend({ defaults:
            { 
                Post: [Post],
                PostPublished: [Post],
                PostUnpublished: [Post],
                Source: Source,
                Person: Person
            }});

        // hacks
        ajaxMap = data.ajaxMap;
        $.ajax = function( url, options ) 
        {
            var d = new $.Deferred;
            ajaxMap[url] ? d.resolve(ajaxMap[url]) : d.reject();
            return d;
        };
        
        test("should parse complex parts", function()
        {
            var c = new Collaborator('Collaborator/1');
            $(c).on('read', function()
            { 
                ok(this.get('Source') instanceof giz.Model, 'model computes sub-models'); 
                ok(this.get('Post') instanceof giz.Collection, 'model computes sub-collections');
            });
            c.sync();
        });
    };
    
    return {run: run};
});