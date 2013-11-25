define([ 
    'jquery', 
    'gizmo/superdesk',
    'jqueryui/autocomplete',
    config.guiJs('livedesk', 'models/users'),
	'tmpl!livedesk>citizen-desk/checker-list'
], function( $, Gizmo ) {

	    Users = Gizmo.Auth(new Gizmo.Register.Users());
	   	Users.xfilter('Id,EMail,FirstName,LastName,FullName,Name')
			//.limit(1)
			.sync();
    	return UserDrop = Gizmo.View.extend({
				init: function(){
					var self = this;
					self.data = [];
					if(!self.collection) {
						self.collection = Users;
					}
					this.render();
				},
				killMenu: function(){
					var self = this;
					$('.dropdown.open .dropdown-toggle', self.el).dropdown('toggle');
				},
				sync: function() {

					this.collection
						.on('read', self.render, self)
						.xfilter('EMail,FirstName,LastName,FullName,Name')
						.sync()    			
				},
				render: function(evt, data){
					var self = this;
					self.collection.each(function(){
						self.data.push({label: this.get('FullName'), value: this.feed()});
					});
					self.el.tmpl(self.template, self.getCurrent(), function(){
						var autocomp = $('input',self.el).autocomplete({
							autoFocus: true,
							minLength: 0,
							appendTo: $('.assignment-result-list',self.el),
							source: self.data
						}).data( "autocomplete" );
						autocomp._renderItem = function( ul, item ) {
								return $( "<li></li>" )
									.data( "item.autocomplete", item )
									.append( '<figure class="avatar-small"></figure><span>'+ item.label+'</span>'  )
									.appendTo( ul );
						};
						autocomp._renderMenu = function( ul, items ) {
							var self = this;
							$.each( items, function( index, item ) {
								self._renderItem( ul, item );
							});
							$( ul ).removeClass('ui-autocomplete');
						};
					});
				},
				getCurrent: function(){
					return {};
				}		
    		});
});