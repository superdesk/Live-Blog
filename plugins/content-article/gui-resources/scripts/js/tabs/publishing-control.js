define([
    'jquery',
    'gizmo/superdesk'
], function($, giz) {
    var Tab = giz.View.extend({
        events: {
            'a': {'click': 'toggle'}
        },
        toggle: function(evt) {
            evt.preventDefault();
            this._ctrlFor.toggle(); 
        },
        tagName: 'span',
        render: function() {},
        controls: function(obj) {
            this._ctrlFor = obj;
        },
        init: function() {
            this.el
                .attr('data-original-title', "Switches") 
                .attr('data-tab-ctrl', "switches")
                .attr('data-placement', "left")
                .html('<a><i class="big-icon-switches"></i>'+
                    '<span class="badge badge-inverse hide notifications"></span>'+
                    '<span class="badge badge-info hide config-notif">!</span></a>');
        }
    });
    
    var TabContent = giz.View.extend({
        parent: null,
        tagName: 'div',
        events: {},
        init: function() {
            this.el.addClass('tabcontent').attr('data-tab', "publishing-control").html('<section></section>');
        },
        render: function() {

        },
        resetEvents: function() {},
        toggle: function() 
        {
            
            this._parent.deactivateTabContents();
            
            var tabpane = $(this.el).parent();
            if (tabpane.hasClass('open-tabpane')) {
                $(this.el).hide();
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
        },
        setParent: function(editView)
        {
            this._parent = editView;
        }
    });

    tabContent = new TabContent,
    tab = new Tab;
    tab.controls(tabContent);
    
    return {control: tab, content: tabContent};
});