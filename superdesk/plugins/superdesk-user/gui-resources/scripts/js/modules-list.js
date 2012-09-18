define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('superdesk/user', 'models/user'),
    'tmpl!superdesk/user>list',
    'tmpl!superdesk/user>item',
],
function($, superdesk, giz, User)
{
    var 
    ItemView = giz.View.extend
    ({
        tagName: 'tr',
        model: null,
        init: function()
        {
            this.model.on('read update', this.render, this);
        },
        render: function()
        {
            $(this.el).tmpl('superdesk/user>item', {User: this.model.feed()});
            $('.edit', this.el).prop('model', this.model);
            return this;
        },
        update: function()
        {
            
        },
        remove: function()
        {
            
        }
    }),
    ListView = giz.View.extend
    ({
        users: null,
        init: function()
        {
            var self = this;
            this.users = new (giz.Collection.extend({ model: User, href: new giz.Url('Superdesk/User') }));
            this.users.on('read update', this.render, this);
        },
        activate: function()
        {
            var self = this;
            self.users.xfilter('*').sync();
            
            // delegate events on edit button for items 
            $(self.el).on('click', 'table tbody .edit', function()
            {
                var model = $(this).prop('model');
                // fill in values with bound model props
                $('#user-edit-modal form input', self.el).each(function()
                {
                    $(this).val( model.get( $(this).attr('name') ) );
                });
                $('#user-edit-modal', self.el).modal();
            });

            // same thing for delete
            $(self.el).on('click', 'table tbody .delete', function()
            {
                
            });
                    
        },
        render: function()
        {
            var data = {},
                self = this;
            superdesk.applyLayout('superdesk/user>list', data, function()
            {
                // new ItemView for each models 
                self.users.each(function()
                { 
                    $('table tbody', self.el).append( (new ItemView({ model: this })).render().el ); 
                });
            });
        }
        
    }),
    
    listView = new ListView({ el: '#area-main' }); 
    
    return function()
    {
        listView.activate();
    };
    
    
    
    
    
    
    
    users,
    presentation = this;
    var app = function()
    {
        $('#area-main').html(layout);
        
        users = new $.rest(superdesk.apiUrl + '/resources/Superdesk/User').xfilter('Id, Name')
            .done(function(users)
            {
                $('#area-content', layout)
                    .tmpl($("#tpl-user-list", superdesk.tmplRepo), {users: users, scriptPath: args.updateScript});
            });
    };
    
    this.view.load('user/templates/list.html').done(app);
    
    // edit button functionality 
    $(document)
    .off('click.superdesk-user-list', '.user-list .btn-primary')
    .on('click.superdesk-user-list', '.user-list .btn-primary', function(event)
    {
        presentation
            .setScript(args.updateScript)
            .setLayout(superdesk.layouts.update.clone())
            .setArgs({users: users, userId: $(this).attr('user-id')})
            .run();
        event.preventDefault();
    });
    
    $(document)
    .off('click.superdesk-user-list', '#btn-add-user')
    .on('click.superdesk-user-list', '#btn-add-user', function(event)
    {
        presentation
            .setScript(args.addScript)
            .setLayout(superdesk.layouts.update.clone())
            .setArgs({users: users})
            .run()
    })    
});

