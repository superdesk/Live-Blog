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
            this.el.addClass('tabcontent temptabcont').attr('data-tab', "media").html('<section></section>');
        },
        toggle: function()
        {
            if( $(this.el).hasClass('open') )
            {
                this.deactivate();
                $(this.el).removeClass('open');
                return;
            }
            $(this.el).addClass('open');
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