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
define('jqueryui/texteditor', ['jquery','jqueryui/widget', 'jqueryui/ext'], function ($) 
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
                    var markerId = arguments[0] ? arguments[0] : "sel-" + (+new Date()) + "-" + ("" + Math.random()).slice(2);
                    var range = window.getSelection().getRangeAt(0);
                    var marker = $('<span />').html('&#xfeff;').attr('sel-id', markerId ).hide();
                    if( range.collapsed ) 
                        range.insertNode(marker.get(0));
                    else // not collapsed for selecting nodes like <img />
                    {
                        var intermRange = range.cloneRange();
                        var firstMarker = marker.get(0);
                        intermRange.insertNode(firstMarker);
                        range.setStartAfter(firstMarker);
                        intermRange.collapse(false);
                        var secondMarker = marker.clone().get(0);
                        intermRange.insertNode(secondMarker);
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
                selectionHas : function(nodeName)
                {
                    if( window.getSelection )
                    {
                        var range = window.getSelection().getRangeAt(0),
                            contents = $(range.commonAncestorContainer).contents();
                        for( var i = range.startOffset; i < range.endOffset; i++ )
                            if( $(contents[i]).is(nodeName) ) 
                                return $(contents[i]);
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
                            container = range.startContainer; // TODO investigate this...
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
                    return $(container).parents(':eq(0)');
                },
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
                _create : function()
                {
                    var lib = this.plugins.lib;
                    lib.command.prototype.lib = lib;
                    lib.dialogAidedCommand.inherits(lib.command);
                    lib.imageCommand.inherits(lib.dialogAidedCommand);
                    lib.linkCommand.inherits(lib.dialogAidedCommand);
                },
                command : function( command ) 
                {
                    this.execute = function() 
                    {
                        console.log(this.lib.selectionContents())
                        document.execCommand(command, false, null);
                        $(this).trigger('command-'+command+'.text-editor');
                    };
                    this.toggleState = function()
                    {
                        if(this.queryState())
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
                    this.id = Math.random();
                },
                /*!
                 * basic command which adds a jquery ui dialog for popup on execute
                 */
                dialogAidedCommand : function()
                {
                    this.parentClass.apply(this); // need to instance the parent command
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
                                self.lib.restoreSelection(self.restoreSelectionMarkerId);
                            }
                        });
                    
                    this.getDialog = function()
                    {
                        return this.dialog;
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
                    this.queryState = function()
                    {
                        return this.lib.selectionHas('img');
                    };
                    this.dialogButtons = 
                    {
                        insert : 
                        {
                            text : 'Insert',
                            click : function()
                            {
                                var url = $(this).find('#editor-image-value').val();
                                var text = $(this).find('#editor-image-text').val();
                                if( url === null )
                                {
                                    $(this).dialog('close');
                                    return false;
                                };
                                self.lib.restoreSelection(self.restoreSelectionMarkerId, true);
                                if( url.replace(/^http:\/\//,'') !== "" )
                                {
                                    // need to remark selection because apparently inserting images removes ranges
                                    self.restoreSelectionMarkerId = self.lib.markSelection(self.restoreSelectionMarkerId); 
                                    console.log(document.execCommand("insertImage", false, url))
                                    self.lib.restoreSelection(self.restoreSelectionMarkerId);
                                    $(self).trigger('image-inserted.text-editor');
                                }
                                $(this).dialog('close');
                            }
                        },
                        remove : 
                        {
                            text : 'Remove',
                            click : function()
                            {
                                self.currentSelectedImage.remove();
                                $(self).trigger('image-removed.text-editor');
                                $(this).dialog('close');
                            }
                        },
                        cancel : 
                        {
                            text : 'Cancel',
                            click : function() { $(this).dialog("close"); }
                        }
                    };
                    this.currentSelectedImage = false;
                    this.getDialog = function()
                    {
                        var dialog = this.dialog;
                        var img = this.lib.selectionHas('img');
                        var imgText = img ? img.attr('alt') : '';
                        var initialUrl = img ? img.attr('src') : "http://";
                        if( !img )
                            this.dialog.dialog('option', 'buttons', [this.dialogButtons.insert, this.dialogButtons.cancel]);
                        else
                        {
                            this.dialog.dialog('option', 'buttons', this.dialogButtons);
                            this.currentSelectedImage = img;
                        }
                        this.dialog.find('#editor-image-value').val(initialUrl);
                        this.dialog.find('#editor-image-text').val(imgText);
                        return dialog;
                    };
                },
                // TODO decorator pattern
                linkCommand : function(self) // passed this object to get other plugins
                {
                    var dialog = this.dialog.attr('title', 'Add a link')
                        .append($('<p />')
                            .append( $('<label />').attr('for', 'editor-link-text').text('Link text:'))
                            .append( $('<input />').attr('id', 'editor-link-text')))
                        .append($('<p />')
                            .append( $('<label />').attr('for', 'editor-link-value').text('Link href:'))
                            .append( $('<input />').attr('id', 'editor-link-value')));
                    var self = this;
                    this.dialogButtons = 
                    {
                        insert : 
                        {
                            text : 'Insert',
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
                                    document.execCommand("createLink", false, url);
                                    $(self).trigger('link-inserted.text-editor');   
                                }
                                $(this).dialog('close');
                            }
                        },
                        remove : 
                        {
                            text : 'Remove',
                            click : function()
                            {
                                self.lib.restoreSelection(self.restoreSelectionMarkerId);
                                document.execCommand("unlink", false, null);
                                $(self).trigger('link-removed.text-editor');
                                $(this).dialog('close');
                            }
                        },
                        cancel : 
                        {
                            text : 'Cancel',
                            click : function(){ $(this).dialog("close"); }
                        }
                    };
                    this.getDialog = function()
                    {
                        var a = $( $(self.lib.selectionContents() ).eq(0));
                        var aText = $(a).text();
                        var urlRe = new RegExp();
                        urlRe.compile("^[A-Za-z]+://[A-Za-z0-9-_]+\\.[A-Za-z0-9-_%&\?\/.=]+$");
                        var isA = a.is('a');
                        var isUrl = urlRe.test(aText);
                        var initialUrl = isA ? a.attr('href') : ( isUrl ? aText : "http://" );
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
                        return $($(self.lib.selectionContents()).eq(0)).is('a');
                    };
                },
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
                        command.execute();
                        $(this).trigger('command-executed.text-editor');
                    });
                    command.addElement(elem.get(0));
                    return command;
                }
            },
            toolbar : function()
            {
                this.element = $('<div />').addClass('edit-toolbar').addClass('btn-toolbar');
                this._create = function(elements)
                {
                    var cmds = [];
                    for( var i in this.plugins.controls ) 
                        try
                        {
                            var cmd = this.plugins.controls[i].call(this, elements);
                            this.plugins.toolbar.element.append( cmd.getElements() );
                            cmds.push(cmd);
                        }
                        catch(e){ /*console.exception(e);*/ }
                    var self = this;
                    $(elements).on('keyup mouseup', function()
                    {
                        try
                        {
                            for( var i in cmds ) 
                                cmds[i].toggleState();
                        }
                        catch(e){ /*console.exception(e);*/ }
                    });
                };
            },
            controls : 
            {
                bold : function()
                {
                    var element = $('<a class="bold" />').text('b'),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.command( "bold" ), element );
                    return command;
                },
                italic : function() 
                {
                    var element = $('<a class="italic" />').text('i'),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.command( "italic" ), element );
                    return command;
                },
                underline : function()
                {
                    var element = $('<a class="underline" />').text('u'),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.command( "underline" ), element );
                    return command;
                },
                strikeThrough : function()
                {
                    var element = $('<a class="strike" />').text('s'),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.command( "strikeThrough" ), element );
                    return command;
                },
                justifyLeft : function()
                {
                    var element = $('<a class="align left" />').html(''),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.command( "JustifyLeft" ), element);
                    return command;
                },
                justifyCenter : function()
                {
                    var element = $('<a class="align center" />').html(''),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.command( "JustifyCenter" ), element );
                    return command;
                },
                justifyRight : function()
                {
                    var element = $('<a class="align right" />').html(''),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.command( "JustifyRight" ), element );
                    return command;
                },
                link : function()
                {
                    var element = $('<a class="link" />').html('&infin;'),
                        command = new this.plugins.lib.commandFactory( new this.plugins.lib.linkCommand(), element );
                    return command;
                },
                image : function()
                {
                    var element = $('<a class="image" />').html('&#x2740;');
                    var command = new this.plugins.lib.commandFactory( new this.plugins.lib.imageCommand(this), element );/*new lib.dialogAidedCommand(new lib.command)*/
                    this.plugins.floatingToolbar.blockElements.push('img');
                    return command;
                }
            },
            floatingToolbar :
            {
                blockElements: [],
                _create : function(elements)
                {
                    var toolbar = this.plugins.toolbar.element,
                        self = this;

                    toolbar.css({ position : 'absolute', top : 0, left : 0 }).hide().appendTo('body');
                    
                    var findBlockParent = function()
                    {
                        var blockElem = self.plugins.lib.selectionChildren(),
                            isBlock = false,
                            style;
                        if( blockElem.length != 1 )
                            blockElem = self.plugins.lib.selectionParent().get(0)
                        else
                            blockElem = blockElem.get(0);

                        while(!isBlock)
                        {
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
                    $(elements).on('focusin keydown click', function(event)
                    {
                        var self = this;
                        setTimeout(function(){ moveToolbar.call(self, event); }, 1); 
                    });
                    $(elements).on('blur focusout', hideToolbar);
                }
            }
        },
        options:
        {
            toolbar:{ class: null, classes:{ topFixed: 'fixed-top' }},
            imageDialogUI: 
                '<p><label for="editor-image-text">Image description:</label><input id="editor-image-text" data-option="image-text"></p>'+
                '<p><label for="editor-image-value">Image URL:</label><input id="editor-image-value" data-option="image-value"></p>'+
                '<p>'+
                    '<label for="editor-image-value">Image align:</label>'+
                    '<div class="btn-group" data-toggle="buttons-radio">'+
                        '<button class="btn btn-primary">Left</button>'+
                        '<button class="btn btn-primary">Middle</button>'+
                        '<button class="btn btn-primary">Right</button>'+
                    '</div>'+
                '</p>'
        },
        plugin : function()
        {
        //  console.log(this, arguments)            
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
            //$.Widget.prototype._setOption.apply( this, arguments );
        },
        _destroy: function() 
        { 
            
        }
    }); 
});

