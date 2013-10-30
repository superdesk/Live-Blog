/*!
 * text editor plugin on jQuery UI extended
 * 
 * usage:
 * // extend controls plugin
 * var myControls = $.extend({}, $.ui.texteditor.prototype.plugins.controls, { custom : customObject });
 * $('article .body').texteditor({plugins : { controls : myControls }});
 * 
 * // replace controls
 * $('article header h1').texteditor({ plugins : { controls : { custom : customControl } } });
 *  
 * // add another plugin
 * $('article header h1').texteditor('plugin', { customPlugin: { _create : function(){ ... } }}); 
 * 
 */
define('jqueryui/texteditor', ['jquery','jqueryui/widget', 'jqueryui/ext', 'jqueryui/draggable'], function ($) 
{
    "use strict";
    $.widget( "ui.texteditor", 
    {
        plugins : 
        {
            lib : 
            {
                markSelection : function() 
                {
                    var markerId = arguments[0] ? arguments[0] : "sel-" + (+new Date()) + "-" + ("" + Math.random()).slice(2),
                        selection = window.getSelection(),
                        range = selection.rangeCount ? selection.getRangeAt(0) : false,
                        marker = $('<span />').html('&#xfeff;').attr('sel-id', markerId ).hide();

                    if( !range ) return false;
                    if( range.collapsed ) 
                        range.insertNode(marker.get(0));
                    else // not collapsed for selecting nodes like <img />
                    {
                        // making sure there are only 2 selections with the same id at this point
                        var selMark = $('[sel-id="'+markerId+'"]'), 
                            intermRange = range.cloneRange(),
                            firstMarker = !selMark.length ? marker.get(0) : selMark.get(0),
                            secondMarker = !selMark.length ? marker.clone().get(0) : selMark.get(1);
                        !selMark.length && intermRange.insertNode(firstMarker);
                        range.setStartAfter(firstMarker);
                        intermRange.collapse(false);
                        !selMark.length && intermRange.insertNode(secondMarker);
                        range.setEndBefore(secondMarker);
                        intermRange.detach();
                    }
                    return markerId;
                },
                restoreSelection : function(markerId)
                {
                    var selection = window.getSelection(),
                        range = document.createRange(),
                        selMark = $('[sel-id="'+markerId+'"]');
                    if( !selMark.length ) return;
                    range.setStartAfter(selMark.get(0));
                    if( selMark.length > 1 )
                        range.setEndBefore(selMark.get(1));
                    selection.removeAllRanges();
                    selection.addRange(range);
                    if(!arguments[1]) selMark.remove();
                    return selection;
                },
                selectionChildren : function()
                {
                    var range = window.getSelection().getRangeAt(0),
                        contents = $(range.commonAncestorContainer).contents(),
                        ret = [];

                    for( var i = range.startOffset; i < range.endOffset; i++ )
                        contents[i] && ret.push(contents[i]);
                    
                    return $(ret).filter(function()
                    { 
                        return !(this.nodeType == 3 && $(this).text().trim() == '');
                    });
                },
                selectionText : function()
                {
                    if( window.getSelection )
                        return window.getSelection().getRangeAt(0).toString();
                    return '';
                },
                selectionHas : function(nodeName)
                {
                    if( window.getSelection )
                    {
                        var range = window.getSelection().getRangeAt(0);
                        if( range.startContainer.nodeType == Node.TEXT_NODE ||
                            range.startContainer.nodeType == Node.COMMENT_NODE ||
                            range.startContainer.nodeType == Node.CDATA_SECTION_NODE ) return false;
                              
                        for( var i = range.startOffset-1; i <= range.endOffset; i++ )
                            if( $(range.startContainer.childNodes[i]).is(nodeName) ) return $(range.startContainer.childNodes[i]);
                        if( range.startContainer.innerHTML 
                                && $(range.startContainer.innerHTML).is(nodeName) 
                                && $(range.endContainer.innerHTML).is(nodeName) )
                            return $(range.startContainer.innerHTML);
                        return false;
                    }
                },
                selectionParent : function()
                {
                    if( window.getSelection )
                    {
                        var selection = window.getSelection();
                        if( selection.rangeCount <= 0 ) return false;
                        var range = selection.getRangeAt(0),
                            container = range.collapsed ? range.startContainer : range.commonAncestorContainer;
                        
                    }
                    else
                    {
                        var selection = document.selection;
                        if( selection.type == "Control" ) 
                        {
                            var range = selection.createRange();
                            if( range.length == 1 ) 
                                var container = range.item(0); 
                            else  
                                return null; 
                        } 
                        else 
                        {
                            var range = selection.createRange();
                            var container = range.parentElement();
                        }
                    }
                    return range.collapsed && container.nodeType == 3 ? $(container).parents(':eq(0)') : $(container);
                },
                /*!
                 * returns a copy of the selection contents
                 */
                selectionContents : function()
                {
                    if( window.getSelection )
                    {
                        var range = window.getSelection().getRangeAt(0);
                        var contents = $.makeArray(range.cloneContents().childNodes);
                    }
                    else
                    {
                        var selection = document.selection;
                        if( selection.type == "Control" ) 
                        {
                            var range = selection.createRange();
                            if( range.length == 1 ) 
                                var contents = range.item(0); 
                            else  
                                return null; 
                        } 
                        else 
                        {
                            var range = selection.createRange();
                            var contents = range.htmlText();
                        }   
                    }
                    return $(contents).filter(function()
                    { 
                        return !(this.nodeType == 3 && $(this).text().trim() == '');
                    });
                },
                selectionHtml: function()
                {
                    var selection = window.getSelection(),
                        range = selection.rangeCount ? selection.getRangeAt(0) : false,
                        tmpDiv = $('<div />');
                    tmpDiv.append(range.cloneContents().childNodes).find("[sel-id]").remove();
                    return tmpDiv.html();
                },
                _create : function(elements)
                {
                    var lib = this.plugins.lib;
                    lib.command.prototype.lib = lib;
                    lib.dialogAidedCommand.inherits(lib.command);
                    lib.dialogAidedCommand.prototype.dialogRepo = new Array;
                    lib.imageCommand.inherits(lib.dialogAidedCommand);
                    lib.linkCommand.inherits(lib.dialogAidedCommand);
                    lib.htmlCodeCommand.inherits(lib.dialogAidedCommand);
                },
                command : function( command ) 
                {
                    this.execute = function() 
                    {
                        document.execCommand(command, false, null);
                        this.toggleState();
                        $(this).trigger('command-'+command+'.text-editor');
                    };
                    this.toggleState = function()
                    {
                        if(this.queryState.apply(this, arguments))
                            $(this.getElements()).addClass('active');
                        else
                            $(this.getElements()).removeClass('active');
                    };
                    this.queryState = function() 
                    {
                        return document.queryCommandState(command);
                    };
                    this._elements = [];
                    this.addElement = function(elem)
                    {
                        this._elements.push(elem);
                    };
                    this.getElements = function()
                    {
                        return this._elements;
                    };
                    this.id = command;
                },
                /*!
                 * basic command which adds a jquery ui dialog for popup on execute
                 * inheriting classes must set dialog.prop('caller', this) - this = them
                 *  to make restore selection work Q_Q 
                 */
                dialogAidedCommand : function()
                {
                    this.parentClass.apply(this, ['dialog']); // need to instance the parent command
                    this.restoreSelectionMarkerId = null;
                    var self = this;
                    this.dialog = $( "<div />" )
                        .dialog
                        ({ 
                            autoOpen: false,
                            modal: true,
                            width: 500, // TODO from options
                            close: function()
                            {
                                var caller = $(this).prop('caller'); 
                                caller.restoreSelectionMarkerId 
                                    && self.lib.restoreSelection(caller.restoreSelectionMarkerId);
                            }
                        });
                    
                    this.getDialog = function()
                    {
                        return this.dialog;
                    };
                    this.getSelectionMarkerId = function()
                    {
                        return this.restoreSelectionMarkerId;  
                    };
                    this.execute = function()
                    {
                        this.restoreSelectionMarkerId = this.lib.markSelection();
                        this.getDialog().dialog('open');
                    };
                },
                imageCommand : function(thisPlugin)
                {
                    var dialog = this.dialog.attr('title', 'Add/edit an image').append(thisPlugin.options.imageDialogUI),
                        self = this;
                    
                    $(thisPlugin).on('plugins-remove', function()
                    { 
                        dialog.dialog('remove').remove();
                    });
                    
                    this.queryState = function()
                    {
                        return this.lib.selectionHas('img');
                    };
                    this.dialogButtons = 
                    {
                        insert : 
                        {
                            text : 'Insert',
                            class: 'btn-primary btn',
                            click : function()
                            {
                                var url = $(this).find('[data-option="image-value"]').val(),
                                    text = $(this).find('[data-option="image-text"]').val(),
                                    width = $(this).find('[data-option="image-width"]').val() || thisPlugin.options.imageDefaultWidth,
                                    height = $(this).find('[data-option="image-height"]').val() || thisPlugin.options.imageDefaultHeight,
                                    align = $(this).find('[data-toggle="buttons-radio"] .active');
                                
                                if( url === null )
                                {
                                    $(this).dialog('close');
                                    return false;
                                };
                                self.lib.restoreSelection(self.restoreSelectionMarkerId, true);

                                    // need to remark selection because apparently inserting images removes ranges
                                    self.restoreSelectionMarkerId = self.lib.markSelection(self.restoreSelectionMarkerId);
                                    //document.execCommand("insertImage", false, url);
                                    if( window.getSelection )
                                    {
                                        var rng= window.getSelection().getRangeAt(0);
                                        rng.deleteContents()
                                        rng.insertNode( $('<img />').attr('src', url).get(0) );
                                    }
                                    self.lib.restoreSelection(self.restoreSelectionMarkerId);
                                    var newImg = $(self.lib.selectionHas('img'));
                                    align && newImg.attr('align', align.attr('data-value'));
                                    width && newImg.css('width', width);
                                    height && newImg.css('height', height);
                                    newImg.attr('alt', text);
                                    $(self).trigger('image-inserted.text-editor');

                                $(this).dialog('close');
                                self.lib.restoreSelection(self.restoreSelectionMarkerId);
                            }
                        },
                        remove : 
                        {
                            text : 'Remove',
                            class: 'btn-warning btn',
                            click : function()
                            {
                                self.lib.restoreSelection(self.restoreSelectionMarkerId);
                                self.currentSelectedImage.remove();
                                self.currentSelectedImage = false;
                                $(self).trigger('image-removed.text-editor');
                                $(this).dialog('close');
                            }
                        },
                        cancel : 
                        {
                            text : 'Cancel',
                            class: 'btn',
                            click : function() { $(this).dialog("close"); }
                        }
                    };
                    this.currentSelectedImage = false;
                    this.getDialog = function()
                    {
                        var dialog = this.dialog,
                            img = this.lib.selectionHas('img'),
                            imgText = img ? img.attr('alt') : '',
                            imgWidth = img ? img.attr('width') : '',
                            imgHeight = img ? img.attr('height') : '',
                            initialUrl = img ? img.attr('src') : "http://",
                            align = img ? img.attr('align') : false;
                        
                        dialog.prop('caller', this);
                        
                        if( !img )
                            this.dialog.dialog('option', 'buttons', [this.dialogButtons.insert, this.dialogButtons.cancel]);
                        else
                        {
                            this.dialog.dialog('option', 'buttons', this.dialogButtons);
                            this.currentSelectedImage = img;
                        }
                        this.dialog.find('[data-option="image-value"]').val(initialUrl);
                        this.dialog.find('[data-option="image-text"]').val(imgText);
                        this.dialog.find('[data-option="image-width"]').val(imgWidth);
                        this.dialog.find('[data-option="image-height"]').val(imgHeight);
                        align && this.dialog.find('[data-toggle="buttons-radio"] [data-value="'+align+'"]').addClass('active');
                        return dialog;
                    };
                },
                // TODO decorator pattern
                linkCommand : function(thisPlugin, calledFor) // passed this object to get other plugins
                {
                    var dialog = this.dialog.attr('title', 'Add a link')
                        .append($('<p />')
                            .append( $('<label />').attr('for', 'editor-link-text').text('Link text:'))
                            .append( $('<input />').attr('id', 'editor-link-text').addClass('input-xlarge') ))
                        .append($('<p />')
                            .append( $('<label />').attr('for', 'editor-link-value').text('Link href:'))
                            .append( $('<input />').attr('id', 'editor-link-value').addClass('input-xlarge') ));
                    var self = this;
                    
                    $(thisPlugin).on('plugins-remove', function()
                    { 
                        dialog.dialog('remove').remove();
                    });
                    
                    this.dialogButtons = 
                    {
                        cancel : 
                        {
                            text: 'Cancel',
                            class: 'btn',
                            click: function()
							{ 
								$(calledFor).data('linkCommandActive', false);
								$(this).dialog("close"); 
								$(calledFor).focus(); 
							}
                        },
                        remove : 
                        {
                            text : 'Remove',
                            class: 'btn btn-warning',
                            click : function()
                            {
                                self.lib.restoreSelection(self.restoreSelectionMarkerId);
                                var ap = $($(self.lib.selectionParent()).eq(0)),
                                    a = ap.is('a') ? ap : $(this.lib.selectionHas('a')).eq(0);
                                a.replaceWith(a.text());
                                document.execCommand("unlink", false, null);
                                $(self).trigger('link-removed.text-editor');
                                $(calledFor).data('linkCommandActive', false);
								$(this).dialog('close');
								$(calledFor).focus();
                            }
                        },
                        insert : 
                        {
                            text : 'Insert',
                            class: 'btn-primary btn',
                            click : function()
                            {
                                var url = $(this).find('#editor-link-value').val();
                                var text = $(this).find('#editor-link-text').val();
                                if( url===null )
                                {
                                    $(this).dialog('close');
                                    return false;
                                };
                                self.lib.restoreSelection(self.restoreSelectionMarkerId);
                                if( url==="" )
                                {
                                    document.execCommand("unlink", false, null);
                                    $(self).trigger('link-removed.text-editor');
                                }
                                else 
                                {
                                    if( window.getSelection )
                                    {
                                        var rng= window.getSelection().getRangeAt(0);
                                        rng.deleteContents()
                                        rng.insertNode( $('<a href="'+url+'" />').text(text).get(0) );
                                    }
                                    //document.execCommand("createLink", false, url);
                                    $(self).trigger('link-inserted.text-editor');   
                                }
                                $(calledFor).data('linkCommandActive', false);
                                $(this).dialog('close');
								$(calledFor).focus(); 
                            }
                        }
                        
                    };
                    this.getDialog = function()
                    {
                        this.dialog.prop('caller', this);
                        
                        $(calledFor).data('linkCommandActive', true);
                        
                        var ap = $($(self.lib.selectionParent()).eq(0)),
                            a = ap.is('a') ? ap : $(this.lib.selectionHas('a')).eq(0),
                            selText = this.selectedText,
                            aText = $.trim(selText) != '' ? selText : a.text(),
                            urlRe = new RegExp();

                        urlRe.compile("^[A-Za-z]+://[A-Za-z0-9-_]+\\.[A-Za-z0-9-_%&\?\/.=]+$");
                        var isA = a.is('a'),
                            isUrl = urlRe.test(aText),
                            initialUrl = isA ? a.attr('href') : ( isUrl ? aText : "http://" );
                        if( !isA )
                            this.dialog.dialog('option', 'buttons', [this.dialogButtons.insert, this.dialogButtons.cancel]);
                        else
                            this.dialog.dialog('option', 'buttons', this.dialogButtons);
                        this.dialog.find('#editor-link-value').val(initialUrl);
                        this.dialog.find('#editor-link-text').val(!isUrl ? aText : '');
                        return this.dialog;
                    };
                    this.queryState = function() 
                    {
                        return this.lib.selectionHas('a') || $($(self.lib.selectionParent()).eq(0)).is('a');
                    };
                },
                
                htmlCodeCommand: function(thisPlugin)
                {
                    var dialog = this.dialog.dialog( 'option', 'title', 'HTML code')
                                    .append($('<textarea class="editor-code" />')),
                        self = this;
                    
                    $(thisPlugin).on('plugins-remove', function()
                    { 
                        dialog.dialog('remove').remove();
                    });
                    
                    this.queryState = function(){ return false; };
                    this.getDialog = function()
                    {
                        var dialog = this.dialog,
                            parent = $(this.lib.selectionParent()),
                            html;
                        
                        dialog.prop('caller', this);
                        if( parent.attr('contenteditable') )
                            self.editTarget = parent;
                        else
                            self.editTarget = parent.parents('[contenteditable]:eq(0)')

                        parent = self.editTarget.clone();
                        parent.find('[sel-id]').remove();
                        dialog.find('textarea').val(parent.html());
                        
                        this.dialog.dialog('option', 'buttons', this.dialogButtons);
                        return dialog;
                    };
                    
                    this.dialogButtons = 
                    {
                        cancel: { text: 'Cancel', class: 'btn', click: function(){ $(this).dialog('close'); } },
                        ok: 
                        { 
                            text: 'Ok',
                            class: 'btn btn-primary',
                            click: function()
                            {
                                self.lib.restoreSelection(self.restoreSelectionMarkerId);
                                parent = self.editTarget;
                                parent.html($(this).find('textarea.editor-code').val());
                                $(this).dialog('close');
                            }
                        }
                    }
                    this.id = 'code';
                },
                /*!
                 * factory class for commands
                 */
                commandFactory : function(command, elem) 
                {   
                    elem.unselectable = "on"; // IE, prevent focus
                    $(elem).on( "mousedown", function(evt) 
                    { 
                        // we cancel the mousedown default to prevent the button from getting focus
                        // (doesn't work in IE)
                        if (evt.preventDefault) evt.preventDefault();
                    });
                    $(elem).on( "click", function(evt) 
                    {
                        var selected = 'getSelection' in window ?
                            window.getSelection().getRangeAt(0).toString() : '';
                        command.selectedText = selected;
                        command.execute();
                        $(this).trigger('command-executed.text-editor');
                    });
                    command.addElement(elem.get(0));
                    return command;
                }
            },
            // TODO dirty, see https://developer.mozilla.org/en-US/docs/DOM/MutationObserver 
            pasteCleanTypes: function()
            {
                this._create = function(elements)
                {
                    $(elements).on('paste.texteditor textInput.texteditor', function()
                    {
                        var self = this;
                        setTimeout(function(){ $('[style]', self).each(function()
                        {
                            $(this).attr('style').indexOf('font-family') !== -1 && $(this).css
                            ({
                                fontFamily: function(index, value){ return ''; }
                            });  
                        });}, 100);
                    });
                };
            },
            toolbar : function()
            {
                this.element = $('<div />').addClass('edit-toolbar').addClass('btn-toolbar');
                this.items = [];
                this._create = function(elements)
                {
                    var cmds = [];
                    for( var i in this.plugins.controls ) 
                        try
                        {
                            var cmd = this.plugins.controls[i].call(this, elements);
                            this.plugins.toolbar.items.push(cmd);
                            this.plugins.toolbar.element.append(cmd.getElements());
                            cmds.push(cmd);
                        }
                        catch(e){ console.exception(e); }
                    var self = this;
                    $(elements).on('keyup.texteditor mouseup.texteditor', function()
                    {
                        try
                        {
                            for( var i in cmds ) 
                                cmds[i].toggleState(self.plugins.toolbar);
                        }
                        catch(e){ /*console.exception(e);*/ }
                    });
                    $(elements).trigger('toolbar-created');
                    
                    var justifyGrp = []
                    for( var i=0; i<cmds.length; i++ )
                        if( $.inArray(cmds[i].id, ['JustifyCenter', 'JustifyLeft', 'JustifyRight']) != -1 )
                            justifyGrp.push(cmds[i]);
                    
                    $(justifyGrp).each(function(i, curCmd)
                    {
                        $(curCmd._elements).on('click', function()
                        {
                            for( var j=0; j<justifyGrp.length; j++ ) justifyGrp[j].toggleState();
                            curCmd.toggleState();
                        });
                    });
                    
                };
            },
            controlElements: {},
            controls : 
            {
                bold : function()
                {
                    var element = this.plugins.controlElements.bold || $('<a class="bold" />').text('b'),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.command( "bold" ), element );
                    return command;
                },
                italic : function() 
                {
                    var element = this.plugins.controlElements.italic || $('<a class="italic" />').text('i'),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.command( "italic" ), element );
                    return command;
                },
                underline : function()
                {
                    var element = this.plugins.controlElements.underline || $('<a class="underline" />').text('u'),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.command( "underline" ), element );
                    return command;
                },
                strikeThrough : function()
                {
                    var element = this.plugins.controlElements.strike || $('<a class="strike" />').text('s'),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.command( "strikeThrough" ), element );
                    return command;
                },
                justifyLeft : function()
                {
                    var element = this.plugins.controlElements.justLeft || $('<a class="align left" />').html(''),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.command( "JustifyLeft" ), element);
                    return command;
                },
                justifyCenter : function()
                {
                    var element = this.plugins.controlElements.justCenter || $('<a class="align center" />').html(''),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.command( "JustifyCenter" ), element );
                    return command;
                },
                justifyRight : function()
                {
                    var element = this.plugins.controlElements.justRight || $('<a class="align right" />').html(''),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.command( "JustifyRight" ), element );
                    return command;
                },
                link : function(calledForElements)
                {
                    var element = this.plugins.controlElements.link || $('<a class="link" />').html(''),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.linkCommand(this, calledForElements), element );
                    return command;
                },
                image : function(calledForElements)
                {
                    var element = this.plugins.controlElements.image || $('<a class="image" />').html('');
                    var command = new this.plugins.lib.commandFactory( new this.plugins.lib.imageCommand(this, calledForElements), element );
                    this.plugins.floatingToolbar && this.plugins.floatingToolbar.blockElements.push('img');
                    return command;
                },
                html : function(calledForElements)
                {
                    var element = this.plugins.controlElements.html || $('<a class="code" />').html('&lt;/&gt');
                    var command = new this.plugins.lib.commandFactory( new this.plugins.lib.htmlCodeCommand(this, calledForElements), element );
                    return command;
                }
            },
            elements:
            {
                /**
                 * placeholder and focus functionality
                 * @param elements
                 */
                _create: function(elements)
                {
                    var placeholder = $('<span class="'+this.options.placeholderClass+'" />');
                    $(elements).each(function()
                    { 
                        var $self = $(this),
                            placeholderText = $(this).attr('placeholder');
                        if(!placeholderText) return false;
                        $(this).text() === '' && $(this).prepend(placeholder.html(placeholderText));
                    });
                    
                    $(elements)
                    .on('focusin.texteditor', function()
                    {
                        $(this).addClass('focus');
                    })
                    .filter('[placeholder]')
                    .on('focusin.texteditor', function()
                    {
                        var $self = $(this),
                            hasContent = $self.data('has-content');
                        !hasContent && placeholder.remove(); 
                    });
                    $(elements)
                    .on('focusout.texteditor', function()
                    {
                        $(this).removeClass('focus');
                    })
                    .filter('[placeholder]')
                    .on('focusout.texteditor', function()
                    {
                        var $self = $(this),
                            placeholderText = $self.attr('placeholder');
                        
                        if( $self.text() === '' ) 
                            $self.prepend(placeholder.html(placeholderText)).data('has-content', false); 
                        else 
                            $self.data('has-content', true);
                    })
                    .on('placeholder.texteditor', function(){
                        var $self = $(this),
                            placeholderText = $self.attr('placeholder');
                        
                        if( $self.text() === '' ) 
                            $self.prepend(placeholder.html(placeholderText)).data('has-content', false); 
                        else 
                            $self.data('has-content', true);
                    });
                }
            },
            draggableToolbar:
            {
                isDragged: false,
                _create: function(elements)
                {
                    if(!this.plugins.toolbar) return false;
                    var toolbar = this.plugins.toolbar.element,
                        self = this.plugins.draggableToolbar,
                        isDragged;
                    
                    toolbar.draggable
                    ({ 
                        cancel: 'a', 
                        stop: function()
                        { 
                            isDragged = true;
                        }
                    });
                    toolbar.on('dblclick', function()
                    { 
                        isDragged = false;
                        $(elements).data('toolbar-dragged', false);
                        $(elements).trigger('focusin');
                    });
                    $(elements).on('focusin.texteditor keydown.texteditor click.texteditor', function(event)
                    {
                        isDragged && toolbar.show() && $(this).data('toolbar-dragged', true);
                    });
                }
            },
            floatingToolbar:
            {
                blockElements: [],
                _create: function(elements)
                {
                    if(!this.plugins.toolbar) return false;
                    var toolbar = this.plugins.toolbar.element,
                        self = this;
                    
                    toolbar.css({ position : 'absolute', top : 0, left : 0 }).hide().appendTo('body');
                    
                    var findBlockParent = function()
                    {
                        var blockElem = self.plugins.lib.selectionChildren(),
                            isBlock = false,
                            style;
                        if( blockElem.length != 1 )
                            blockElem = self.plugins.lib.selectionParent().get(0);
                        else
                            blockElem = blockElem.get(0);
                        
                        while(!isBlock)
                        {
                            if( blockElem.nodeType != 1 )
                            {
                                blockElem = $(blockElem).parent().get(0);
                                continue;
                            }
                            if( elements.index(blockElem) !== -1 
                                || $.inArray( $(blockElem).prop('tagName').toLowerCase(), self.plugins.floatingToolbar.blockElements) !== -1 )
                            { 
                                isBlock = blockElem; 
                                break; 
                            }
                            style = window.getComputedStyle(blockElem);
                            style.display == 'block' && (isBlock = blockElem);
                            blockElem = $(blockElem).parent().get(0);
                        }
                        return isBlock;
                    },
                    moveToolbar = function(event)
                    {
                        // escape tabs and shifts and so on..
                        if( event.type == 'keydown' && $.inArray(event.keyCode, [224, 17, 18, 16, 9]) !== -1) return;
                        
                        toolbar.removeClass(self.options.toolbar.classes.topFixed);
                        var para = findBlockParent();
                        switch(self.options.floatingToolbar)
                        {
                            case 'top':
                                var ofst = $(para).eq(0).offset(),
                                    left = ofst.left,
                                    top = ofst.top - toolbar.outerHeight();
                                if($('html').scrollTop() > top) 
                                {
                                    toolbar
                                        .removeAttr('style')
                                        .css({left: left})
                                        .addClass(self.options.toolbar.classes.topFixed)
                                        .fadeIn('fast');
                                    return;
                                }
                            break;
                            case 'left':
                            default: 
                                var ofst = $(para).eq(0).offset(),
                                    left = ofst.left + $(para).eq(0).width(),
                                    top = ofst.top;
                            break;
                        }
                        toolbar.css({top : top, left : left, position: 'absolute'}).fadeIn('fast');
                    };
                    
                    var hideToolbar = function()
                    {
                        toolbar.fadeOut('fast'); // TODO css transition
                    };
                    // timer here cause webkit is fail
                    $(elements).on('focusin.texteditor keydown.texteditor click.texteditor', function(event)
                    {
                        if( !$(this).data('toolbar-dragged') )
                        {
                            var self = this;
                            setTimeout(function(){ moveToolbar.call(self, event); }, 1);
                        }
                    });
                    $(elements).on('blur.texteditor focusout.texteditor', hideToolbar);
                }
            }
        },
        options:
        {
            placeholderClass: 'placeholder',
            toolbar:{ class: null, classes:{ topFixed: 'fixed-top' }},
            imageDefaultHeight: 100,
            imageDefaultWidth: 100,
            imageDialogUI: 
                '<form class="form-horizontal"><fieldset>'+
                '<div class="control-group">'+
                    '<label class="control-label" for="editor-image-text">Description:</label>'+
                    '<div class="controls">'+
                        '<input id="editor-image-text" data-option="image-text" class="input-large" />'+
                    '</div>'+
                '</div>'+
                '<div class="control-group hide">'+
                    '<label class="control-label" for="editor-image-value">URL:</label>'+
                    '<div class="controls">'+
                        '<input id="editor-image-value" data-option="image-value" class="input-large" />'+
                    '</div>'+
                '</div>'+
                '<div class="control-group">'+
                    '<label class="control-label" for="editor-image-value">Align:</label>'+
                    '<div class="controls"><div class="btn-group" data-toggle="buttons-radio">'+
                        '<button class="btn" data-value="left"><i class="icon-align-left" /></button>'+
                        '<button class="btn" data-value="middle"><i class="icon-align-center" /></button>'+
                        '<button class="btn" data-value="right"><i class="icon-align-right" /></button>'+
                    '</div></div>'+
                '</div>'+
                '<div class="control-group hide">'+
                    '<label class="control-label" for="editor-image-value">Size:</label>'+
                    '<div class="controls">'+
                        '<input type="text" class="input-mini" placeholder="width" data-option="image-width" /> x '+
                        '<input type="text" placeholder="height" class="input-mini" data-option="image-height" />'+
                    '</div>'+
                '</div>'+
                '</fieldset></form>'
        },
        plugin : function()
        {
        },
        _create : function()
        {
            $(this.element).attr('contentEditable', true);
        },
        _init: function() 
        { 
        },
        _setOption: function( key, value ) 
        {
            $.Widget.prototype._setOption.apply( this, arguments );
        },
        destroy: function() 
        {
        },
        pluginsDestroy: function()
        {
            $(this).trigger('plugins-remove');
            /*this.plugins.lib.dialogRepo && $(this.plugins.lib.dialogRepo).each(function()
            {
                console.log(this);
            });*/
            try
            {
                this.plugins.toolbar.element  && this.plugins.toolbar.element.remove();
            }
            catch(e){}
            
        }
    }); 
});

