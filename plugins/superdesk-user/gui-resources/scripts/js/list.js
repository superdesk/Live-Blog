define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('superdesk/user', 'models/user'),
    config.guiJs('superdesk/user', 'models/person'),
    'utils/sha512',
    config.guiJs('media-archive', 'upload'),
    config.guiJs('superdesk/user', 'jquery/avatar'),
    'tmpl!superdesk/user>list',
    'tmpl!superdesk/user>item',
    'tmpl!superdesk/user>add',
    'tmpl!superdesk/user>update'
],

// TODO remove cleanup duplicate code

function($, superdesk, giz, User, Person, sha, uploadCom)
{
    var 
    // TODO place in appropriate plugins
    Source = giz.Model.extend({url: new giz.Url('Superdesk/Source')}),
    Sources = new (giz.Collection.extend({ model: Source, href: new giz.Url('Superdesk/Source') })),
    Collaborator = giz.Model.extend
    ({
        url: new giz.Url('Superdesk/Collaborator'),
        sources: Sources
    }),
    PersonCollaborators = giz.Collection.extend({model: Collaborator}),
    // ---
    
    PersonIcon = giz.Model.extend
    ({
        url: new giz.Url('Superdesk/Person/{1}/MetaData/{2}/PersonIcon')
    });
    
    var ItemView = giz.View.extend
    ({
        tagName: 'tr',
        model: null,
        init: function()
        {
            var self = this;
            this.model.on('read update', this.render, this);
            this.model.on('delete', function(){ self.el.remove(); });
        },
        render: function()
        {
            delete this.model.data['Password'];
            $(this.el).tmpl('superdesk/user>item', {User: this.model.feed()});
            $(this.el).prop('model', this.model).prop('view', this);
            $('.edit', this.el).prop('model', this.model).prop('view', this);
            $('.delete', this.el).prop('model', this.model).prop('view', this);
            return this;
        },
        update: function(data)
        {
            /*!
             * Set all the data at once, caz a nasty bug in set model in gizmojs.
             */
            if( this.model.__collaborator && !data.Collaborator )
                var colabSync = this.model.__collaborator.remove().sync();
            
            if( !this.model.__collaborator && data.Collaborator )
            {
                var newCollaborator = new Collaborator;
                var colabSync = newCollaborator.set('Person', this.model.get('Id'))
                    .sources.xfilter('*').sync().done(function()
                    {
                        newCollaborator.sources.each(function()
                        {
                            if(this.get('Name') == 'internal')
                            {
                                newCollaborator.set('Source', this.get('Id'));
                                return false;
                            }
                        });
                        newCollaborator.sync(newCollaborator.url.get()); 
                    });
            }
            
            delete this.model.__collaborator;
            delete data.Collaborator;
            
            // hash password
            if( data.Password )
                data.Password = (new sha(data.Password, 'ASCII')).getHash('SHA-512', 'HEX');
            
            var chPassModel = giz.Auth(new giz.Model(this.model.href+'/ChangePassword'));
            chPassModel.set('Id', this.model.get('Id'));
            chPassModel.set('Password', data.Password);
            var passSync = chPassModel.sync();
            
            delete data.Password;
            this.model.set(data);
            
            // TODO add this fnc in gizmo
            var personSync = this.model.sync();
            $.isEmptyObject(this.model.changeset) && personSync.resolve();
            return $.when(colabSync, passSync, personSync);
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
            '[name="search"]': { 'keypress': 'key2Search' },
            '[data-action="search"]': { 'click': 'search' },
            '[data-action="cancel-search"]': { 'click': 'cancelSearch' },
            '#user-add-modal [data-action="save"]': { 'click': 'addUser' },
            '#user-edit-modal [data-action="save"]': { 'click': 'updateUser' },
            '.pagination a': { 'click': 'switchPage' },
            'table tbody .edit': { 'click': 'showUpdateUser' },
            'table tbody .delete': { 'click': 'showDeleteUser' },
            '.add-user': { 'click': 'showAddUser' },
            '#user-add-modal [data-action="close"]': { 'click': 'closeAddUser' },
            '#user-edit-modal [data-action="close"]': { 'click': 'closeUpdateUser' },
            '#user-delete-modal [data-action="delete"]': { 'click': 'deleteUser' },
            '#user-delete-modal [data-action="close"]': { 'click': 'closeDeleteUser' },
            "[data-action='browse']": { 'click': 'browse' },
            "[data-action='upload']": { 'change': 'upload' }
        },
        
        closeUpdateUser: function(){ $('#user-edit-modal', this.el).modal('hide'); },
        
        closeAddUser: function(){ $('#user-add-modal', this.el).modal('hide'); },
        
        closeDeleteUser: function(){ $('#user-delete-modal', this.el).modal('hide'); },
        
        // -- upload
        browse: function(evt)
        {
            $(evt.target).siblings('[type="file"]').trigger('click');
        },
        uploadEndPoint: $.superdesk.apiUrl+'/resources/my/Archive/MetaData/Upload?thumbSize=large&X-Filter=*&Authorization='+ localStorage.getItem('superdesk.login.session'),
        upload: function(evt)
        {
            var uploadInput = $(evt.target),
                files = uploadInput[0].files,
                self = this; 
            for( var i=0; i<files.length; i++)
            {
                xhr = uploadCom.upload( files[i], 'upload_file', this.uploadEndPoint,
                        // display some progress type visual
                        function(){ $('[data-action="browse"]', self.el).val(_('Uploading...')); }, 'json');
                xhr.onload = function(event) 
                { 
                    $('[data-action="browse"]', this.el).val(_('Browse'));
                    try // either get it from the responseXML or responseText
                    {
                        var content = JSON.parse(event.target.responseText);
                    }
                    catch(e)
                    {
                        var content = JSON.parse(event.target.response);
                    }
                    if(!content) return;
                    $(self).triggerHandler('uploaded', [content.Id]);
                    self._latestUpload = content;
                    
                    uploadInput.siblings('.user-image').html('<img src="'+content.Thumbnail.href+'" />');
                };
            }
            $('[data-action="upload"]', this.el).val('');
        },
        _latestUpload: null,
        // -- upload
        
        showAddUser: function()
        { 
            var self = this;
            $('#user-add-modal .alert', this.el).addClass('hide'); 
            $('#user-add-modal', this.el).modal();
            $('#user-add-modal form', this.el).trigger('reset');
            $('#user-add-modal', this.el).on('shown', function()
            { 
                $('#user-add-modal form input:eq(0)', this.el).focus(); 
            })
            .on('close', function(){ self._latestUpload = null; });
        },
        
        showDeleteUser: function(evt)
        { 
            $('#user-delete-modal', this.el).prop('view', $(evt.target).prop('view')); 
            $('#user-delete-modal', this.el).modal(); 
        },
        
        key2Search: function(evt)
        {
            if(evt.keyCode == 27 ) 
            { 
                $('[data-action="cancel-search"]', this.el).trigger('click'); 
                evt.preventDefault(); 
            }
            if(evt.keyCode == 13) $('[data-action="search"]', this.el).trigger('click');
        },
        cancelSearch: function()
        {
            $('[name="search"]', this.el).val('');
            $('[data-action="search"]', this.el).trigger('click');
        },
        
        /*!
         * pagination handler
         */
        switchPage: function(evt)
        {
            switch(true)
            {
                case this.syncing: return; 
                case $(evt.target).attr('data-pagination') == 'currentpages':
                    this.page.offset = $(evt.target).attr('data-offset');
                    this.refresh();
                    break;
                case $(evt.target).attr('data-pagination') == 'prev':
                    var o = parseInt(this.page.offset) - parseInt(this.page.limit);
                    if( o >= 0 ) { this.page.offset = o; this.refresh(); } 
                    break;
                case $(evt.target).attr('data-pagination') == 'next':
                    var o = parseInt(this.page.offset) + parseInt(this.page.limit);
                    if( o < this.page.total ) { this.page.offset = o; this.refresh(); } 
                    break;
                case $(evt.target).attr('data-pagination') == 'first':
                    this.page.offset = 0; 
                    this.refresh();
                    break;
                case $(evt.target).attr('data-pagination') == 'last':
                    this.page.offset = this.page.total - (this.page.total % this.page.limit); 
                    this.refresh();
                    break;
                case $(evt.target).attr('data-ipp') > 0:
                    this.page.limit = $(evt.target).attr('data-ipp');
                    this.refresh();
                    break;
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
                this.refresh();
                $('[data-action="cancel-search"]', self.el).addClass('hide');
                return;
            }
            
            this.users._list = [];
            this.syncing = true;
            this.users.xfilter('*').sync({data: {'all.ilike': '%'+src+'%'}, done: function(data){ self.syncing = false; }});
            
            $('[data-action="cancel-search"]', self.el).removeClass('hide');
        },
        
        deleteUser: function()
        {
            $('#user-delete-modal', this.el).prop('view').remove();
            $('#user-delete-modal', this.el).modal('hide'); 
            this.refresh();
        },
        checkPass: function(modal)
        {
            var pass = $(modal+' form input#inputPass', self.el).val();
            if( pass.length > 0 && $(modal+' form input#inputPassConfirm', self.el).val() !== pass ) return false;
            return true;
        },
        checkEmail: function(email)
        {
            return /^([_a-zA-Z0-9-]+)(\.[_a-zA-Z0-9-]+)*@([a-zA-Z0-9-]+\.)+([a-zA-Z]+)$/.test(email);
        },
        /*!
         * add user handler
         */
        addUser: function()
        {
            // new model
            var self = this,
                newModel = giz.Auth(new self.users.model());
            
            if( !self.checkPass('#user-add-modal') ) 
            {
                $('#user-add-modal .alert', self.el).removeClass('hide')
                    .html(_('Password mismatch!')+'');
                return false;
            }
            $('#user-add-modal form input', self.el).each(function()
            {
                var val = $(this).val(),
                    name = $(this).attr('name');
                if( name && !$(this).attr('data-ignore') && val != '' ) newModel.set(name, val);
            });

            // checking email
            if( newModel.get('EMail') && !self.checkEmail(newModel.get('EMail')) )
            {
                $('#user-add-modal form input#inputEmail', self.el).focus().parents('.control-group:eq(0)').addClass('error');
                return false;
            }
            
            // hashing password
            newModel.set('Password', (new sha(newModel.get('Password'), 'ASCII')).getHash('SHA-512', 'HEX'));

            newModel.on('insert', function()
            {
                $('#user-add-modal', self.el).modal('hide');
                self.addItem(newModel);
                delete newModel.data['Password'];

                var h = function()
                {
                    // scroll to last page
                    var e = new $.Event;
                    e.target = $('<a data-offset="'+String(Math.floor(self.page.total/self.page.limit)*self.page.limit)+'" data-pagination="currentpages" />');
                    self.switchPage(e);
                };
                
                // set user image
                if( self._latestUpload )
                {
                    var pi = new PersonIcon,
                        piurl = PersonIcon.prototype.url.get().replace('\{1\}', newModel.get('Id')).replace('\{2\}', self._latestUpload.Id);
                    pi.sync(piurl).done(function(){ self._latestUpload = null; });
                }
                
                // TODO very uncool
                if( $('#user-add-modal form input#inputCollaborator:checked').length )
                {
                    var newCollaborator = new Collaborator;
                    newCollaborator.set('Person', newModel.get('Id'))
                        .on('insert', h, this)
                        .sources.xfilter('*').sync().done(function()
                        {
                            newCollaborator.sources.each(function()
                            {
                                if(this.get('Name') == 'internal')
                                {
                                    newCollaborator.set('Source', this.get('Id'));
                                    return false;
                                }
                            });
                            newCollaborator.sync(newCollaborator.url.get()); 
                        });
                }
                else h.call(this);
                // ---   
                
            });
            
            // sync on collection href for insert
            newModel.xfilter('Id').sync(self.users.href.get())
            // some fail handler
            .fail(function(data)
            {
                eval('var data = '+data.responseText);
                var msg = '';
                if(data.details) for(var i in data.details.model.User)
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

            $('#user-edit-modal figure.user-image', this.el).html('');
            
            var personModel = giz.Auth(new Person(model.hash().replace('User', 'Person')));
            personModel.sync().done(function()
            {
                var p = personModel.get('Id'),
                    person = $.avatar.parse(personModel, 'Email'),
                    c = new PersonCollaborators({ href: new giz.Url('Superdesk/User/'+p+'/Collaborator')}),
                    m = personModel.get('MetaData');
                
                // display user image
//                m.sync({ data: { thumbSize: 'large' }}).done(function()
//                {
//                    $('#user-edit-modal figure.user-image', self.el).html('<img src="'+m.get('Thumbnail').href+'" />');
//                });
                
                // check collaborator status
                c.xfilter('Id,Source.Id,Source.Name').sync().done(function()
                {  
                    c.each(function()
                    { 
                        if( this.get('Source').Name == 'internal' )
                        {
                            model.__collaborator = this;
                            $('#user-edit-modal form input#inputCollaborator', self.el).attr('checked', true);
                        }
                    });
                });

                $('#user-edit-modal figure.user-image', self.el).html(person['Avatar']);
                $('#user-edit-modal form input', self.el).each(function()
                {
                    var val = model.get( $(this).attr('name') ) || person[$(this).attr('name')];
                    !$.isObject(val) && $(this).val( val );
                });

            })
            .fail(function()
            {
                $('#user-edit-modal form input', self.el).each(function()
                {
                    $(this).val( model.get( $(this).attr('name') ) );
                });
            });
            
            var self = this;
            // fill in values with bound model props
            $('#user-edit-modal .alert', this.el).addClass('hide');
            $('#user-edit-modal', self.el).modal();
            $('#user-edit-modal', this.el)
                .on('shown', function(){ $('#user-add-modal form input:eq(0)', this.el).focus(); })
                .on('close', function(){ self._latestUpload = null; });
            $('#user-edit-modal', self.el).prop('view', $this.prop('view'));
        },
        /*!
         * update user handler
         */
        updateUser: function()
        { 
            var data = {},
                self = this;
            if( !self.checkPass('#user-edit-modal') ) 
            {
                $('#user-edit-modal .alert', self.el).removeClass('hide')
                    .html(_('Password mismatch!')+'');
                return false;
            }
            $('#user-edit-modal form input', self.el).each(function()
            {
                var val = $(this).val(),
                    name = $(this).attr('name');
                if( $(this).is(':checkbox') && $(this).is(':not(:checked)') ) return true;
                if( name && val != '' ) data[name] = val;
                
            });
            
            // checking email
            if( data.EMail && !self.checkEmail(data.EMail) )
            {
                $('#user-edit-modal form input#inputEmail', self.el).focus().parents('.control-group:eq(0)').addClass('error');
                return false;
            }
            
            $('#user-edit-modal', self.el).prop('view').update(data)
            .fail(function(data)
            {
                eval('var data = '+data.responseText);
                var msg = '';
                if(data.details) for(var i in data.details.model)
                {
                    var msge = data.details.model[i].error && $.type(data.details.model[i].error.error) == 'array' 
                            ? data.details.model[i].error.error.join(', ') : false;
                    if(!msge) 
                    {
                        msge = '';
                        for(var j in data.details.model[i]) msge += j+': '+data.details.model[i][j]+'. ';
                    }
                    msg += '<em>'+i+'</em> - '+msge+'. ';
                }
                $('#user-edit-modal .alert', self.el).removeClass('hide')
                    .html('<strong>'+data.message+'</strong> '+msg);  
            })
            .done(function()
            {
                if( self._latestUpload )
                {
                    var pi = new PersonIcon,
                        piurl = PersonIcon.prototype.url.get().replace('\{1\}', $('#user-edit-modal', self.el).prop('view').model.get('Id')).replace('\{2\}', self._latestUpload.Id);
                    pi.sync(piurl).done(function(){ self._latestUpload = null; });
                }
                
                $('#user-edit-modal', self.el).modal('hide');
            }); 
        },
        init: function()
        {
            var self = this;
            this.page = 
            { 
                limit: 25, 
                offset: 0, 
                total: null, 
                pagecount: 5, 
                ipp: [25, 50, 100], 
                isipp: function(chk, ctx){ return ctx.current() == ctx.get('limit') ? "disabled" : ""; }
            };
            this.users = giz.Auth(new (giz.Collection.extend({ model: User, href: new giz.Url('Superdesk/User') })));
            this._resetEvents = false;
        },
        refresh: function(opts)
        {
            var self = this;
            this.users._list = [];
            this.syncing = true;
            var options = {data: {limit: this.page.limit, offset: this.page.offset, asc: 'name'}, done: function(data)
            { 
                self.syncing = false; 
                self.page.total = data.total;
            }};
            return this.users.xfilter('*').sync(options).done(function(){ self.render(); });
        },
        activate: function()
        {
            var self = this;
            return this.refresh().done(function()
            {
                $(superdesk.layoutPlaceholder).html(self.el);
                if( self._resetEvents ) self.resetEvents();
                self._resetEvents = true;
            });
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
        tagName: 'span',
        render: function(cb)
        {
            this.paginate();
            var data = {pagination: this.page},
                self = this;
            $.tmpl('superdesk/user>list', data, function(e, o)
            {
                self.el.html(o);
                $.tmpl('superdesk/user>add', {}, function(e, o){ $(self.el).append(o); });
                $.tmpl('superdesk/user>update', {}, function(e, o){ $(self.el).append(o); });
                $.isFunction(cb) && cb.apply(self);
                // new ItemView for each models
                self.renderList();
                self.users.on('read update', self.renderList, self);
            });
            $.superdesk.hideLoader();
        }
        
    }),
    
    listView = new ListView(); 
    
    return function(){ listView.activate(); };
});

