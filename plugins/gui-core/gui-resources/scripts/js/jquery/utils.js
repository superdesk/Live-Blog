define('jquery/utils',['jquery'], function ($) {
$.isString = function( obj ) {
    return obj && typeof(obj) === 'string';
}
$.isObject = function( obj ) {
    return obj && typeof(obj) === 'object';
};
$.isDefined = function( obj ) {
    return obj && typeof(obj) !== 'undefined';
};
$.combineObj = function(keys, values) {
    var object = {};
    if( $.isArray( values ) ) {
		for (i = 0; i < keys.length; i++) {
			object[keys[i]] = values[i];
		}
	}
	if( $.isFunction(values)) {
		for (i = 0; i < keys.length; i++) {
			object[keys[i]] = values;
		}		
	}
    return object;
};
$.arrayValues = function(obj) {
	var arr = [];
	for(i in obj) {
		arr.push(obj[i]);
	}
	return arr;
};
$.mergeObj = function(first, second) {
	if(arguments.length > 2) {
		for(i=2;i<arguments.length;i++) {
			map = arguments[i];
			if( $.isString( map ) )
				map = map.split(",");
			if( $.isArray(map) ) {
				for(k=0;k<map.length;k++)
						first[map[k]]= second[map[k]];
			}
			else if( $.isObject( map ) ) {
				for(k in map) {
					if( $.isFunction( map[k] ) )
						first[k] = map[k](second,k);
					else
						first[k] = second[map[k]];
				}
			}
		}
	} else {
			for(i in 	first)
				first[i] = second[i];
	}
};
$.styledNodeHtml = function(node)
{
    node = $(node);
    if( node.attr('style') && node.attr('style') !== '')
    {
        var wrapper = $('<span/>');
        $('<span style="'+node.attr('style')+'" />').append(node.html()).appendTo(wrapper);
        return wrapper.html();
    }
    return node.html();
};
$.fn.preloadImages = function() {
	this.each(function(){
		$('<img/>')[0].src = this;
	});
};
$.extend($.browser, {language: window.navigator.userLanguage || window.navigator.language});
});