define('providers/image', 
[ 
    'providers', 
    'jquery',
    'gizmo/superdesk',
    config.guiJs('livedesk', 'action'),
    config.guiJs('media-archive', 'adv-upload'),
    'tmpl!livedesk>providers/image'
], function(providers, $, gizmo, Action, UploadView)
{
    var 
    uploadView = new UploadView,
    ImageView = gizmo.View.extend
    ({
        events: { "[data-toggle='modal']": { 'click': 'openUploadScreen' } },
        openUploadScreen: function()
        {
            uploadView.activate();
            $(uploadView.el).addClass('modal hide fade responsive-popup').modal();
        },
        init: function()
        { 
            $(uploadView).on('complete', function(){ console.log(uploadView.getRegisteredItems()); });
            this.render(); 
        },
        render: function()
        { 
            $(this.el).tmpl('livedesk>providers/image'); 
        },
        addItem: function(event)
        {
            console.log(event);
        }
    }),
    imageView = null;
    $.extend( providers.image, { init: function(blogUrl)
    { 
        if( !imageView || (this.el.get(0) != imageView.el.get(0)) )
            imageView = new ImageView({ el: this.el, blogUrl: blogUrl });
        return imageView;
    }});
    
    return providers;
});