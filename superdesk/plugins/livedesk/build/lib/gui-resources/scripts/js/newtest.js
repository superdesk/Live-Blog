define(['newgizmo'], 
function(Gizmo)
{
	var LiveDesk = Gizmo.View.extend({
		namespace: 'livedesk'
	});
	var EditView = LiveDesk.extend({
		events: {
			'[ci="savepost"]': { 'click': 'saveAndPost' },
			'[ci="save"]': { 'click': 'save'}
		},
		init: function(){
			this.model = 'some';
			fixedToolbar = 
			{
				_create: function(elements)
				{
					var self = this;
					$(elements).on('toolbar-created', function()
					{
						self.plugins.toolbar.element.hide()
							.appendTo($('.edit-block .toolbar-placeholder')); 
					}); 
					$(elements).on('focusin.texteditor keydown.texteditor click.texteditor', function(event)
					{
						self.plugins.toolbar.element.fadeIn('fast');
					});
					$(elements).on('blur.texteditor focusout.texteditor', function()
					{ 
						self.plugins.toolbar.element.fadeOut('fast'); 
					});
				}
			};
			$('.edit-block article.editable').texteditor({ plugins: 
			{
				floatingToolbar: null, 
				draggableToolbar: null, 
				fixedToolbar: fixedToolbar
			}});			
		},
		render: function(){
		
		},
		save: function(evt){
			e.preventDefault();
			var data = {
				Content: $.styledNodeHtml('.edit-block article.editable'),
				Type: $(this.el).find('[name="type"]').val()
			};
			new $.restAuth(theBlog+'/Post').resetData().xfilter('Id,AuthorName,Content,Type.Key,PublishedOn,CreatedOn,Author.Source.Name').insert(data).done(function(post){
				$('.editable',self.el).html('');
				$('[name="type"]',self.el).val('normal');
				startx = self.data.length;
				self.data[startx] = post;
				post.startx = startx;
				updatePost( post );
			});		
		},
		saveAndPost: function(evt){
			var data = {
				Content: $.styledNodeHtml('.edit-block article.editable'),
				Type: $(this.el).find('[name="type"]').val()
			};
			new $.restAuth(theBlog+'/Post').resetData().xfilter('Id,AuthorName,Content,Type.Key,PublishedOn,CreatedOn,Author.Source.Name').insert(data).done(function(post){
				$('.editable',self.el).html('');
				$('[name="type"]',self.el).val('normal');
				startx = self.data.length;
				self.data[startx] = post;
				post.startx = startx;
				post.PublishedOn = true;
				updatePost( post );
				new $.restAuth(post.href+'/Publish').resetData().insert().done(function(){
					require([$.superdesk.apiUrl+'/content/gui/superdesk/livedesk/scripts/js/edit-live-blogs.js'],
						function(EditApp){ new EditApp(theBlog).update(); });
				});
			});
			
		}
	});
});