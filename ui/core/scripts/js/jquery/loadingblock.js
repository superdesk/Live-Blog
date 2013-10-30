/*
    Use:
        - $('#element').loadingblock();        //to initialize loading block over an element

        - $('#element').loadingblock({         //function additional params        
            message   : 'This is message',     //add text message to loading block
            toggle    : true/false             //show/hide loading block once it is initialized
            destroy   : true/false             //destroy loading block when it is no more needed, false is default
            changePos : true/false             //change postitioning style of parent block , true is default         
          });  


    Calling .loadingblock() on the element that already contained one, will result with overriding the old one

    It is not possible to use loading block on elements that are not able to have child nodes (like <input>)
*/

(function ($) {
 
    $.fn.loadingblock = function(options) {
        
        var s = $.extend({
            toggle  : true,
            message : '',
            destroy : false,
            changePos : true
        }, options );


        var _block = this.find("> .async-loading");
        var _exist = _block.length > 0 ? true : false;
        var _msg = _block.find(".loading-msg")

        if (_exist) {
            s.destroy ? (_block.remove()) : (s.toggle ? (_msg.html(s.message), _block.show()) : (_block.hide(),_msg.html(s.message)));
        }
        else {
            var _pos = this.css('position');
            (_pos !== 'absolute' && _pos !== 'relative' && _pos !== 'fixed' && s.changePos) && this.css('position','relative');
            var template = '<div class="async-loading"><div class="loading-msg">' + s.message + '</div></div>';
            this.append(template);
        }

        return this;
    }; 
}( jQuery ));