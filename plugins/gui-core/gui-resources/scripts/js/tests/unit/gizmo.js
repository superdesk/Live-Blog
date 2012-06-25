requirejs.config({ paths:{ jquery: '../jquery', gizmo: '../gizmo' }});
define(['jquery', 'qunit', 'gizmo', 'unit/gizmo-data'], function($, q, giz, data)
{
    var run = function()
    {
        module('gizmo.js');
        
        test("should be defined", function() 
        {
            ok( giz, 'gizmo defined' );
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
            }})
            xtest = Post.extend();

        console.dir(Post);

        // hacks
        ajaxMap = data.ajaxMap;
        $.ajax = function( url, options ) 
        {
            var d = new $.Deferred,
                isDelete = options.type && options.type == 'get' && 
                            options.headers && options.headers['X-HTTP-Method-Override'] && 
                            options.headers['X-HTTP-Method-Override'] == "DELETE";
            ajaxMap[url] || isDelete ? d.resolve(ajaxMap[url] || null) : d.reject();
            return d;
        };
        
        test("model should read complex data", function()
        {
            var c = new Collaborator('Collaborator/1');
            $(c).on( 'read', function()
            { 
                ok( typeof this.get('Name') === 'string', 'model computes primitive properties')
                ok( this.get('Source') instanceof giz.Model, 'model computes sub-models' ); 
                ok( this.get('Post') instanceof giz.Collection, 'model computes sub-collections' );
            });
            c.sync();
        });
        
        asyncTest("should handle delete", function()
        {
            var p = new giz.Collection('Collaborator/1/Post', Post),
                item = 1,
                testHasOneLess = function()
                { 
                    p.get(item).done(function(){ ok(false, 'item stil present in collection after atempt on its removal'); start(); })
                        .fail(function(){ ok(true, 'item gone from collection after its removal! yay!'); start(); }); 
                };
            // on sync we get an item and try to remove it
            $(p).on( 'read', function()
            {
                p.get(item).done(function(model)
                {
                    model.remove().sync().done( testHasOneLess );
                });
            });
            p.sync();
        });
    };
    
    return {run: run};
});