define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'upload'),
    'tmpl!media-archive>add'
],
function($, superdesk, giz, uploadCom)
{
    var 
    /*!
     * add media view
     */
    AddView = giz.View.extend
    ({
        events: 
        {
            "[data-action='browse']": { 'click': 'browse' },
            "[data-action='upload']": { 'change': 'upload' }
        },
        browse: function()
        {
            $('input[type="file"]', this.el).trigger('click');
        },
        uploadEndPoint: $.superdesk.apiUrl+'/resources/my/HR/User/'+localStorage.getItem('superdesk.login.id')+'/MetaData/Upload?X-Filter=*&Authorization='+ localStorage.getItem('superdesk.login.session'),
        upload: function()
        {
            var files = $('[data-action="upload"]', this.el)[0].files,
                self = this; 
            for( var i=0; i<files.length; i++)
            {
                xhr = uploadCom.upload( files[i], 'upload_file', this.uploadEndPoint,
                        // display some progress type visual
                        function(){ $('[data-action="browse"]', self.el).val(_('Uploading...')); }, 'json');
                xhr.onload = function(event) 
                { 
                    $('[data-action="browse"]', this.el).val(_('Browse'));
                    try // either get it from the responseXML or responseText
                    {
                        var content = JSON.parse(event.target.responseText);
                    }
                    catch(e)
                    {
                        var content = JSON.parse(event.target.response);
                    }
                    if(!content) return;
                    $(self).triggerHandler('uploaded', [content.Id]);
                };
            }
            $('[data-action="upload"]', this.el).val('');
            this.hide();
        },
        init: function()
        {
            this.render();
        },
        render: function()
        {
            $(this.el).tmpl('media-archive>add', {Title: _('Add media')});
        },
        activate: function()
        {
            $(this.el).modal('show');
        },
        hide: function()
        {
            $(this.el).modal('hide');
        }
    }),
    /*!
     * the instance
     */
    Add = new AddView;
    
    return Add;
});