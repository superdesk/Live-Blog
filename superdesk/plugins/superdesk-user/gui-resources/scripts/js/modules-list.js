define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('superdesk/user', 'models/user'),
    config.guiJs('superdesk/user', 'models/person'),
    'tmpl!superdesk/user>list',
    'tmpl!superdesk/user>item'
],
function($, superdesk, giz, User, Person)
{
    var 
    ItemView = giz.View.extend
    ({
        tagName: 'tr',
        model: null,
        init: function()
        {
            var self = this;
            this.model.on('read update', this.render, this);
            this.model.on('delete', function(){ self.el.remove(); })
        },
        render: function()
        {
            $(this.el).tmpl('superdesk/user>item', {User: this.model.feed()});
            $(this.el).prop('model', this.model).prop('view', this);
            $('.edit', this.el).prop('model', this.model).prop('view', this);
            $('.delete', this.el).prop('model', this.model).prop('view', this);
            return this;
        },
        update: function(data)
        {
            for( var i in data ) this.model.set(i, data[i]);
            return this.model.sync();
        },
        remove: function()
        {
            this.model.remove().sync();
        },
        hide: function()
        {
            $(this.el).addClass('hide');
        },
        show: function()
        {
            $(this.el).removeClass('hide');
        }
    }),
    ListView = giz.View.extend
    ({
        users: null,
        events:
        {
            '[data-action="search"]': { 'click': 'search' },
            '#user-add-modal [data-action="save"]': { 'click': 'addUser' },
            '#user-edit-modal [data-action="save"]': { 'click': 'updateUser' },
            '.pagination a': { 'click': 'switchPage' },
            'table tbody .edit': { 'click': 'showUpdateUser' }
        },
        /*!
         * pagination handler
         */
        switchPage: function(evt)
        {
            if( this.syncing ) return;
            if( $(evt.target).attr('data-pagination') == 'currentpages' )
            {
                this.page.offset = $(evt.target).attr('data-offset');
                this.activate();
            }
            if( $(evt.target).attr('data-pagination') == 'prev' )
            {
                var o = parseInt(this.page.offset) - parseInt(this.page.limit);
                if( o >= 0 ) { this.page.offset = o; this.activate(); } 
            }
            if( $(evt.target).attr('data-pagination') == 'next' )
            {
                var o = parseInt(this.page.offset) + parseInt(this.page.limit);
                if( o < this.page.total ) { this.page.offset = o; this.activate(); } 
            }
        },
        /*!
         * search box handler
         */
        search: function()
        {
            var self = this,
                src = $('[name="search"]', self.el).val().toLowerCase();
            if( src.length <= 1 )
            {
                //$('tr', self.el).each(function(){ $(this).prop('view') && $(this).prop('view').show(); });
                this.activate();
                $('[data-action="cancel-search"]', self.el).addClass('hide');
                return;
            }
            
            this.users._list = []
            this.syncing = true;
            this.users.xfilter('*').sync({data: {'all.ilike': '%'+src+'%'}, done: function(data){ self.syncing = false; }});
            
            /*$('tr', self.el).each(function()
            {
                var mdl = $(this).prop('model');
                if( mdl != undefined && 
                    ( mdl.get('Name').toLowerCase().indexOf(src) == -1 &&
                      mdl.get('FirstName').toLowerCase().indexOf(src) == -1 &&
                      mdl.get('EMail').toLowerCase().indexOf(src) == -1 ) )
                {
                    $(this).prop('view').hide();
                    return true;
                }
                mdl != undefined && $(this).prop('view').show();
            });*/
            $('[data-action="cancel-search"]', self.el).removeClass('hide');
        },
        /*!
         * add user handler
         */
        addUser: function()
        {
            // new model
            var self = this,
                newModel = new self.users.model();
            $('#user-add-modal form input', self.el).each(function()
            {
                var val = $(this).val();
                if( val != '' ) newModel.set($(this).attr('name'), val);
            });
            
            newModel.on('insert', function()
            {
                $('#user-add-modal', self.el).modal('hide');
                self.addItem(newModel);
            });
            
            // sync on collection href for insert
            newModel.sync(self.users.href.get())
            // some fail handler
            .fail(function(data)
            {
                eval('var data = '+data.responseText);
                var msg = '';
                for(var i in data.details.model.User)
                    msg += i+', '+data.details.model.User[i]+'. ';
                $('#user-add-modal .alert', self.el).removeClass('hide')
                    .html('<strong>'+data.message+'</strong> '+msg);
            });
        },
        /*!
         * popup update user interface
         */
        showUpdateUser: function(evt)
        {
            var $this = $(evt.target),
                model = $this.prop('model');

            var personModel = giz.Auth(new Person(model.hash().replace('User', 'Person')));
            personModel.sync();
            
            // fill in values with bound model props
            $('#user-edit-modal form input', self.el).each(function()
            {
                $(this).val( model.get( $(this).attr('name') ) || personModel.get( $(this).attr('name') ) );
            });
            $('#user-edit-modal', self.el).modal();
            $('#user-edit-modal', self.el).prop('view', $this.prop('view'));
        },
        /*!
         * update user handler
         */
        updateUser: function()
        { 
            var data = {};
            $('#user-edit-modal form input', self.el).each(function()
            {
                var val = $(this).val();
                if( val != '' ) data[$(this).attr('name')] = val;
            });
            $('#user-edit-modal', self.el).prop('view').update(data)
            .done(function()
            {
                $('#user-edit-modal', self.el).modal('hide');
            }); 
        },
        init: function()
        {
            var self = this;
            
            this.page = { limit: 25, offset: 0, total: null, pagecount: 5 };
            
            // list all users
            this.users = giz.Auth(new (giz.Collection.extend({ model: User, href: new giz.Url('Superdesk/User') })));
            //this.users.on('read update', this.render, this);
            
            $(self.el).on('keypress', '[name="search"]', function(evt)
            {
                if(evt.keyCode == 27 ) $('[data-action="cancel-search"]', self.el).trigger('click');
                if(evt.keyCode == 13) $('[data-action="search"]', self.el).trigger('click');
            });
            $(self.el).on('click', '[data-action="cancel-search"]', function(evt)
            {
                $('[name="search"]', self.el).val('');
                $('[data-action="search"]', self.el).trigger('click');
            });
            $(self.el).on('click', '.add-user', function()
            {
                $('#user-add-modal .alert', self.el).addClass('hide');
                $('#user-add-modal', self.el).modal();
            });
            $(self.el).on('click', '#user-add-modal [data-action="close"]', function()
            { 
                $('#user-add-modal', self.el).modal('hide');
            });
            $(self.el).on('click', '#user-edit-modal [data-action="close"]', function()
            { 
                $('#user-edit-modal', self.el).modal('hide'); 
            });
            $(self.el).on('click', 'table tbody .delete', function()
            {
                $('#user-delete-modal', self.el).prop('view', $(this).prop('view'));
                $('#user-delete-modal', self.el).modal();
            });
            $(self.el).on('click', '#user-delete-modal [data-action="delete"]', function()
            {
                $('#user-delete-modal', self.el).prop('view').remove();
                $('#user-delete-modal', self.el).modal('hide'); 
            });
            $(self.el).on('click', '#user-delete-modal [data-action="close"]', function()
            { 
                $('#user-delete-modal', self.el).modal('hide'); 
            });
        },
        activate: function()
        {
            var self = this;
            this.users._list = [];
            this.syncing = true;
            this.users.xfilter('*').sync({data: {limit: this.page.limit, offset: this.page.offset},
                done: function(data){ self.syncing = false; self.page.total = data.total; self.render(); }});
        },
        
        addItem: function(model)
        {
            $('table tbody', this.el).append( (new ItemView({ model: model })).render().el );
        },
        
        paginate: function()
        {
            this.page.currentpages = [];
            for( var i= -this.page.pagecount/2; i < this.page.pagecount/2; i++ )
            {
                var x = parseInt(this.page.offset) + (Math.round(i) * this.page.limit);
                if( x < 0 || x >= this.page.total ) continue;
                var currentpage = {offset: x, page: (x/this.page.limit)+1};
                if( Math.round(i) == 0 ) currentpage.className = 'active';
                this.page.currentpages.push(currentpage);
            }
        },
        
        renderList: function()
        {
            $('table tbody', this.el).html('');
            var self = this;
            this.users.each(function(){ self.addItem(this); });
        },
        
        render: function()
        {
            this.paginate();
            var data = {pagination: this.page},
                self = this;
            superdesk.applyLayout('superdesk/user>list', data, function()
            {
                // new ItemView for each models 
                self.renderList();
                self.users.on('read update', self.renderList, self);
            });
            $.superdesk.hideLoader();
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

