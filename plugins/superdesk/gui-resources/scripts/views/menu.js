define(['backbone'], function(Backbone) {
    var Item = Backbone.Model.extend();
    var ItemCollection = Backbone.Collection.extend({model: Item});

    /**
     * Submenu item view
     */
    var ItemView = Backbone.View.extend({
        tagName: 'li',
        render: function() {
            var link = $('<a />').text(this.model.get('Label')).attr('href', '#' + this.model.get('NavBar'));
            $(this.el).html(link);
            return this;
        }
    });

    /**
     * Main item view - require in submenu and add items to it
     */
    var MenuView = Backbone.View.extend({
        initialize: function() {
            this.collection.on('add', this.render, this);
        },

        render: function() {
            this.renderItems();
            return this;
        },

        renderItems: function() {
            var list = $(this.el).find('ul[data-submenu="menu.config"]').empty();
            this.collection.each(function(item) {
                var view = new ItemView({model: item});
                list.append(view.render().el);
            });
        },

        addItem: function(data) {
            this.collection.add(data);
        }
    });

    var items = new ItemCollection();
    var view = new MenuView({el: $('.menu-menu-config').closest('li'), collection: items});
    return view;
});
