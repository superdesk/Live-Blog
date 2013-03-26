define
([
  'jquery',
  'gizmo/superdesk',
], 
function($, giz)
{ 
    var Tab = giz.View.extend
    ({
        events: 
        {
            'a': { 'click': 'toggle' } 
        },
        toggle: function(evt)
        { 
            evt.preventDefault();
            this._ctrlFor.toggle(); 
        },
        controls: function(obj){ this._ctrlFor = obj; },
        tagName: 'span',
        init: function()
        {
            this.el
                .attr('data-original-title', "Media") 
                .attr('data-tab-ctrl', "media")
                .attr('data-placement', "left")
                .html('<a><i class="big-icon-media"></i>'+
                    '<span class="badge badge-inverse hide notifications"></span>'+
                    '<span class="badge badge-info hide config-notif">!</span></a>');
        }
    }),
    TabContent = giz.View.extend
    ({
        tagName: 'div',
        init: function()
        {
            this.el.addClass('tabcontent').attr('data-tab', "media").html('<section></section>');
        },
        resetState: function()
        {
            this.deactivate();
            $(this.el).hide();
            $(this.el).parent().removeClass('open-tabpane');
            return this;
        },
        toggle: function()
        {
            var tabpane = $(this.el).parent();
            if( tabpane.hasClass('open-tabpane') )
            {
                $(this.el).hide();
                this.deactivate();
                tabpane.removeClass('open-tabpane');
                return;
            }
            $(this.el).show();
            tabpane.addClass('open-tabpane');
            this.activate();

        },
        deactivate: function()
        {
            $(this).trigger('inactive');
        },
        activate: function()
        {
            $(this).trigger('active');
        }
    }),
    tabContent = new TabContent,
    tab = new Tab;
    tab.controls(tabContent);
    return {control: tab, content: tabContent};
});