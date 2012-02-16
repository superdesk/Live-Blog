// doT.js
// 2011, Laura Doktorova
// https://github.com/olado/doT
//
// doT is a custom blend of templating functions from jQote2.js
// (jQuery plugin) by aefxx (http://aefxx.com/jquery-plugins/jqote2/)
// and underscore.js (http://documentcloud.github.com/underscore/)
// plus extensions.
//
// Licensed under the MIT license.
//
(function() {
	var doT = { version : '0.1.6' };

	if (typeof module !== 'undefined' && module.exports) {
		module.exports = doT;
	} else {
		this.doT = doT;
	}

	doT.templateSettings = // make sure you don't conflict rules between eachother 
	{
        evaluate: /\{\%([\s\S]+?)\%\}/g,
        interpolate: /\{\{([\s\S]+?)\}\}/g,
        encode: /\{\{!([\s\S]+?)\}\}/g,
		use: /\{\{#([\s\S]+?)\}\}/g, //compile time evaluation
		define: /\{\{##\s*([\w\.$]+)\s*(\:|=)([\s\S]+?)#\}\}/g, //compile time defs
        ends: /(endfor|endif|enblock)/g,
        between: /(else)/g,
        conditionalStart: /\{\?([\s\S]+?)\}/g,
        conditionalEnd: /\{\?\}/g,
		varname: 'it',
		strip: true,
		append: true
	};

	function resolveDefs(c, block, def) {
		block = block || '';
        return ((typeof block === 'string') ? block : block.toString())
		.replace(c.define, function (match, code, assign, value) {
			if (code.indexOf('def.') === 0) {
				code = code.substring(4);
			}
			if (!(code in def)) {
				if (assign === ':') {
					def[code]= value;
				} else {
					eval("def[code]=" + value);
				}
			}
			return '';
		})
		.replace(c.use, function(match, code) {
            var v = eval("def."+code);
			return v ? resolveDefs(c, v, def) : v;
		});
	}

	doT.template = function(tmpl, c, def) {
		c = c || doT.templateSettings;
		var cstart = c.append ? "'+(" : "';out+=(", // optimal choice depends on platform/size of templates
		    cend   = c.append ? ")+'" : ");out+='";
        var str = (c.use || c.define) ? resolveDefs(c, tmpl, def || {}) : tmpl;
        
		str = ("with("
            + c.varname
            + "){var out='" +
			((c.strip) ? str.replace(/\s*<!\[CDATA\[\s*|\s*\]\]>\s*|[\r\n\t]|(\/\*[\s\S]*?\*\/)/g, ''): str)
			.replace(/\\/g, '\\\\')
			.replace(/'/g, "\\'")
			.replace(c.interpolate, function(match, code) 
			{
				return cstart + code.replace(/\\'/g, "'").replace(/\\\\/g,"\\").replace(/[\r\t\n]/g, ' ') + cend;
			})
			.replace(c.encode, function(match, code) 
			{
				return cstart + code.replace(/\\'/g, "'").replace(/\\\\/g, "\\").replace(/[\r\t\n]/g, ' ') + ").toString().replace(/&(?!\\w+;)/g, '&#38;').split('<').join('&#60;').split('>').join('&#62;').split('" + '"' + "').join('&#34;').split(" + '"' + "'" + '"' + ").join('&#39;').split('/').join('&#47;'" + cend;
			})
			.replace(c.conditionalEnd, function(match, expression) 
			{
				return "';}out+='";
			})
			.replace(c.conditionalStart, function(match, expression) 
			{
				var code = "if( typeof (" + expression + ") != 'undefined' && " + expression + "){ ";
				return "';" + code.replace(/\\'/g, "'").replace(/\\\\/g,"\\").replace(/[\r\t\n]/g, ' ') + "out+='";
			})
			.replace(c.evaluate, function(match, code) 
			{                
				var x = "';" + code
					.replace(c.between, '}$1')
                    .replace(c.ends, '}')
                    .replace(/\\'/g, "'")
                    .replace(/\\\\/g, "\\")
                    .replace(/[\r\t\n]/g, ' ') +
                    ( c.ends.test(code) ? "" : "{" ) + "out+='";
                    c.ends.test(code); // Chrome weird true vs. false fix
                    return x;
			})
			+ "';return out;}" )
			.replace(/\n/g, '\\n')
			.replace(/\t/g, '\\t')
			.replace(/\r/g, '\\r')
			.split("out+='';").join('')
			.split("var out='';out+=").join('var out=');

		try {
			return new Function(c.varname, str);
		} catch (e) {
			if (typeof console !== 'undefined') console.log("Could not create a template function: " + str);
			throw e;
		}
	};
}());

(function($)
{
    $.fn.extend
    ({
        tmpl : function(selector, data, defs)
        {
        	return this.each(function()
        	{
        		$(this).html( $.tmpl(selector, data), undefined, defs ); 
        	});
        },
        renderTmpl: function(data)
        {
        	return $( $.tmpl(this, data) );
        }
    });
    $.extend
    ({
        tmpl : function(tmpl, data, defs)
        {
            if (!$(tmpl).data('compiled-template')) 
            	$(tmpl).data('compiled-template', doT.template( $(tmpl).html(), undefined, defs ));
            
            fn = $(tmpl).data('compiled-template');
            if(typeof fn === 'function')
                return fn(data);
            else
                return;
        },
        tmplOption : function(key)
    	{
    		$.extend(doT.templateSettings, key);
    	}
    });
})(jQuery);
