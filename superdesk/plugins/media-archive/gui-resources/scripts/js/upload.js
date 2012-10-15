define
([
    'jquery',
    'jqueryui/texteditor'        
],
function()
{
    var origImageCtrl = $.ui.texteditor.prototype.plugins.controls.image,
        uploadComponent = 
        {
            upload: function(file, filename, path, startCb)
            {
                var fd = new FormData();
                fd.append(filename || 'upload_file', file);
                var xhr = new XMLHttpRequest();
                xhr.open('POST', path, true);
                xhr.setRequestHeader('X-Filter', 'Content');
                startCb && startCb.apply(this);
                xhr.send(fd);
                return xhr;
            },
            /*!
             * plugin for texteditor
             */
            texteditor: function()
            {
                // call super
                var command = origImageCtrl.apply(this, arguments),
                    htmlCom = ' <form id="editoruploadform" '+
                              '     method="post" enctype="multipart/form-data" class="form-horizontal clearfix"'+
                              '     action="'+$.superdesk.apiUrl+'/resources/Archive/MetaData/Upload"><fieldset>'+
                              '     <label class="control-label" for="editor-image-text">Upload:</label>'+
                              '     <div style="position:relative" class="controls">'+
                              '         <input type="file" name="upload_file" multiple="multiple"'+
                              '             style="position:absolute; width:100%; opacity:0;" />'+
                              '         <input type="button" value="'+_('Browse')+'"'+
                              '             class="btn btn-primary btn-block btn-medium span3" style="position:absolute;" />'+
                              ' </div></fieldset></form>';
                // build upload form html component
                $(command.dialog).prepend(htmlCom);
                $('form#editoruploadform [type=file]', command.dialog)
                    .on('change', function(){ $('form#editoruploadform', command.dialog).trigger('submit'); });
                $('form#editoruploadform [type=button]', command.dialog)
                    .on('click', function(){  $('form#editoruploadform [type=file]', command.dialog).trigger('click'); });
                
                $('form#editoruploadform', command.dialog).on('submit', function()
                {
                    var xhr = uploadComponent.upload( $('[name="upload_file"]', 
                        command.dialog)[0].files[0], 'upload_file', 
                        $(this).attr('action'),
                        function(){ $('form#editoruploadform [type=button]', command.dialog).val(_('Uploading...')); });
                    
                    xhr.onload = function(event) 
                    { 
                        $('form#editoruploadform [type=button]', command.dialog).val(_('Browse'));
                        $('[name="upload_file"]', command.dialog).val('');
                        var content = $(event.target.responseXML.firstChild).find('Content');
                        if(!content) return;
                        var valIn = $('[data-option="image-value"]', command.dialog);
                        valIn.parents('.control-group:eq(0)').addClass('success');
                        $('<span class="help-inline">&#10004;</span>').insertAfter(valIn);
                        valIn.val(content.attr('href'));
                        setTimeout(function()
                        { 
                            valIn.parents('.control-group:eq(0)').removeClass('success'); 
                            valIn.next('.help-inline').remove(); 
                        }, 5000);
                    };
                    
                    return false;
                });
                return command;
            }
        }
    ;
    
    return uploadComponent;
    
    $.ui.texteditor.prototype.plugins.controls.image = function()
    {
        // call super
        var command = origImageCtrl.apply(this, arguments);
            
        // build upload form html component
        $(command.dialog).prepend('<form id="editoruploadform" '+
            ' method="post" enctype="multipart/form-data" class="form-horizontal clearfix"'+
            ' action="'+$.superdesk.apiUrl+'/resources/Archive/MetaData/Upload"><fieldset>'+
            '<label class="control-label" for="editor-image-text">Upload:</label>'+
            '<div style="position:relative" class="controls">'+
            '<input type="file" name="upload_file" multiple="multiple"'+
            ' style="position:absolute; width:100%; opacity:0;" />'+
            '<input type="button" value="'+_('Browse')+'"'+
            ' class="btn btn-primary btn-block btn-medium span3" style="position:absolute;" />'+
            '</div></fieldset></form>');
        
        $('form#editoruploadform [type=file]', command.dialog)
            .on('change', function(){ $('form#editoruploadform', command.dialog).trigger('submit'); });
        $('form#editoruploadform [type=button]', command.dialog)
            .on('click', function(){  $('form#editoruploadform [type=file]', command.dialog).trigger('click'); });
        
        $('form#editoruploadform', command.dialog).on('submit', function()
        {
            var file = $('[name="upload_file"]', command.dialog)[0].files[0],
                fd = new FormData();
            fd.append('upload_file', file);
            var xhr = new XMLHttpRequest();
            xhr.open('POST', $(this).attr('action'), true);
            xhr.setRequestHeader('X-Filter', 'Content');
            $('form#editoruploadform [type=button]', command.dialog).val(_('Uploading...'));
            xhr.onload = function(event) 
            { 
                $('form#editoruploadform [type=button]', command.dialog).val(_('Browse'));
                $('[name="upload_file"]', command.dialog).val('');
                var content = $(event.target.responseXML.firstChild).find('Content');
                if(!content) return;
                var valIn = $('[data-option="image-value"]', command.dialog);
                valIn.parents('.control-group:eq(0)').addClass('success');
                $('<span class="help-inline">&#10004;</span>').insertAfter(valIn);
                valIn.val(content.attr('href'));
                setTimeout(function()
                { 
                    valIn.parents('.control-group:eq(0)').removeClass('success'); 
                    valIn.next('.help-inline').remove(); 
                }, 5000);
            };
            xhr.send(fd);
            return false;
        });
        return command;
    };
});