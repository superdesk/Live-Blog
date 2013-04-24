define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    'gizmo/superdesk/action',
    config.guiJs('superdesk/user', 'models/user'),
    config.guiJs('superdesk/user', 'models/person'),
    'utils/sha512',
    config.guiJs('media-archive', 'upload'),
    config.guiJs('superdesk/user', 'jquery/avatar'),
    'tmpl!superdesk/user>list',
    'tmpl!superdesk/user>item',
    'tmpl!superdesk/user>add',
    'tmpl!superdesk/user>update',
    'tmpl!core>layouts/footer',
    'tmpl!core>layouts/footer-static',
    'tmpl!core>layouts/footer-dinamic'
],

// TODO remove cleanup duplicate code

function($, superdesk, giz, Action, User, Person, sha, uploadCom)
{
    var 
    // TODO place in appropriate plugins
    Source = giz.Model.extend({url: new giz.Url('Data/Source')}),
    Sources = new (giz.Collection.extend({ model: Source, href: new giz.Url('Data/Source') })),
    Collaborator = giz.Model.extend
    ({
        url: new giz.Url('Data/Collaborator'),
        sources: Sources
    }),
    PersonCollaborators = giz.Collection.extend({model: Collaborator}),
    // ---
    
    RoleModel = giz.Model.extend
    ({
        url: new giz.Url('HR/User/{1}/Role/{2}'),
        update: function(userId, roleId)
        {
            var self = this;
                href = this.url.get().replace('\{1\}', userId).replace('\{2\}', roleId),
                dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); };
            return dataAdapter(href).update();
        },
        remove: function(userId, roleId)
        {
            var self = this;
            href = this.url.get().replace('\{1\}', userId).replace('\{2\}', roleId),
            dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); };
            return dataAdapter(href).remove();            
        }
    }),
    RoleCollection = giz.Collection.extend({ model: RoleModel }),
    
    PersonIcon = giz.Model.extend
    ({
        url: new giz.Url('HR/Person/{1}/MetaData/{2}/PersonIcon')
    });
    /*!
     * list item view
     */
    var ItemView = giz.View.extend
    ({
        tagName: 'tr',
        model: null,
        init: function()
        {
            var self = this;
            
            this.model.off('read.userlist').off('update.userlist').on('read.userlist update.userlist', this.render, this);
            this.model.off('delete.userlist').on('delete.userlist', function(){ self.el.remove(); });
            this.model.sync();
        },
        render: function()
        {
            var self = this,
            // set icon
                icon = new PersonIcon;
                icon.href = this.model.get('MetaDataIcon').href.replace('my/', '');
            icon.sync({data: { thumbSize: 'small'}}).done(function()
            { 
                $('figure img', self.el).attr('src', icon.get('Thumbnail').href);
            }).fail(function(){
				$('figure img', self.el).attr('src', $.avatar.get(self.model.get("EMail")));
			});
            // ---
            
            delete this.model.data['Password'];
            $(this.el).tmpl( 'superdesk/user>item', 
                {User: this.model.feed()},
                function()
                {
                    // authentication techniques
                    Action.get('modules.user.update').done(function(action)
                    { 
                        if( !action )
                        { 
                            $('button.edit', self.el).addClass('hide');
                            $('button.delete', self.el).addClass('hide');
                        }
                    });
                });
            $(this.el).prop('model', this.model).prop('view', this);
            $('[data-action="edit"]', this.el).prop('model', this.model).prop('view', this);
            $('[data-action="delete"]', this.el).prop('model', this.model).prop('view', this);
            return this;
        },
        update: function(data)
        {
            var self = this;
            // ?
                var newCollaborator = new Collaborator;
                var colabSync = newCollaborator.set('User', this.model.get('Id'))
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
            // ?
            
            delete data.Collaborator;
            
            // update role
            var newRole = new RoleModel(),
                roleRem = [],
                roleAct = data.Role,
                roleSync = $.Deferred;
            for(var i=0; i<this.model.__roles.length; i++) // remove prev roles
                roleRem.push(newRole.remove(self.model.get('Id'), self.model.__roles[i].get('Id')));
            $.when.apply($, roleRem).then(function() // add new roles
            {
                roleSync = newRole.update(self.model.get('Id'), roleAct);
                self.model.__roles = [];
            });
            delete data.Role;
            
            // hash password
            if( data.Password )
                data.Password = (new sha(data.Password, 'ASCII')).getHash('SHA-512', 'HEX');
            
            var chPassModel = giz.Auth(new giz.Model(this.model.href+'/Password'));
            chPassModel.set('Id', this.model.get('Id'));
            chPassModel.set('NewPassword', data.Password);
            var passSync = chPassModel.sync();
            
            delete data.Password;
            this.model.set(data);
            
            // TODO add this fnc in gizmo
            var personSync = this.model.sync(); 
            $.isEmptyObject(this.model.changeset) && personSync.resolve();
            return $.when(roleSync, passSync, personSync);
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
            '#user-add-modal form': { 'submit': 'addUserFormSubmit' },
            '#user-edit-modal [data-action="save"]': { 'click': 'updateUser' },
            '#user-edit-modal form': { 'submit': 'updateUserFormSubmit' },
            '.pagination a': { 'click': 'switchPage' },
            'table tbody [data-action="edit"]': { 'click': 'showUpdateUser' },
            'table tbody [data-action="delete"]': { 'click': 'showDeleteUser' },
            '.add-user': { 'click': 'showAddUser' },
            '#user-add-modal [data-action="close"]': { 'click': 'closeAddUser' },
            '#user-edit-modal [data-action="close"]': { 'click': 'closeUpdateUser' },
            '#user-delete-modal [data-action="delete"]': { 'click': 'deleteUser' },
            '#user-delete-modal [data-action="close"]': { 'click': 'closeDeleteUser' },
            "[data-action='browse']": { 'click': 'browse' },
            "[data-action='upload']": { 'change': 'showUpload' },
            "[data-action='confirm-upload']": { 'click': 'upload' },
            '[data-input="role"] li': { 'click': 'changeRole' },
            '#avatar-upload-edit': { 'click': 'editUserIcon' },
            '#avatar-upload-add': { 'click': 'addUserIcon' },
            '#avatar-upload-popover-edit a.close': { 'click' : 'closeEditUserIcon' },
            '#avatar-upload-popover-add a.close': { 'click' : 'closeAddUserIcon' }
        },
        
        editUserIcon: function(evt){ evt.preventDefault(); $("#avatar-upload-popover-edit", this.el).show(); },
        
        addUserIcon: function(evt){ evt.preventDefault(); $("#avatar-upload-popover-add", this.el).show(); },
        
        closeEditUserIcon: function(evt) { evt.preventDefault(); $("#avatar-upload-popover-edit", this.el).hide(); },
        
        closeAddUserIcon: function(evt) { evt.preventDefault(); $("#avatar-upload-popover-add", this.el).hide(); },
        
        closeUpdateUser: function(){ $('#user-edit-modal', this.el).modal('hide'); },
        
        closeAddUser: function(){ $('#user-add-modal', this.el).modal('hide'); },
        
        closeDeleteUser: function(){ $('#user-delete-modal', this.el).modal('hide'); },
        
        // -- upload
        browse: function(evt)
        {
            $(evt.target).siblings('[type="file"]').trigger('click');
        },
        uploadEndPoint: $.superdesk.apiUrl+'/resources/my/HR/User/'+
            localStorage.getItem('superdesk.login.id')+
            '/MetaData/Upload?thumbSize=large&X-Filter=*&Authorization='+ localStorage.getItem('superdesk.login.session'),
        showUpload: function(evt)
        {
            var val = $(evt.currentTarget).val(),
                file = val.split(/[\\/]/);
            $('[data-value="upload-filename"]').val(file[file.length-1]);
            $('[data-action="confirm-upload"]').removeClass("disabled");
        },
        upload: function(evt)
        {
            var uploadInput = $(evt.target).siblings('[type="file"]'),
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
                    
                    $('#avatar-upload-popover-edit a.close', self.el).trigger('click');
                    $('#avatar-upload-popover-add a.close', self.el).trigger('click');
                    uploadInput.parents('form:eq(0)').find('figure.user-avatar img').attr('src', content.Thumbnail.href);
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
            
            // show role select val
            var firstRole = $('#user-edit-modal form [data-input="role"] li:eq(0)');
            $('#user-add-modal form [data-input="role"] [data-selected-value]', self.el)
                .attr('data-selected-value', firstRole.attr('data-value'))
                .text(firstRole.text());
            
            $('#user-add-modal figure.user-avatar img', this.el).attr('src', config.content_url+'/lib/core/images/default_profile_3_bigger.png');
        },
        
        /*!
         * passing along view prop
         */
        showDeleteUser: function(evt)
        {
            evt.preventDefault();
            $('#user-delete-modal', this.el).prop('view', $(evt.currentTarget).prop('view')); 
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
         * change role select handler
         */
        changeRole: function(evt)
        {
            var clicked = $(evt.currentTarget); 
            clicked.parents('[data-input="role"]:eq(0)').find('[data-selected-value]')
                .attr('data-selected-value', clicked.attr('data-value'))
                .text(clicked.text());
        },
        /*!
         * 
         */
        addUserFormSubmit: function(evt)
        {
            evt.preventDefault();
            $('#user-add-modal [data-action="save"]').trigger('click');
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
            var pass = newModel.get('Password');
            pass && pass.length && newModel.set('Password', (new sha(newModel.get('Password'), 'ASCII')).getHash('SHA-512', 'HEX'));

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
                //if( $('#user-add-modal form input#inputCollaborator:checked').length )
                //{
                    var newCollaborator = new Collaborator;
                    newCollaborator.set('User', newModel.get('Id'))
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
                //}
                //else h.call(this);
                // ---   
                    
               // insert role
               var newRole = new RoleModel;
               newRole.update(newModel.get('Id'), $('#user-add-modal form [data-input="role"] [data-selected-value]', self.el).attr('data-selected-value'));
                
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
         * 
         */
        updateUserFormSubmit: function(evt)
        {
            evt.preventDefault();
            $('#user-edit-modal [data-action="save"]').trigger('click');
        },
        
        /*!
         * popup update user interface
         */
        showUpdateUser: function(evt)
        {
            evt.preventDefault();
            var $this = $(evt.currentTarget),
                model = $this.prop('model');

            $('#user-edit-modal figure.user-avatar img', this.el).attr('src', config.content_url+'/lib/core/images/default_profile_3_bigger.png');
            $('.control-group').removeClass('error');
            
            var personModel = /*giz.Auth(*/new Person(model.hash().replace('User', 'Person').replace('my/', ''))/*)*/,
                roleCollection = new RoleCollection({href: new giz.Url('HR/User/'+model.get('Id')+'/Role')});
                checkColab = function(id)
                {
                    $('#user-edit-modal form input#inputCollaborator', self.el).attr('checked', false);
                    var c = new PersonCollaborators({ href: new giz.Url('HR/User/'+id+'/Collaborator')});
                    // check collaborator status
                    c.xfilter('Id,Source.Id,Source.Name').sync().done(function()
                    {  
                        c.each(function()
                        { 
                            if( this.get('Source').Name == 'internal' )
                            {
                                model.__collaborator = this;
                                $('#user-edit-modal form input#inputCollaborator', self.el).attr('checked', true);
                                return false;
                            }
                        });
                    });
                };
            
            // get user role and display it
            model.__roles = [];
            roleCollection.xfilter('*').sync({data: {limit: 1}}).done(function()
            { 
                roleCollection.each(function()
                { 
                    model.__roles.push(this);
                    $('#user-edit-modal form [data-input="role"] [data-selected-value]', self.el)
                        .attr('data-selected-value', this.get('Id'))
                        .text(this.get('Name'));
                });
            });
            
            personModel.sync().done(function()
            {
                var p = personModel.get('Id'),
                    person = personModel.feed(),
                    m = personModel.get('MetaDataIcon');
                //checkColab(p);

                m.sync({data:{thumbSize: 'huge'}})
                    .done(function()
                    { 
                        $('#user-edit-modal figure.user-avatar img', self.el).attr('src', m.get('Thumbnail').href); 
                    });
                
                $('#user-edit-modal form input', self.el).each(function()
                {
                    var val = model.get( $(this).attr('name') ) || person[$(this).attr('name')];
                    !$.isObject(val) && $(this).is(':not(:checkbox)') && $(this).val( val );
                });

            })
            .fail(function()
            {
                /*checkColab(model.get('Id'));*/
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
                self = this,
                userItemView = $('#user-edit-modal', self.el).prop('view');
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
                if( $(this).is(':checkbox') ) data[name] = true;
                if( name && val != '' ) data[name] = val;
                // deleted value
                if( userItemView.model.get(name) && val == '' ) data[name] = '';
            });
            data['Role'] = $('#user-edit-modal form [data-input="role"] [data-selected-value]', self.el).attr('data-selected-value');
            
            /*
             * for( var i in this.model.data )
                if( i != 'Id' && this.model.data[i] && !data[i] ) data[i] = '';
             */
            
            // checking email
            if( data.EMail && !self.checkEmail(data.EMail) )
            {
                $('#user-edit-modal form input#inputEmail', self.el).focus().parents('.control-group:eq(0)').addClass('error');
                return false;
            }
            
            userItemView.update(data)
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
                    pi.sync(piurl).done(function()
                    {
                        $('#user-edit-modal', self.el).prop('view').model.triggerHandler('update');
                        self._latestUpload = null; 
                    });
                }
                $('#user-edit-modal', self.el).modal('hide');
            }); 
        },
        _roleList: null,
        _dialogs: {add: $('<span />'), update: $('<span />') },
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
            this.users = giz.Auth(new (giz.Collection.extend({ model: User, href: new giz.Url('HR/User') })));
            //this.users = new (giz.Collection.extend({ model: User, href: new giz.Url('HR/User') }));
            this._resetEvents = false;
            
            // get available roles and add them to templates
            this._roleList = new RoleCollection({href: localStorage.getItem('superdesk.login.selfHref').replace('my/', '')+'/Role'});
            this._roleList.xfilter('*').sync().done(function()
            {
                $.tmpl('superdesk/user>add', {Roles: self._roleList.feed()}, function(e, o){ self._dialogs.add.append(o); });
                $.tmpl('superdesk/user>update', {Roles: self._roleList.feed()}, function(e, o){ self._dialogs.update.append(o); });    
            });
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
            $('table tbody', this.el).append( (new ItemView({ model: model })).el );
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
                
                $(self.el).append(self._dialogs.add);
                $(self.el).append(self._dialogs.update);
                
                // authentication techniques
                Action.get('modules.user.update').done(function(action)
                { 
                    if( !action ){ $('.add-user', self.el).addClass('hide'); }
                });
                $.isFunction(cb) && cb.apply(self);
                // new ItemView for each models
                self.renderList();
                /*if( !self.users.__hasUserListEvents )
                {
                    self.users.on('read update', self.renderList, self);
                    self.users.__hasUserListEvents = true;
                }*/
            });
            $.superdesk.hideLoader();
        }
        
    }),
    
    listView = new ListView(); 
    
    return function(){ listView.activate(); };
});

