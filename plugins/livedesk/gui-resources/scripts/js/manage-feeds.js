define([
    'jquery',
    'gizmo/superdesk',

    'tmpl!livedesk>layouts/livedesk',
    'tmpl!core>layouts/footer',
    'tmpl!core>layouts/footer-static',
	'tmpl!livedesk>manage-feeds',
	'tmpl!livedesk>manage-feeds-provider',
], function ($, Gizmo) {
    var BlogProvider = Gizmo.Model.extend({});

    var BlogProviderCollection = Gizmo.Collection.extend({
        model: BlogProvider,

        url: new Gizmo.Url('LiveDesk/BlogProvider'),

        init: function() {
            var collection = this;
            this.model.on('insert', function(model) {
                collection.trigger('add');
            });
        }
    });

    var BlogProviderView = Gizmo.View.extend({
        tagName: 'li class="chain-source"',

        events: {
            '.remove': {click: '_remove'},
            '.edit': {click: '_edit'}
        },

        init: function() {
            this.model.on('delete', this.remove, this);
        },

        render: function() {
            var $el = $(this.el);
            var data = this.model.feed();
            $.tmpl('livedesk>manage-feeds-provider', data, function(e, o) {
                $el.html(o);
            });
            return this;
        },

        _remove: function(e) {
            e.preventDefault();
            this.model.remove().sync();
        },

        _edit: function(e) {
            e.preventDefault();
            console.log('edit', this.model);
        }
    });

    var AddBlogProviderView = Gizmo.View.extend({
        data: {},

        events: {
            '#add-provider-save': {click: 'save'},
            'input:text[name="URL"]': {change: 'setData'},
            'input:text[name="Title"]': {change: 'setData'}
        },

        setData: function(e) {
            var target = $(e.target);
            this.data[target.attr('name')] = target.val();
        },

        save: function(e) {
            e.preventDefault();
            this.collection.insert(this.data);
            this.reset();
            $(this.el).modal('hide');
        },

        reset: function() {
            $(this.el).find('input:text').val('');
            this.data = {};
        }
    });

    var ListBlogProviderView = Gizmo.View.extend({
        init: function() {
            this.collection.on('read', this.render, this);
            this.collection.on('add', this.render, this);
        },

        render: function() {
            var list = $(this.el);

            list.empty();
            this.collection.each(function() {
                var modelView = new BlogProviderView({model: this});
                list.append(modelView.render().el);
            });

            if (!this.collection.count()) {
                list.append($('<li />').text(_("So far there are no providers. Start with Add New Source button.")));
            }

            return this;
        }
    });

    /**
     * Manage Feeds Main View
     */
    var ManageFeedsView = Gizmo.View.extend({
        el: '#area-main',

        events: {
            'a[href="#AddSource"]': {click: 'renderAdd'}
        },

        init: function() {
            this.model.one('read', this.render, this);
        },

        render: function() {
            var data = this.model.feed();
            data.ui = {
                content: 'is-content=1',
                side: 'is-side=1',
                submenu: 'is-submenu',
                submenuActive4: 'active'
            };

            var view = this;
	        $.tmpl('livedesk>manage-feeds', data, function(e,o){
		        $(view.el).html(o);

                $('.sf-checkbox').each(function(i,val){
                    $(val).after('<span class="sf-checkbox-custom" target-checkbox="' + $(val).attr('name') +'"></span>');
                    $(val).hide();
                });

                $('.sf-checkbox-custom').click(function(e){
                    e.preventDefault();
                    $(this).toggleClass('sf-checked');
                    var own_box = $('input[name="' + $(this).attr("target-checkbox") + '"]');
                    //set active class

                    var set_bg = own_box.attr("set-bg"); 
                    if (typeof set_bg !== undefined && set_bg !== false) {
                    $(this).parents().eq(set_bg-1).toggleClass('active-bg');
                    }
        
        
                    if (own_box.prop('checked')==true) { 
                    own_box.prop('checked',false); 
                    }
                    else { 
                    own_box.prop('checked',true); 
                    }
                    return false;
                    
                });

                $(".chain-source-collapse a").click(function(e){
       		            $(this).parents().eq(2).toggleClass("chain-collapsed");
                });

                view.renderList();
            });
            return this;
        },

        renderList: function() {
            var list = new ListBlogProviderView({collection: this.collection, el: '#provider-list'});
            this.collection.xfilter('Title').sync();
        },

        renderAdd: function() {
            var addView = new AddBlogProviderView({collection: this.collection, el: '#AddSource'});
        }
    });

    return function(blogHref) {
        main = new ManageFeedsView({
            model: Gizmo.Auth(new Gizmo.Register.Blog(blogHref)),
            collection: new BlogProviderCollection()
        });

        main.model.sync();
    }
});
