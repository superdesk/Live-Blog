requirejs.config({ paths:{ jquery: '../jquery', gizmo: '../gizmo', history: '../history', utils: '../utils' }});
define(['jquery', 'qunit', 'gizmo/superdesk', 'unit/gizmo-data'], function($, q, giz, data)
{
    var xtest = xasyncTest = $.noop, 
    run = function()
    {
        module('gizmo.js');
        
        test("should be defined", function() 
        {
            ok( giz, 'gizmo defined' );
        });
        
        /*
        asyncTest("change set", function()
        {
            var Collaborator = giz.Model.extend({ helloYesThisDog: true }),
            Collaborators = giz.Collection.extend({ model: Collaborator}),
            User = giz.Model.extend(),
            Blog = giz.Model.extend
            ({ 
                defaults:
                { 
                    Collaborator: Collaborators,
                    Creator: User
                }
            });
            b = new Blog('http://localhost:8080/resources/my/LiveDesk/Blog/1');
            b.on('read', function()
            {
                b.set('Description', 'x');
                b.set('Title', 'x');
                console.log(b)
            });
            b.sync();
        });
        
        return;
        
        /*asyncTest("xxxxx", function()
        {
            var Collaborator = giz.Model.extend({ helloYesThisDog: true }), 
            Collaborators = giz.Collection.extend({ model: Collaborator}), 
            Blog = giz.Model.extend
            ({ 
                defaults:
                { 
                    Collaborator: Collaborators
                }
            }),
            
            b = new Blog('http://localhost:8080/resources/my/LiveDesk/Blog/1');
            b.on('read', function()
            { 
                console.group('test'), 
                console.dir(this.defaults.Collaborator)
                console.dir(this.get('Collaborator'));
                console.groupEnd();
            });
            b.sync(); 
            
            start();
        });*/
        
        // models
        var Post = giz.Model.extend({ defaults:{ Author: Collaborator }}),
            Source = giz.Model.extend(),
            Person = giz.Model.extend(),
            ColabPost = giz.Collection.extend({model: Post}),
            Collaborator = giz.Model.extend({ defaults:
            { 
                Post: ColabPost,
                PostPublished: [Post],
                PostUnpublished: [Post],
                Source: Source,
                Person: Person
            }});
            // this should be solved by require.js
            Post.prototype.defaults.Author = Collaborator;

        //console.dir(new giz.Collection('Collaborator/1/Post/Published', Post));
        //return;  
            
        // hacks
        ajaxMap = data.ajaxMap;
        $.ajax = function( url, options ) 
        {
            var d = new $.Deferred,
                isInsert = (options.type  && options.type == 'post') &&
                    (!options.headers || !options.headers['X-HTTP-Method-Override']),
                isDelete = options.type && options.type == 'get' && 
                            options.headers && options.headers['X-HTTP-Method-Override'] && 
                            options.headers['X-HTTP-Method-Override'] == "DELETE";

            if( ajaxMap[url] && isInsert ) // simulate insert
                for( var i in ajaxMap[url] )
                { 
                    var data = $.extend(options.data,{href: 'some/href/'+String(Math.random()).replace('.','')});
                    ajaxMap[url][i].push(data);
                    d.resolve( ajaxMap[url][i][ajaxMap[url][i].length-1] );
                    break;
                }

            ajaxMap[url] || isDelete ? d.resolve(ajaxMap[url] || null) : d.reject();
            return d;
        };
        
        
        asyncTest('', function()
        {
           var p1 = giz.Auth(new Post('Post/1')),
               p2 = new Post('Post/2'),
               p11 = new Post('Post/1');

           console.log(new Post('Post/3'));
           
           p11.on('update', function(){ console.log(this, arguments) })
           
           p1.set({Content: 'D'});
           
           start();
           
        });
        
        return;
        
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

        asyncTest("should handle insert", function()
        {
            var p = new Post(),
                c = new giz.Collection('Collaborator/1/Post/Published', Post),
                csync = function(){ c.sync.call(c); },
                clistlen = 0;
                
            // read handler for collection, test new items inserted here
            $(c).on('read', function()
            {
                var newlen = c.getList().length;
                ok( clistlen < newlen, 'insert works, we have '+newlen+' items in list' );
            });

            // push a new model object
            $(p).on('insert', function(event)
            {  
                ok(event.type == 'insert', 'triggers "insert" handler');
                csync();
            });
            p.set({ 'Author': 1, 'Content': 'Test content', 'Id': 3})
                .sync('Collaborator/1/Post/Published');
            
            // insert from collection
            var p1 = new Post;
            p1.set({ 'Author': 1, 'Content': 'Test content', 'Id': 4});
            c.insert(p1).done(csync);
            c.insert({ 'Author': 1, 'Content': 'Test content', 'Id': 4}).done(csync);
            start();
        });
        
        asyncTest("should handle update", function()
        {
            var p = new Post('Person/1'),
                newNameData = 'Some other name',
                updateHandler = function(event)
                {
                    ok( event.type == 'update', 'triggers "update" event' );
                    ok( p.get('FirstName') == newNameData, 'data gets updated' );
                },
                updateFnc = function()
                {
                    p.set('FirstName', newNameData).sync();
                };
            $(p).on( 'read', updateFnc );
            $(p).on( 'update', updateHandler);
            p.sync();
            start();
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
                    $(model).on('delete', function(event)
                    {
                        ok( event.type == 'delete', 'triggers "delete" handler');
                    });
                    model.remove().sync().done( testHasOneLess );
                });
            });
            p.sync();
            start();
        });
        
        asyncTest("can be extended", function()
        {
            var newSync = $.extend({}, giz.Sync, 
            {
                options: { headers: { 'Authentication': 1 } },
                href: function(source)
                {
                    return 'my/'+source;
                },
                reset: function()
                {
                    try{ delete this.options.headers['X-Filter']; }catch(e){}
                }
            }),
            authModel = giz.Model.extend
            ({ 
                syncAdapter: newSync,
                xfilter: function()
                {
                    if( this.syncAdapter.options.headers ) this.syncAdapter.options.headers = {};
                    this.syncAdapter.options.headers['X-Filter']
                        = arguments.length > 1 ? $.makeArray(arguments).join(',') : $.isArray(data) ? data.join(',') : data;
                    return this;
                }
            });
                
            ok((new authModel).syncAdapter.options.headers.Authentication == 1, 
                    'has new "sync" object with slightly different options');
            
            var p = new authModel('Person/1');
            $(p).on('read', function()
            {
                ok(this.get('Collaborator').href == "my/Person/1/Collaborator", 
                        'model reads authenticated resources');
            });
            // a bit of testing on xfilter as well
            p.xfilter('Id', 'Name').sync();
            
            var notUniqueModel = giz.Model.extend({ pushUnique: null, _uniq: null }),
                p1 = new notUniqueModel('Person/1'),
                p2 = new notUniqueModel('Person/1');
            
            $.when( p1.sync(), p2.sync() ).then(function()
            {
                p1.set('FullName', p2.FullName + ' Something else');
                ok(p1.data.FullName != p2.data.FullName, 'can override unique behavior');
            });
            
            start();
            
        });
        
        module('gizmo/superdesk.js');
        
        test('cross actions', function()
        {
            //Post.on('insert', function(){  })
        });
        
        // TODO test for delete xfilter
        test('differential sync', function()
        {
        //    console.log(new Post instanceof giz.AuthModel);
        });
        
    };
    
    return {run: run};
});