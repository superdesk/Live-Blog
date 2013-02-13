define([
	'jquery',
	'gizmo/superdesk',
	config.guiJs('superdesk/user', 'models/person'),
    config.guiJs('livedesk', 'action'),
	'jquery/rest',
	'jquery/superdesk',
	'jquery/avatar',
	config.guiJs('livedesk', 'models/collaborators'),
	config.guiJs('livedesk', 'models/blog'),
	config.guiJs('livedesk', 'models/collaborator'),
	config.guiJs('livedesk', 'models/blog-collaborator-types'),
	'tmpl!livedesk>layouts/livedesk',
	'tmpl!livedesk>layouts/blog',
    'tmpl!livedesk>layouts/footer',
    'tmpl!livedesk>layouts/footer-static',
    'tmpl!livedesk>layouts/footer-dinamic',	
	'tmpl!livedesk>manage-collaborators',
	'tmpl!livedesk>manage-collaborators/internal-collaborator',
	'tmpl!livedesk>manage-collaborators/internal-collaborators',
	'tmpl!livedesk>manage-collaborators/add-internal-collaborator',
	'tmpl!livedesk>manage-collaborators/blog-collaborator-types'
	], function ($, Gizmo, Person, Action ) {

    var 
    userImages = [],
    addUserImages = function()
    {
        for(var i=0; i<userImages.length; i++) 
            mainManageCollaboratosView.el.find('[data-user-id="'+userImages[i].UserId+'"] figure')
                .html('<img src="'+userImages[i].Thumbnail+'" />');
    },
	/*!
	 * A default view witch can handle the sort process
	 *    the model will be added in the views in a sorted fashion.
	 * Implementes need
	 *   Initialize:
	 *     the _view propertie empty
	 */ 
	SortedView = Gizmo.View.extend({
		_views: [],
		// default key for sorting the objects
		sortProperty: 'Name',
		sortOne: function(model, view){
			var self = this,
				dir = "after", 
				from,
				count = self._views.length;
			if(!count) {
				self._views = [view];
			} else {
				if( dir == "after") {
					from = self._views[self._views.length-1];
					self._views.push(view);
				} else {
					from = self._views[0];
					self._views.unshift(view);
				}
				/*!
				 * Sort function by getting sortProperty within model from the view
				 * key of the string property to be sorted can be specified in the sortProperty
				 */
				self._views.sort(function(a,b){
					return a.model.get(self.sortProperty).toLowerCase() > b.model.get(self.sortProperty).toLowerCase();
				});
				pos = self._views.indexOf(view);
				if(pos === 0 ) {
					from = self._views[1];
					dir = "before";
				} else if( pos === (self._views.length -1) ) {
					from = self._views[self._views.length - 2];
					dir = "after";
				} else {
					from = self._views[pos-1];
					dir = "after";
				}
				from.el[dir](view.el);
			}
			return view;
		}
	}),
	AddInternalCollaboratorView = Gizmo.View.extend({
		events: {
			'.select-colaborator': { change: 'addInternalCollaborator' }
		},	
		init: function(){
			this.render();
		},
		render: function(){
		    
		    var data = this.model.feed('', true),
		        self = this;
		    (new Person(Person.prototype.url.get()+'/'+self.model.get('User').get('Id')))
            .one('read', function()
            { 
                var meta = this.get('MetaDataIcon')
                meta.sync({data:{ thumbSize: 'medium' }}).done(function()
                {  
                    userImages.push({UserId: self.model.get('User').get('Id'), Thumbnail: meta.get('Thumbnail').href});
                    self.el.find('figure[data-user-id="'+self.model.get('User').get('Id')+'"]')
                        .html('<img src="'+meta.get('Thumbnail').href+'" />');
                });
            })
            .sync();
		    
			this.el.tmpl('livedesk>manage-collaborators/add-internal-collaborator', data, addUserImages );
		},
		addInternalCollaborator: function(evt) {
			var self = this;
			if($(evt.target).is(':checked')) {
				self.model.set({'Type': 'Collaborator'}, {silent: true});
				self._parent._addPending.push(self.model);
			} else {
				pos = self._parent._addPending.indexOf(self.model);
				if(pos !== -1) {
					self._parent._addPending.splice(pos,1);
				}
			}
		}
	}),
	AddInternalCollaboratorsView = Gizmo.View.extend({
		events: {
			'.save': { click: 'addPendingCollaborators'},
			'[name="internalCollaboratorSelectAll"]': { change: 'toggleCollaborators' },
			'.searchbox': { keyup: 'searchWait' }
		},
		stillTyping: false,

		init: function(){
			var self = this;
			self.collection
				.on('read', self.render, self)
				.on('modified', self.render, self);

		},
		searchWait: function(evt) {
			var self = this, el = $(evt.target);
			clearTimeout($(el).data("typing"));
			$(el).data("typing", setTimeout(function(){
				var val = $(el).val();
				if( $(el).data('previous') !== val )
					self.search(val);
				$(el).data('previous', val);
			}, 200));
		},
		search: function(searchText) {
			var self = this;
			self.collection
				.xfilter('Id,Name,User.Id,User.FullName,User.EMail')
				.limit(self.collection.config("limit"))
				.param('%'+searchText+'%','qu.firstName.ilike')
				.sync();
		},
		refresh: function() {
			var self = this;
			self._addPending = [];
			self.el.find('.searchbox').val('');
			self.collection
				.xfilter('Id,Name,User.Id,User.FullName,User.EMail')
				.limit(self.collection.config("limit"))
				.sync();
		},
		addOne: function(model) {
			if( (model.get('User')._clientId !== undefined) && ($.inArray(model.get('User').get('Id'), this._parent.internalColabsList) === -1) ) {
				var self = this,
					view = new AddInternalCollaboratorView({ model: model, _parent: self});
					self.el.find('.internal-collaborators').append(view.el);
			}
		},
		addAll: function(evt, data) {
			for(var i=0, count = data.length; i<count; i++) {
				this.addOne(data[i]);
			}
		},
		render: function(evt, data) {
			var self = this;
			if(!data)
				data = self.collection._list;
			self.el.find('.internal-collaborators').html('');
			self.addAll(evt, data);
		},
		addPendingCollaborators: function(evt) {
			var self = this;
			self._parent.addAllNew(evt, self._addPending).save(evt, self._addPending);
		},
		toggleCollaborators: function(evt) {
			var self = this;
			self.el.find('.internal-collaborators [type="checkbox"]').prop('checked', $(evt.target).is(':checked')).change();
		}
	}),
	TypesCollaboratorView = Gizmo.View.extend({
		events: {
			'.dropdown-menu li': {
				click: 'selectType'
			}
		},
		init: function(){
			var self = this;
			if(self.collection.desynced) {
				self.collection
					.on('read update',self.render, self);
			} else {
				self.render();
			}
		},
		render: function(){
			var self = this,
				data = { 
					Selected: self.model.get("Type"),
					BlogCollaaboratorTypes: self.collection.feed()
				};
			self.el.tmpl("livedesk>manage-collaborators/blog-collaborator-types",data);
		},
		selectType: function(evt){
			var self = this,
				blogCollaboratorType = $(evt.target).attr('data-name');
			self.model.saveType(blogCollaboratorType, self.updateTypeHref).done(function(){
				self.el.find('.dropdown-toggle span').text(blogCollaboratorType);
			});
		}
	}),
	ManageInternalCollaboratorView = Gizmo.View.extend({
		events: {
			'a[href="#delete_internal_collaborator"]': { click: 'delete' }
		},
		init: function(){
			this.render();
		},
		render: function(){
			var self = this;
			
			(new Person(Person.prototype.url.get()+'/'+self.model.get('User').get('Id')))
            .one('read', function()
            { 
                var meta = this.get('MetaDataIcon')
                meta.sync({data:{ thumbSize: 'medium' }}).done(function()
                {  
                    userImages.push({UserId: self.model.get('User').get('Id'), Thumbnail: meta.get('Thumbnail').href});
                    self.el.find('figure[data-user-id="'+self.model.get('User').get('Id')+'"]')
                        .html('<img src="'+meta.get('Thumbnail').href+'" />');
                });
            })
            .sync();
			this.el.tmpl('livedesk>manage-collaborators/internal-collaborator', self.model.feed('', true), function(){
				addUserImages();
				self.typesCollaaborator = new TypesCollaboratorView({
					el: self.el.find('.dropdown-simple'),
					collection: self._parent.blogTypesCollaborator,
					updateTypeHref: self._parent.collection.href, // need to pass this for correct update href
					model: self.model
				});
			});
		},
		delete: function(){
			var self = this;
			$('#delete_internal_collaborator')
				.find('#delete_collaborator_name').text(self.model.get('Name')).end()
				.find('.btn-primary').off(self.getEvent("click")).on(self.getEvent("click"), function(evt){
					evt.preventDefault();
					self._parent.remove(evt, self.model);
					
					// remove from list of current internal colabs
					var idx = $.inArray(self.model.get('User').get('Id'), self._parent.internalColabsList); 
					idx !== -1 && self._parent.internalColabsList.splice(idx, 1);
					// ---
					
					delete self.model.get('User').internalCollaboratorView;
					self.el.fadeTo(900, '0.1', function(){
						self.el.remove();
					});
					//$("#delete_internal_collaborator").modal('hide');			
				});
		}
	}),
	ManageInternalCollaboratorsView = SortedView.extend({
		events: {
			'[href="#addCollaborator2"]': { click: 'addInternalCollaborators' }
		},
		init: function(){
			var self = this;
			self.addInternalCollaboratorsView = null;
			self._views = [];
			self._addPending = [];
			self._deletePending = [];
			self._internalColabsList = [];
			self.collection
				.one('read', self.render, self)
				.xfilter('Id,Type,Name,User.Id,User.FullName,User.EMail')
				//.limit(self.collection.config("limit"))
				.sync();
			self.blogTypesCollaborator = new Gizmo.Register.BlogCollaaboratorTypes();
			self.blogTypesCollaborator.sync();
		},
		addOne: function(model) {
			var self = this,
				view = new ManageInternalCollaboratorView({ model: model, _parent: self});
			//model.get('User').internalCollaboratorView = view;
			self._internalColabsList.push(model.get('User').get('Id'));
			self.el.find('.plain-table').prepend(view.el);
			self.sortOne(model, view);
		},
		addAllNew: function(evt, data) {
			for(var i=0, count = data.length; i<count; i++) {
				this.addOne(data[i]);
				this._addPending.push(data[i]);
			}
			return this;
		},
		addAll: function(evt, data) {
			for(var i=0, count = data.length; i<count; i++) {
				this.addOne(data[i]);
			}
		},
		render: function(evt, data) {
			if(!this.checkElement())
				return;
			var self = this;
			self.el.tmpl('livedesk>manage-collaborators/internal-collaborators',function(){
				self.addAll(evt, self.collection._list);
			});
		},
		addInternalCollaborators: function(evt) {
			var self = this;
			if(!self.addInternalCollaboratorsView) {
				self.addInternalCollaboratorsView = new AddInternalCollaboratorsView({
					collection: self.collectionPotentialCollaborator,//Gizmo.Auth(new Gizmo.Register.Collaborators()),
					el: $('#addCollaborator2'),
					_parent: self
				});
			}
			self.addInternalCollaboratorsView.refresh();
		},
		save: function(evt, data) {
			var self = this;
			self.collection.add(data);
			return this;
		},
		remove: function(evt, model) {
			var self = this;
			self.collection.remove([model])
		}
	}),

	MainManageCollaboratorsView = Gizmo.View.extend({
		refresh: function () {
			var self = this;
			self.model = Gizmo.Auth(new Gizmo.Register.Blog(self.theBlog));
			self.model
				.one('read', self.render, self)
				.sync();
		},
		render: function(evt, data) {
			if(!this.checkElement())
				return;
			var self = this,
			data = $.extend({}, this.model.feed(), {
					
					BlogHref: self.theBlog,
					FooterFixed: true,
					ui:	{

						content: 'is-content=1',
						side: 'is-side=1',
						submenu: 'is-submenu',
						submenuActive1: 'active'
					},
				    isLive: function(chk, ctx){ return ctx.current().LiveOn ? "hide" : ""; },
				    isOffline: function(chk, ctx){ return ctx.current().LiveOn ? "" : "hide"; }
			});
			self.manageInternalCollaboratorsView = new ManageInternalCollaboratorsView({
				collection: self.model.get('Collaborator'),
				collectionPotentialCollaborator: self.model.get('CollaboratorPotential')
			});
            data.ui = {
				content: 'is-content=1', 
				side: 'is-side=1', 
				submenu: 'is-submenu', 
				submenuActive3: 'active'	
			};

			$.superdesk.applyLayout('livedesk>manage-collaborators', data, function(){
		       var topSubMenu = $(self.el).find('[is-submenu]');
		        $(topSubMenu)
		        .off(self.getEvent('click'), 'a[data-target="configure-blog"]')
		        .on(self.getEvent('click'), 'a[data-target="configure-blog"]', function(event)
		        {
		            event.preventDefault();
		            var blogHref = $(this).attr('href');
		            Action.get('modules.livedesk.configure').done(function(action) {
		                    require([action.get('Script').href], function(app){ 
		                    	//console.log(app);
		                    	new app(blogHref); });
		            });
		        })
		        .off(self.getEvent('click'), 'a[data-target="manage-collaborators-blog"]')
				.on(self.getEvent('click'), 'a[data-target="manage-collaborators-blog"]', function(event)
				{
					event.preventDefault();
					var blogHref = $(this).attr('href')
					Action.get('modules.livedesk.manage-collaborators').done(function(action) {
							require([action.get('Script').href], function(app){ new app(blogHref); });
					});
				})
		        .off(self.getEvent('click'), 'a[data-target="edit-blog"]')
		        .on(self.getEvent('click'), 'a[data-target="edit-blog"]', function(event)
		        {
		            event.preventDefault();
		            var blogHref = $(this).attr('href');
		            Action.get('modules.livedesk.edit').done(function(action) {
							require([action.get('Script').href], function(EditApp){ EditApp(blogHref); });
		            });
		        });
				self.el.find('.controls').append(self.manageInternalCollaboratorsView.el);
			});
		}
	});
	var mainManageCollaboratosView = new MainManageCollaboratorsView({
		el: '#area-main'
	});
	return app = function (theBlog) {
		mainManageCollaboratosView.theBlog = theBlog;
		mainManageCollaboratosView.refresh();
	}
});