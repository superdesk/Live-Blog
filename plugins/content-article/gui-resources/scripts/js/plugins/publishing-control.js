define([
    'jquery',
    'backbone',
    'gizmo/superdesk',
    config.guiJs('superdesk/article', 'tabs/publishing-control'),
    'tmpl!superdesk/article>plugins/publishing-control',
    'tmpl!superdesk/article>plugins/publishing-control/item'
], 
function($, Backbone, giz, publishingControlTab) {
    PublishingControlTabBoxPlugin = Backbone.View.extend({
    	_parent: null,
    	_article: null,
    	_activatedOnce: false,
    	events: {},
    	initialize: function() {
    		var self = this;
    		this.$el.appendTo($('section', publishingControlTab.content.$el));
    		$(publishingControlTab.content).on('active', function() {
    			self.activate();
    		});
    		this.render();
    	},
    	render: function() {
    		this.$el.tmpl('superdesk/article>plugins/publishing-control');
    	},
    	setParent: function(editView) {
            this._parent = editView;
        },
        setArticle: function(article) {
            this._article = article;
        },
        activate: function() {
        	if (this._activatedOnce === false) {
        		$('.sf-checkbox').each(function(i,val){
			      	var ischecked = "";
			      	if ($(val).attr("checked")=="checked") ischecked="sf-checked";
			        $(val).wrap('<span class="sf-checkbox-custom ' + ischecked + '"></span>');
			        $(val).hide();

			        var set_bg = $(val).attr("set-bg"); 
					if (typeof set_bg !== undefined && set_bg !== false && $(val).attr("checked")=="checked") {
						$(this).parents().eq(set_bg-1).toggleClass('active-bg');
					}
			    });
			    $('.sf-checkbox-custom').click(function(e){
			    	e.preventDefault();
			        $(this).toggleClass('sf-checked');
			        var own_box = $(this).find(".sf-checkbox").first();

			        var set_bg = own_box.attr("set-bg"); 
			        if (typeof set_bg !== undefined && set_bg !== false) {
			        	$(this).parents().eq(set_bg-1).toggleClass('active-bg');
			        }
			        if (own_box.prop('checked')==true) {
			        	own_box.prop('checked',false);
			        } else {
			        	own_box.prop('checked',true);
			        }
			    });
			    this._activatedOnce = true;
        	}
        }
    });
    
    return new PublishingControlTabBoxPlugin;
});