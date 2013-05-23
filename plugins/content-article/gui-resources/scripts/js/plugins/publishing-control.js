define([
    'jquery',
    'backbone',
    'gizmo/superdesk',
    config.guiJs('superdesk/article', 'tabs/publishing-control'),
    'tmpl!superdesk/article>plugins/publishing-control',
    'tmpl!superdesk/article>plugins/publishing-control/item'
], 
function($, Backbone, giz, publishingControlTab) {
    var TargetType = Backbone.Model.extend({

    });

    var TargetTypeCollection = Backbone.Collection.extend({
    	model: TargetType
    });

    var PublishingControlTabBoxPlugin = Backbone.View.extend({
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
        		//
        		$('.sf-toggle').each(function(i,val){
			      	var additional_class="";
			      	if ($(val).attr("checked")=="checked")  additional_class += " sf-checked ";
			      	if ($(val).hasClass("on-off")) additional_class +=" on-off-toggle ";
			      	if ($(val).hasClass("sf-disable")) additional_class += " sf-disable ";
			        $(val).wrap('<div class="sf-toggle-custom ' + additional_class + '"><div class="sf-toggle-custom-inner"></div></div>');
			        $(val).hide();
			    });
			    $('.sf-toggle-custom').click(function(e){
			        e.preventDefault();
			        if (!$(this).hasClass("sf-disable")) {
						$(this).toggleClass('sf-checked');
				        var own_box = $(this).find(".sf-toggle").first();
				        if (own_box.prop('checked')==true) {
				        	own_box.prop('checked',false);
				        } else {
				        	own_box.prop('checked',true);
				        }
			        }
			    });
			    //
			    this._activatedOnce = true;
        	}
        }
    });
    
    return new PublishingControlTabBoxPlugin(new TargetTypeCollection);
});