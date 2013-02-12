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
            /*!
             * upload one file to server
             * @param {object} file The object to append to FormData (form.files[i])
             * @param {string} filename The key of the file in post data
             * @param {string} path Server path to upload to
             * @param {function} startCb Callback for upload start, falls back to format if string and !format 
             * @param {string} format The format to append to path example ".xml"
             */
            upload: function(file, filename, path, startCb, format)
            {
                var fd = new FormData(),
                    format = typeof startCb == 'string' && !format ? startCb : (format ? format : 'xml');
                fd.append(filename || 'upload_file', file);
                var xhr = new XMLHttpRequest();
                // replace or add format we want as response in url // path = path.search(/(((\..+)?\?))/) != -1 ? path.replace(/(((\..+)?\?))/,'.xml?') : path+'.xml';
                xhr.open('POST', (path+' ').replace(/(((\.[\w\d-]+)?\?)|(\s$))/,'.'+format+'$1'), true);
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
                              '     action="'+$.superdesk.apiUrl+'/resources/my/HR/User/'+localStorage.getItem('superdesk.login.id')+'/MetaData/Upload?X-Filter=*&Authorization='+ localStorage.getItem('superdesk.login.session')+'"><fieldset>'+
                              '     <label class="control-label" for="editor-image-text">Upload:</label>'+
                              '     <div style="position:relative" class="controls">'+
                              //'         <input type="hidden" name="Authorization" value="'+ localStorage.getItem('superdesk.login.session')+'"/>"'+
                              '         <input type="button" value="'+_('Browse')+'"'+
                              '             class="btn btn-primary btn-block btn-medium span3" style="position:absolute;" />'+
                              '         <input type="file" name="upload_file" multiple="multiple"'+
                              '             style="position:absolute; top: 0px; left: 0px; width:100%; opacity:0;" />'+
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
                        function()
                        {
                            $('body').css('cursor', 'wait');
                            $('form#editoruploadform [type=button]', command.dialog).val(_('Uploading...')); 
                        });
                    
                    xhr.onload = function(event) 
                    { 
                        $('body').css('cursor', 'auto');
                        $('form#editoruploadform [type=button]', command.dialog).val(_('Browse'));
                        $('[name="upload_file"]', command.dialog).val('');
                        try // either get it from the responseXML or responseText
                        {
                            var content = $(event.target.responseXML.firstChild).find('Content');
                        }
                        catch(e)
                        {
                            var content = $(event.target.responseText).find('content');
                        }
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
    
});