define([
    'jquery',
    'gizmo/superdesk',
    'backbone'
], function($, giz, Backbone) {
    var Tab = Backbone.View.extend({
        tagName: 'span',
        _ctrlFor: null,
        events: {
            'click a': 'toggle'
        },
        initialize: function() {
            this.$el
                .attr('data-original-title', "Switches") 
                .attr('data-tab-ctrl', "switches")
                .attr('data-placement', "left")
                .html('<a><i class="big-icon-switches"></i>'+
                    '<span class="badge badge-inverse hide notifications"></span>'+
                    '<span class="badge badge-info hide config-notif">!</span></a>');
        },
        render: function() {},
        controls: function(obj) {
            this._ctrlFor = obj;
        },
        resetEvents: function() {},
        toggle: function(evt) {
            evt.preventDefault();
            this._ctrlFor.toggle(); 
        }
    });
    
    var TabContent = Backbone.View.extend({
        tagName: 'div',
        events: {},
        initialize: function() {
            this.$el.addClass('tabcontent').attr('data-tab', "publishing-control").html('<section></section>');
        },
        render: function() {

        },
        resetEvents: function() {},
        toggle: function() {
            var tabpane = this.$el.parent();
            if (tabpane.hasClass('open-tabpane')) {
                this.$el.hide();
                this.deactivate();
                tabpane.removeClass('open-tabpane');
                return;
            }
            $(this.el).show();
            tabpane.addClass('open-tabpane');
            this.activate();
        },
        deactivate: function() {
            $(this).trigger('inactive');
        },
        activate: function() {
            $(this).trigger('active');
        }
    });

    tabContent = new TabContent,
    tab = new Tab;
    tab.controls(tabContent);
    
    return {control: tab, content: tabContent};
});