define
([
    'jquery', 
    'superdesk/image-plugin'
],
function ($, Image) 
{
    'use strict';
    
    var upload = null,
        GENTICS = window.GENTICS,
        Aloha = window.Aloha,
        activeRange = null,
        activeEditableObj = null;
    
    require
    ({
        baseUrl: config.content_url
    }, 
    [config.guiJs('media-archive', 'adv-upload')], 
    function(Upload)
    { 
        upload = new Upload; 
        $(upload).on('complete', function(){ Image.insertImg(upload.getRegisteredItems()); });
    });
    
    
    Image.handleInsert = function()
    {
        if(!Aloha.activeEditable) return;
        activeRange = Aloha.Selection.getRangeObject();
        activeEditableObj = Aloha.activeEditable.obj;
        
        upload.activate();
        $(upload.el).addClass('modal hide fade responsive-popup').modal();
    };
    
    
    Image.insertImg = function(items) 
    {
        for( var i in items ) (function(item)
        { 
            item.sync({data: { thumbSize: 'large' }}).done(function()
            {
                Aloha.trigger('insert-image.image-plugin', item);
                var newImg = $('<img src="'+item.get('Thumbnail').href+'" />');
                GENTICS.Utils.Dom.insertIntoDOM(newImg, activeRange, jQuery(activeEditableObj));
            });
        })(items[i]);
        
        document.execCommand('enableObjectResizing', true, true);
    };
});
    