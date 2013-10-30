/*!
 * actually redefining MultiSplit
 */
define([ 'jquery', 'ui/multiSplit', 'format/format-plugin' ],
function ($, MultiSplit, Format) 
{
	'use strict';
	
	var origInit = MultiSplit.prototype.init,
	    _activeButtonText = false,
	    origAddMarkup = Format.addMarkup;
	Format.addMarkup = function()
	{
	    if( Aloha.editables.length == 0 ) return;
	    if( !Aloha.activeEditable ) 
	    {
	        Aloha.activateEditable(Aloha.editables[0]);
	        Aloha.activeEditable.obj.focus();
	    }
	    origAddMarkup.apply(this, arguments);
	}
	
	MultiSplit.prototype.init = function()
	{
	    var ret = origInit.apply(this, arguments),
	        settingsToolbar = Aloha.settings.plugins.toolbar.element;

	    // make list item from each button
	    for( var btn in this.buttons)
	    {
	        var newEl = $('<li />').append($(this.buttons[btn].element).clone(true, true)),
                modelEl = $("[data-format='"+btn+"']", settingsToolbar);
            modelEl.length 
                && $(modelEl.prop('attributes')).each(function(){ newEl.attr(this.name, this.value); })
                && $(this.buttons[btn].element).replaceWith(newEl);
	    };
	    
	    // make the container ul
	    var newContent = $('[data-format-content]', settingsToolbar).clone(true, true);
	    newContent.html(this.contentElement.contents());
	    this.contentElement.replaceWith(newContent);
	    
	    var modelToggle = $('[data-editor-ui-component="formatBlock"] [data-format-toggle]', settingsToolbar).clone(true, true);
	    this.toggleButton.html(modelToggle.html());
	    this.toggleButton.addClass(modelToggle.prop('class'));
	    
	    var currentFormat = $('[data-editor-ui-component="formatBlock"] [data-format-current]', settingsToolbar);
	    if( currentFormat.length )
	    {
	        _activeButtonText = currentFormat.text(); 
	        this._hasFormatInfo = true;
	        currentFormat.insertBefore($(this.toggleButton, this.element));
	        
	        var self = this;
	        $('[data-format-current]', $(this.element)).on('click.aloha-plugin-format', function()
	        { 
	            self.toggleButton.trigger('click'); 
	        });
	    }
	    
	    this.element.__isComplex = true;
	    
	    return ret;
	};
	
	MultiSplit.prototype.open = function() 
	{
        this.element.addClass('open');
        this._isOpen = true;
    };

    MultiSplit.prototype.close = function() 
    {
        this.element.removeClass('open');
        this._isOpen = false;
    };
    
    MultiSplit.prototype.toggle = function () 
    {
        this.element.toggleClass('open');
        this._isOpen = !this._isOpen;
    };
    
    MultiSplit.prototype.setActiveButton = function(name) 
    {
        if (!name) {
            name = null;
        }
        if (null !== this._activeButton) {
            this.buttons[this._activeButton]
                .element.removeClass('aloha-multisplit-active');
        }
        this._activeButton = name;
        if (null !== name) {
            this.buttons[name]
                .element.addClass('aloha-multisplit-active');
        }
        
        this._hasFormatInfo && this.buttons[this._activeButton] &&
            this.element.find('[data-format-current]').text($(this.buttons[this._activeButton].element).text());
        
        this._hasFormatInfo && !this.buttons[this._activeButton] &&
            this.element.find('[data-format-current]').text(_activeButtonText);
    }
	
	return MultiSplit
});
